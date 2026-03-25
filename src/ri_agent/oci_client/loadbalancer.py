"""Load Balancer APIクライアントラッパー。"""

import oci

from ri_agent.oci_client.base import create_oci_client


class LoadBalancerClientWrapper:
    """OCI Load Balancer APIのラッパー。"""

    def __init__(self, config: dict, signer, region: str) -> None:
        self.client = create_oci_client(oci.load_balancer.LoadBalancerClient, config, signer, region)

    def get_load_balancer(self, lb_id: str) -> dict:
        """Load Balancerの詳細を取得する。BackendSet→Backendの情報を含む。"""
        response = self.client.get_load_balancer(lb_id)
        lb = response.data
        backend_sets = {}
        if lb.backend_sets:
            for name, bs in lb.backend_sets.items():
                backends = [
                    {"ip": b.ip_address, "port": b.port}
                    for b in (bs.backends or [])
                ]
                backend_sets[name] = {"backends": backends}

        return {
            "ocid": lb.id,
            "name": lb.display_name,
            "compartment_id": lb.compartment_id,
            "lifecycle_state": lb.lifecycle_state,
            "subnet_ids": lb.subnet_ids or [],
            "backend_sets": backend_sets,
        }
