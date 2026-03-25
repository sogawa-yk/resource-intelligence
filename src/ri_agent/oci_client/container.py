"""Container Engine (OKE) APIクライアントラッパー。"""

import oci

from ri_agent.oci_client.base import create_oci_client


class ContainerEngineClientWrapper:
    """OCI Container Engine APIのラッパー。"""

    def __init__(self, config: dict, signer, region: str) -> None:
        self.client = create_oci_client(oci.container_engine.ContainerEngineClient, config, signer, region)

    def get_cluster(self, cluster_id: str) -> dict:
        """OKE Clusterの詳細を取得する。VCN接続情報を含む。"""
        response = self.client.get_cluster(cluster_id)
        c = response.data
        return {
            "ocid": c.id,
            "name": c.name,
            "compartment_id": c.compartment_id,
            "lifecycle_state": c.lifecycle_state,
            "vcn_id": c.vcn_id,
        }

    def list_node_pools(self, compartment_id: str, cluster_id: str) -> list[dict]:
        """クラスタのNodePool一覧を取得する。Subnet接続情報を含む。"""
        response = oci.pagination.list_call_get_all_results(
            self.client.list_node_pools,
            compartment_id,
            cluster_id=cluster_id,
        )
        pools = []
        for np in response.data:
            subnet_ids = []
            if np.node_config_details and np.node_config_details.placement_configs:
                subnet_ids = [
                    pc.subnet_id
                    for pc in np.node_config_details.placement_configs
                    if pc.subnet_id
                ]
            pools.append({
                "ocid": np.id,
                "name": np.name,
                "compartment_id": np.compartment_id,
                "lifecycle_state": np.lifecycle_state,
                "subnet_ids": subnet_ids,
            })
        return pools
