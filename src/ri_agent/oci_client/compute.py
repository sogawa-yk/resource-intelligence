"""Compute APIクライアントラッパー。"""

import oci

from ri_agent.oci_client.base import create_oci_client


class ComputeClientWrapper:
    """OCI Compute APIのラッパー。"""

    def __init__(self, config: dict, signer, region: str) -> None:
        self.client = create_oci_client(oci.core.ComputeClient, config, signer, region)

    def list_vnic_attachments(self, compartment_id: str, instance_id: str) -> list[dict]:
        """Instance→Subnetの接続情報を取得する。"""
        response = oci.pagination.list_call_get_all_results(
            self.client.list_vnic_attachments,
            compartment_id,
            instance_id=instance_id,
        )
        return [
            {"vnic_id": a.vnic_id, "subnet_id": a.subnet_id}
            for a in response.data
            if a.lifecycle_state == "ATTACHED" and a.subnet_id
        ]

    def list_volume_attachments(self, compartment_id: str, instance_id: str) -> list[dict]:
        """Instance→BlockVolumeの接続情報を取得する。"""
        response = oci.pagination.list_call_get_all_results(
            self.client.list_volume_attachments,
            compartment_id,
            instance_id=instance_id,
        )
        return [
            {"volume_id": a.volume_id}
            for a in response.data
            if a.lifecycle_state == "ATTACHED"
        ]

    def list_boot_volume_attachments(
        self, availability_domain: str, compartment_id: str, instance_id: str
    ) -> list[dict]:
        """Instance→BootVolumeの接続情報を取得する。"""
        response = oci.pagination.list_call_get_all_results(
            self.client.list_boot_volume_attachments,
            availability_domain,
            compartment_id,
            instance_id=instance_id,
        )
        return [
            {"boot_volume_id": a.boot_volume_id}
            for a in response.data
            if a.lifecycle_state == "ATTACHED"
        ]
