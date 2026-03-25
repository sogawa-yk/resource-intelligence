"""OCI SDK共通設定モジュール。"""

import os

import oci


class OciAuthenticationError(Exception):
    """OCI認証エラー（401/403）。リトライ対象外。"""


def create_signer() -> tuple[dict, oci.Signer | None]:
    """認証設定を作成する。

    ローカル開発時はConfigFileAuthentication、
    OKE上ではInstance Principal認証を使用する。

    Returns:
        (config, signer): Instance Principal時はconfig={}, signer=signer。
                          ConfigFile時はconfig=oci_config, signer=None。
    """
    use_instance_principal = os.environ.get("OCI_USE_INSTANCE_PRINCIPAL", "").lower() == "true"

    if use_instance_principal:
        signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
        return {}, signer
    else:
        config = oci.config.from_file()
        return config, None


def create_oci_client(client_class, config: dict, signer, region: str, **kwargs):
    """OCI SDKクライアントを統一的に生成する。"""
    retry = create_retry_strategy()
    if signer:
        client = client_class(config, signer=signer, retry_strategy=retry, **kwargs)
    else:
        client = client_class(config, retry_strategy=retry, **kwargs)
    client.base_client.set_region(region)
    return client


def create_retry_strategy():
    """リトライ戦略を作成する。429に対してexponential backoff最大3回。認証エラーはリトライ対象外。"""
    return oci.retry.DEFAULT_RETRY_STRATEGY


def handle_service_error(error: oci.exceptions.ServiceError) -> None:
    """ServiceErrorを検査し、認証エラーの場合はOciAuthenticationErrorを発生させる。"""
    if error.status in (401, 403):
        raise OciAuthenticationError(
            f"認証エラー（HTTP {error.status}）: {error.message}"
        ) from error
    raise error
