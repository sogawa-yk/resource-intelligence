"""依存関係マップサービス。BFSでリソース間の依存関係を探索する。"""

import time
from collections import deque
from datetime import datetime

import structlog

from ri_agent.config import Settings
from ri_agent.models.artifact import Artifact, DependencyMapRequest, SearchRequest
from ri_agent.models.dependency import DependencyMap, Edge, Node, RelationType
from ri_agent.oci_client.base import create_signer
from ri_agent.oci_client.compute import ComputeClientWrapper
from ri_agent.oci_client.container import ContainerEngineClientWrapper
from ri_agent.oci_client.database import DatabaseClientWrapper
from ri_agent.oci_client.loadbalancer import LoadBalancerClientWrapper
from ri_agent.oci_client.network import VirtualNetworkClientWrapper
from ri_agent.storage.local_json import LocalJsonStorage


class DependencyMapService:
    """リソース依存関係マップ生成サービス。"""

    def __init__(self, settings: Settings, storage: LocalJsonStorage | None = None) -> None:
        self.settings = settings
        self.storage = storage or LocalJsonStorage(settings.data_dir)
        self.oci_config, self.signer = create_signer()
        self.log = structlog.get_logger(__name__)

    def generate_map(self, request: DependencyMapRequest, region: str) -> Artifact:
        """起点OCIDからBFSで依存関係マップを生成する。"""
        depth = min(request.depth, 10)
        dep_map = DependencyMap(root_ocid=request.root_ocid, depth=depth)
        errors: list[dict] = []
        start_time = time.monotonic()
        self.log.info("generate_map_start", root_ocid=request.root_ocid, depth=depth, region=region)

        if self._is_compartment_ocid(request.root_ocid):
            dep_map = self._generate_compartment_map(request, region, dep_map)
        else:
            dep_map = self._bfs_explore(request.root_ocid, depth, region, dep_map, request.resource_types, errors)

        elapsed = time.monotonic() - start_time
        self.log.info(
            "generate_map_complete",
            node_count=len(dep_map.nodes),
            edge_count=len(dep_map.edges),
            error_count=len(errors),
            elapsed_seconds=round(elapsed, 2),
        )

        artifact = Artifact(
            artifact_type="dependency_map",
            data={
                "root_ocid": dep_map.root_ocid,
                "depth": dep_map.depth,
                "nodes": [n.model_dump(mode="json") for n in dep_map.nodes],
                "edges": [e.model_dump(mode="json") for e in dep_map.edges],
                "errors": errors,
            },
        )

        self.storage.save_artifact("dependency_map", artifact.model_dump(mode="json"))
        return artifact

    def _bfs_explore(
        self,
        root_ocid: str,
        max_depth: int,
        region: str,
        dep_map: DependencyMap,
        resource_types: list[str] | None = None,
        errors: list[dict] | None = None,
    ) -> DependencyMap:
        """BFSアルゴリズムで依存関係を探索する。"""
        if errors is None:
            errors = []
        visited: set[str] = set()
        queue: deque[tuple[str, str, str, str, int]] = deque()
        # (ocid, resource_type, compartment_id, name, current_depth)

        resource_type = self._detect_resource_type(root_ocid)
        resource_info = self._get_resource_info(root_ocid, region)
        root_name = resource_info.get("name", root_ocid.split(".")[-1][:20])
        root_compartment_id = resource_info.get("compartment_ocid", "")
        root_compartment_name = resource_info.get("compartment_name", "")
        root_lifecycle = resource_info.get("lifecycle_state", "")
        if resource_info.get("resource_type"):
            resource_type = resource_info["resource_type"]

        root_node = Node(
            ocid=root_ocid,
            name=root_name,
            resource_type=resource_type,
            region=region,
            compartment_name=root_compartment_name,
            lifecycle_state=root_lifecycle,
            is_external=False,
        )
        dep_map.nodes.append(root_node)
        visited.add(root_ocid)

        if max_depth == 0:
            return dep_map

        queue.append((root_ocid, resource_type, root_compartment_id, root_name, 0))

        while queue:
            ocid, res_type, compartment_id, name, current_depth = queue.popleft()
            if current_depth >= max_depth:
                continue

            try:
                edges = self._resolve_dependencies(ocid, res_type, compartment_id, region)
            except Exception as e:
                errors.append({
                    "ocid": ocid,
                    "resource_type": res_type,
                    "error_type": type(e).__name__,
                    "message": str(e),
                })
                continue

            for edge_info in edges:
                target_ocid = edge_info["target_ocid"]
                target_type = edge_info["target_type"]
                target_name = edge_info.get("target_name", "")
                relation = edge_info["relation_type"]
                description = edge_info["description"]
                is_external = edge_info.get("is_external", False)

                if resource_types and target_type not in resource_types:
                    continue

                dep_map.edges.append(Edge(
                    source=ocid,
                    target=target_ocid,
                    relation_type=relation,
                    description=description,
                ))

                if target_ocid not in visited:
                    visited.add(target_ocid)
                    target_node = Node(
                        ocid=target_ocid,
                        name=target_name or target_ocid.split(".")[-1][:20],
                        resource_type=target_type,
                        region=region,
                        compartment_name="",
                        lifecycle_state="",
                        is_external=is_external,
                    )
                    dep_map.nodes.append(target_node)

                    if not is_external:
                        target_compartment = edge_info.get("target_compartment_id", "")
                        queue.append((target_ocid, target_type, target_compartment, target_name, current_depth + 1))

        return dep_map

    def _resolve_dependencies(
        self, ocid: str, resource_type: str, compartment_id: str, region: str
    ) -> list[dict]:
        """リソースタイプに応じた依存関係を解決する。"""
        rt = resource_type.lower()
        if rt == "instance":
            return self._resolve_instance_deps(ocid, compartment_id, region)
        elif rt == "subnet":
            return self._resolve_subnet_deps(ocid, region)
        elif rt in ("loadbalancer", "load_balancer"):
            return self._resolve_lb_deps(ocid, region)
        elif rt in ("dbsystem", "db_system"):
            return self._resolve_db_deps(ocid, region)
        elif rt in ("cluster", "okecluster"):
            return self._resolve_oke_deps(ocid, compartment_id, region)
        return []

    def _resolve_instance_deps(self, instance_id: str, compartment_id: str, region: str) -> list[dict]:
        """Instanceの依存関係を解決する。"""
        edges = []
        compute = ComputeClientWrapper(self.oci_config, self.signer, region)

        network = VirtualNetworkClientWrapper(self.oci_config, self.signer, region)
        vnics = compute.list_vnic_attachments(compartment_id, instance_id)
        for vnic in vnics:
            if vnic.get("subnet_id"):
                subnet_name = ""
                try:
                    subnet = network.get_subnet(vnic["subnet_id"])
                    subnet_name = subnet.get("name", "")
                except Exception:
                    pass
                edges.append({
                    "target_ocid": vnic["subnet_id"],
                    "target_type": "Subnet",
                    "target_name": subnet_name,
                    "relation_type": RelationType.attached_to,
                    "description": "ComputeインスタンスがSubnetに接続",
                })

        volumes = compute.list_volume_attachments(compartment_id, instance_id)
        for vol in volumes:
            edges.append({
                "target_ocid": vol["volume_id"],
                "target_type": "BlockVolume",
                "target_name": "",
                "relation_type": RelationType.uses,
                "description": "ComputeインスタンスがBlockVolumeを使用",
            })

        try:
            boot_vols = compute.list_boot_volume_attachments("", compartment_id, instance_id)
            for bv in boot_vols:
                edges.append({
                    "target_ocid": bv["boot_volume_id"],
                    "target_type": "BootVolume",
                    "target_name": "",
                    "relation_type": RelationType.uses,
                    "description": "ComputeインスタンスがBootVolumeを使用",
                })
        except Exception:
            pass

        return edges

    def _resolve_subnet_deps(self, subnet_id: str, region: str) -> list[dict]:
        """Subnetの依存関係を解決する。"""
        edges = []
        network = VirtualNetworkClientWrapper(self.oci_config, self.signer, region)
        subnet = network.get_subnet(subnet_id)

        if subnet.get("vcn_id"):
            vcn_name = ""
            try:
                vcn = network.get_vcn(subnet["vcn_id"])
                vcn_name = vcn.get("name", "")
            except Exception:
                pass
            edges.append({
                "target_ocid": subnet["vcn_id"],
                "target_type": "Vcn",
                "target_name": vcn_name,
                "relation_type": RelationType.belongs_to,
                "description": "SubnetがVCNに所属",
            })

        for sl_id in subnet.get("security_list_ids", []):
            sl_name = ""
            try:
                sl = network.get_security_list(sl_id)
                sl_name = sl.get("name", "")
            except Exception:
                pass
            edges.append({
                "target_ocid": sl_id,
                "target_type": "SecurityList",
                "target_name": sl_name,
                "relation_type": RelationType.governed_by,
                "description": "SubnetにSecurityListが適用",
            })

        if subnet.get("route_table_id"):
            rt_name = ""
            try:
                rt = network.get_route_table(subnet["route_table_id"])
                rt_name = rt.get("name", "")
            except Exception:
                pass
            edges.append({
                "target_ocid": subnet["route_table_id"],
                "target_type": "RouteTable",
                "target_name": rt_name,
                "relation_type": RelationType.governed_by,
                "description": "SubnetにRouteTableが適用",
            })

        return edges

    def _resolve_lb_deps(self, lb_id: str, region: str) -> list[dict]:
        """LoadBalancerの依存関係を解決する。"""
        edges = []
        lb_client = LoadBalancerClientWrapper(self.oci_config, self.signer, region)
        lb = lb_client.get_load_balancer(lb_id)

        for subnet_id in lb.get("subnet_ids", []):
            edges.append({
                "target_ocid": subnet_id,
                "target_type": "Subnet",
                "target_name": "",
                "relation_type": RelationType.attached_to,
                "description": "LoadBalancerがSubnetに接続",
            })

        for bs_name, bs_data in lb.get("backend_sets", {}).items():
            edges.append({
                "target_ocid": f"{lb_id}/backendset/{bs_name}",
                "target_type": "BackendSet",
                "target_name": bs_name,
                "relation_type": RelationType.contains,
                "description": "LoadBalancerがBackendSetを包含",
            })

        return edges

    def _resolve_db_deps(self, db_system_id: str, region: str) -> list[dict]:
        """DbSystemの依存関係を解決する。"""
        edges = []
        db_client = DatabaseClientWrapper(self.oci_config, self.signer, region)
        db = db_client.get_db_system(db_system_id)

        if db.get("subnet_id"):
            edges.append({
                "target_ocid": db["subnet_id"],
                "target_type": "Subnet",
                "target_name": "",
                "relation_type": RelationType.attached_to,
                "description": "DbSystemがSubnetに接続",
            })

        return edges

    def _resolve_oke_deps(self, cluster_id: str, compartment_id: str, region: str) -> list[dict]:
        """OKE Clusterの依存関係を解決する。"""
        edges = []
        oke_client = ContainerEngineClientWrapper(self.oci_config, self.signer, region)

        cluster = oke_client.get_cluster(cluster_id)
        if cluster.get("vcn_id"):
            edges.append({
                "target_ocid": cluster["vcn_id"],
                "target_type": "Vcn",
                "target_name": "",
                "relation_type": RelationType.uses,
                "description": "OKE ClusterがVCNを使用",
            })

        if compartment_id:
            node_pools = oke_client.list_node_pools(compartment_id, cluster_id)
            for np in node_pools:
                for subnet_id in np.get("subnet_ids", []):
                    edges.append({
                        "target_ocid": subnet_id,
                        "target_type": "Subnet",
                        "target_name": "",
                        "relation_type": RelationType.attached_to,
                        "description": f"OKE NodePool '{np['name']}' がSubnetに接続",
                    })

        return edges

    def _generate_compartment_map(
        self, request: DependencyMapRequest, region: str, dep_map: DependencyMap
    ) -> DependencyMap:
        """コンパートメント起点のマップ生成。配下リソースを検索してから各リソースの依存関係を解析する。"""
        from ri_agent.services.resource_search import ResourceSearchService

        search_service = ResourceSearchService(self.settings)
        search_request = SearchRequest(
            compartment_ocid=request.root_ocid,
            resource_types=request.resource_types,
        )
        resources = search_service.search_single_region(region, search_request)

        visited: set[str] = {request.root_ocid}
        for resource in resources:
            if resource.ocid not in visited:
                visited.add(resource.ocid)
                node = Node(
                    ocid=resource.ocid,
                    name=resource.name,
                    resource_type=resource.resource_type,
                    region=resource.region,
                    compartment_name=resource.compartment_name,
                    lifecycle_state=resource.lifecycle_state,
                    is_external=False,
                )
                dep_map.nodes.append(node)

        for resource in resources:
            dep_map = self._bfs_explore(
                resource.ocid,
                min(request.depth, 10),
                region,
                dep_map,
                request.resource_types,
            )

        return dep_map

    def _get_resource_info(self, ocid: str, region: str) -> dict:
        """Resource Search APIでリソースの基本情報を取得する。"""
        try:
            from ri_agent.oci_client.search import ResourceSearchClient
            client = ResourceSearchClient(self.oci_config, self.signer, region)
            results = client.search_resources(f"query all resources where identifier = '{ocid}'")
            if results:
                item = results[0]
                compartment_name = ""
                try:
                    from ri_agent.oci_client.base import create_oci_client
                    import oci
                    identity = create_oci_client(
                        oci.identity.IdentityClient, self.oci_config, self.signer, "us-ashburn-1"
                    )
                    resp = identity.get_compartment(item["compartment_ocid"])
                    compartment_name = resp.data.name
                except Exception:
                    pass
                return {
                    "name": item["name"],
                    "resource_type": item["resource_type"],
                    "compartment_ocid": item["compartment_ocid"],
                    "compartment_name": compartment_name,
                    "lifecycle_state": item["lifecycle_state"],
                }
        except Exception:
            pass
        return {}

    @staticmethod
    def _detect_resource_type(ocid: str) -> str:
        """OCIDからリソースタイプを推定する。"""
        parts = ocid.split(".")
        if len(parts) >= 2:
            type_part = parts[1]
            type_map = {
                "instance": "Instance",
                "vcn": "Vcn",
                "subnet": "Subnet",
                "volume": "BlockVolume",
                "bootvolume": "BootVolume",
                "loadbalancer": "LoadBalancer",
                "dbsystem": "DbSystem",
                "cluster": "Cluster",
                "compartment": "Compartment",
                "securitylist": "SecurityList",
                "routetable": "RouteTable",
            }
            return type_map.get(type_part.lower(), type_part)
        return "Unknown"

    @staticmethod
    def _is_compartment_ocid(ocid: str) -> bool:
        """OCIDがコンパートメントかテナントかを判定する。"""
        parts = ocid.split(".")
        return len(parts) >= 2 and parts[1].lower() in ("compartment", "tenancy")
