"""OCI クライアント初期化ファクトリ。"""

import oci

from ri_agent.config import Settings
from ri_agent.oci_client.base import create_retry_strategy, create_signer


def create_clients(config: Settings) -> dict:
    """必要なOCIクライアントを一括生成する。"""
    oci_config, signer = create_signer()
    retry = create_retry_strategy()

    if signer:
        identity = oci.identity.IdentityClient(oci_config, signer=signer, retry_strategy=retry)
    else:
        identity = oci.identity.IdentityClient(oci_config, retry_strategy=retry)

    return {
        "identity": identity,
        "config": oci_config,
        "signer": signer,
    }
