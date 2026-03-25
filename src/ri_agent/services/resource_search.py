"""リソース検索サービス。テナント横断でOCIリソースを検索する。"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import oci
import structlog

from ri_agent.config import Settings
from ri_agent.models.artifact import Artifact, SearchRequest
from ri_agent.models.resource import Resource, Tags
from ri_agent.oci_client.base import create_oci_client, create_signer
from ri_agent.oci_client.search import ResourceSearchClient
from ri_agent.storage.local_json import LocalJsonStorage


class ResourceSearchService:
    """テナント横断リソース検索サービス。"""

    def __init__(self, settings: Settings, storage: LocalJsonStorage | None = None) -> None:
        self.settings = settings
        self.storage = storage or LocalJsonStorage(settings.data_dir)
        self.oci_config, self.signer = create_signer()
        self.log = structlog.get_logger(__name__)
        self._compartment_cache: dict[str, str] = {}

    def _resolve_compartment_name(self, compartment_ocid: str) -> str:
        """コンパートメントOCIDから名前を解決する（キャッシュ付き）。"""
        if not compartment_ocid:
            return ""
        if compartment_ocid in self._compartment_cache:
            return self._compartment_cache[compartment_ocid]
        try:
            identity = create_oci_client(
                oci.identity.IdentityClient, self.oci_config, self.signer, "us-ashburn-1"
            )
            resp = identity.get_compartment(compartment_ocid)
            name = resp.data.name
            self._compartment_cache[compartment_ocid] = name
            return name
        except Exception:
            self._compartment_cache[compartment_ocid] = ""
            return ""

    def search_single_region(self, region: str, request: SearchRequest) -> list[Resource]:
        """単一リージョンでリソース検索を実行する。"""
        query = ResourceSearchClient.build_query(
            resource_types=request.resource_types,
            compartment_ocid=request.compartment_ocid,
            lifecycle_states=request.lifecycle_states,
        )

        client = ResourceSearchClient(self.oci_config, self.signer, region)
        raw_results = client.search_resources(query)

        resources = []
        for item in raw_results:
            compartment_name = self._resolve_compartment_name(item["compartment_ocid"])
            resources.append(
                Resource(
                    ocid=item["ocid"],
                    name=item["name"],
                    resource_type=item["resource_type"],
                    compartment_ocid=item["compartment_ocid"],
                    compartment_name=compartment_name,
                    region=region,
                    lifecycle_state=item["lifecycle_state"],
                    tags=Tags(
                        defined=item.get("tags", {}).get("defined", {}),
                        freeform=item.get("tags", {}).get("freeform", {}),
                    ),
                    time_created=item["time_created"] or datetime.utcnow().isoformat(),
                )
            )

        return self._apply_post_filters(resources, request)

    def search_all_regions(self, request: SearchRequest) -> Artifact:
        """全サブスクライブ済みリージョンで並列検索を実行する。"""
        regions = request.regions or self._get_subscribed_regions()
        start_time = time.monotonic()
        self.log.info("search_all_regions_start", region_count=len(regions), filters=request.model_dump(exclude_none=True))

        all_resources: list[Resource] = []
        errors: list[dict] = []

        with ThreadPoolExecutor(max_workers=min(len(regions), 10)) as executor:
            future_to_region = {
                executor.submit(self.search_single_region, region, request): region
                for region in regions
            }

            for future in as_completed(future_to_region):
                region = future_to_region[future]
                try:
                    resources = future.result()
                    all_resources.extend(resources)
                except Exception as e:
                    errors.append({
                        "region": region,
                        "error_type": type(e).__name__,
                        "message": str(e),
                    })

        elapsed = time.monotonic() - start_time
        self.log.info(
            "search_all_regions_complete",
            total_resources=len(all_resources),
            region_count=len(regions),
            error_count=len(errors),
            elapsed_seconds=round(elapsed, 2),
        )

        artifact = Artifact(
            artifact_type="resource_list",
            data={
                "total_count": len(all_resources),
                "resources": [r.model_dump(mode="json") for r in all_resources],
                "errors": errors,
            },
        )

        self.storage.save_artifact("resource_search", artifact.model_dump(mode="json"))

        return artifact

    def _get_subscribed_regions(self) -> list[str]:
        """サブスクライブ済みリージョン一覧を取得する。"""
        identity = create_oci_client(
            oci.identity.IdentityClient, self.oci_config, self.signer, "us-ashburn-1"
        )
        response = identity.list_region_subscriptions(self.settings.oci_tenant_ocid)
        return [r.region_name for r in response.data]

    @staticmethod
    def _apply_post_filters(resources: list[Resource], request: SearchRequest) -> list[Resource]:
        """タグフィルタをポストフィルタとして適用する。"""
        if not request.tag_filters:
            return resources

        filtered = []
        for resource in resources:
            match = True
            for key, value in request.tag_filters.items():
                if resource.tags.freeform.get(key) != value:
                    found_in_defined = False
                    for ns_tags in resource.tags.defined.values():
                        if ns_tags.get(key) == value:
                            found_in_defined = True
                            break
                    if not found_in_defined:
                        match = False
                        break
            if match:
                filtered.append(resource)

        return filtered
