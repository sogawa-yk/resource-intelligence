"""設定管理モジュール。"""

import uuid

import structlog
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """環境変数から読み込む設定。"""

    oci_tenant_ocid: str = ""
    oci_compartment_ocid: str = ""
    genai_model_id: str = "cohere.command-a-03-2025"
    genai_endpoint: str = "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"
    data_dir: str = "/data/history"
    log_level: str = "INFO"

    model_config = {"env_prefix": "", "case_sensitive": False}


import logging

_LOG_LEVEL_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


def _get_log_level(name: str) -> int:
    return _LOG_LEVEL_MAP.get(name.upper(), logging.INFO)


def configure_logging(settings: Settings) -> None:
    """structlogのJSON構造化ログを設定する。"""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(ensure_ascii=False),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            _get_log_level(settings.log_level)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def bind_request_id() -> str:
    """リクエストIDを生成してコンテキストにバインドする。"""
    request_id = str(uuid.uuid4())[:8]
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id=request_id)
    return request_id
