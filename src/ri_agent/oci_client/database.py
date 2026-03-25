"""Database APIクライアントラッパー。"""

import oci

from ri_agent.oci_client.base import create_oci_client


class DatabaseClientWrapper:
    """OCI Database APIのラッパー。"""

    def __init__(self, config: dict, signer, region: str) -> None:
        self.client = create_oci_client(oci.database.DatabaseClient, config, signer, region)

    def get_db_system(self, db_system_id: str) -> dict:
        """DbSystemの詳細を取得する。Subnet接続情報を含む。"""
        response = self.client.get_db_system(db_system_id)
        db = response.data
        return {
            "ocid": db.id,
            "name": db.display_name,
            "compartment_id": db.compartment_id,
            "lifecycle_state": db.lifecycle_state,
            "subnet_id": db.subnet_id,
        }
