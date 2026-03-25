"""リソースおよびタグのデータモデル。"""

from datetime import datetime

from pydantic import BaseModel, Field


class Tags(BaseModel):
    """リソースに付与されたタグ情報。"""

    defined: dict[str, dict[str, str]] = Field(default_factory=dict)
    freeform: dict[str, str] = Field(default_factory=dict)


class Resource(BaseModel):
    """OCIテナント内の管理対象リソース。"""

    ocid: str
    name: str
    resource_type: str
    compartment_ocid: str
    compartment_name: str
    region: str
    lifecycle_state: str
    tags: Tags = Field(default_factory=Tags)
    time_created: datetime
