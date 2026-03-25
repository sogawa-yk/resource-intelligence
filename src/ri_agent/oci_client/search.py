"""Resource Search APIクライアントラッパー。"""

import time

import oci
import structlog

from ri_agent.oci_client.base import create_oci_client

log = structlog.get_logger(__name__)


class ResourceSearchClient:
    """OCI Resource Search APIのラッパー。"""

    def __init__(self, config: dict, signer, region: str) -> None:
        self.client = create_oci_client(
            oci.resource_search.ResourceSearchClient, config, signer, region
        )
        self.region = region

    def search_resources(self, query: str) -> list[dict]:
        """構造化クエリでリソースを検索し、ページネーションで全件取得する。"""
        all_resources = []
        search_details = oci.resource_search.models.StructuredSearchDetails(
            query=query,
            type="Structured",
        )

        start = time.monotonic()
        response = self.client.search_resources(search_details)
        all_resources.extend([self._to_dict(item) for item in response.data.items])

        page_count = 1
        while response.has_next_page:
            response = self.client.search_resources(search_details, page=response.next_page)
            all_resources.extend([self._to_dict(item) for item in response.data.items])
            page_count += 1

        elapsed = time.monotonic() - start
        log.info(
            "search_resources",
            api="ResourceSearch",
            region=self.region,
            result_count=len(all_resources),
            pages=page_count,
            latency_seconds=round(elapsed, 2),
        )

        return all_resources

    @staticmethod
    def _to_dict(item) -> dict:
        """ResourceSummaryをdict形式に変換する。"""
        return {
            "ocid": item.identifier,
            "name": item.display_name or "",
            "resource_type": item.resource_type,
            "compartment_ocid": item.compartment_id,
            "region": "",
            "lifecycle_state": item.lifecycle_state or "",
            "tags": {
                "defined": item.defined_tags or {},
                "freeform": item.freeform_tags or {},
            },
            "time_created": item.time_created.isoformat() if item.time_created else "",
        }

    @staticmethod
    def build_query(
        resource_types: list[str] | None = None,
        compartment_ocid: str | None = None,
        lifecycle_states: list[str] | None = None,
    ) -> str:
        """検索条件からOCI構造化クエリを組み立てる。"""
        if resource_types:
            type_clause = ", ".join(resource_types)
            query = f"query {type_clause} resources"
        else:
            query = "query all resources"

        conditions = []
        if compartment_ocid:
            conditions.append(f"compartmentId = '{compartment_ocid}'")
        if lifecycle_states:
            states = ", ".join(f"'{s}'" for s in lifecycle_states)
            conditions.append(f"lifecycleState IN ({states})")

        if conditions:
            query += " where " + " && ".join(conditions)

        return query
