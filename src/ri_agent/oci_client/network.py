"""VCN/Networking APIクライアントラッパー。"""

import oci

from ri_agent.oci_client.base import create_oci_client


class VirtualNetworkClientWrapper:
    """OCI Virtual Network APIのラッパー。"""

    def __init__(self, config: dict, signer, region: str) -> None:
        self.client = create_oci_client(oci.core.VirtualNetworkClient, config, signer, region)

    def get_subnet(self, subnet_id: str) -> dict:
        """Subnetの詳細を取得する。VCN、SecurityList、RouteTableのIDを含む。"""
        response = self.client.get_subnet(subnet_id)
        s = response.data
        return {
            "ocid": s.id,
            "name": s.display_name,
            "vcn_id": s.vcn_id,
            "security_list_ids": s.security_list_ids or [],
            "route_table_id": s.route_table_id,
            "compartment_id": s.compartment_id,
            "lifecycle_state": s.lifecycle_state,
        }

    def get_vcn(self, vcn_id: str) -> dict:
        """VCNの詳細を取得する。"""
        response = self.client.get_vcn(vcn_id)
        v = response.data
        return {
            "ocid": v.id,
            "name": v.display_name,
            "compartment_id": v.compartment_id,
            "lifecycle_state": v.lifecycle_state,
        }

    def get_security_list(self, security_list_id: str) -> dict:
        """SecurityListの詳細を取得する。"""
        response = self.client.get_security_list(security_list_id)
        sl = response.data
        return {
            "ocid": sl.id,
            "name": sl.display_name,
            "compartment_id": sl.compartment_id,
            "lifecycle_state": sl.lifecycle_state,
        }

    def get_route_table(self, route_table_id: str) -> dict:
        """RouteTableの詳細を取得する。"""
        response = self.client.get_route_table(route_table_id)
        rt = response.data
        return {
            "ocid": rt.id,
            "name": rt.display_name,
            "compartment_id": rt.compartment_id,
            "lifecycle_state": rt.lifecycle_state,
        }
