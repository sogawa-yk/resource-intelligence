"""アーティファクトおよびリクエストのデータモデル。"""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class Artifact(BaseModel):
    """スキル実行結果の共通ラッパー。"""

    artifact_type: Literal["resource_list", "dependency_map"]
    version: str = "1.0"
    agent_id: str = "RI"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    data: dict[str, Any] = Field(default_factory=dict)


class SearchRequest(BaseModel):
    """resource-searchスキルの入力パラメータ。"""

    compartment_ocid: str | None = None
    resource_types: list[str] | None = None
    tag_filters: dict[str, str] | None = None
    regions: list[str] | None = None
    lifecycle_states: list[str] | None = None


class DependencyMapRequest(BaseModel):
    """dependency-mapスキルの入力パラメータ。"""

    root_ocid: str = Field(..., description="起点リソースまたはコンパートメントのOCID")
    depth: int = Field(
        default=3,
        ge=0,
        le=10,
        json_schema_extra={"errorMessage": {"minimum": "探索深度は0以上で指定してください", "maximum": "探索深度は10以下で指定してください"}},
    )
    resource_types: list[str] | None = None
