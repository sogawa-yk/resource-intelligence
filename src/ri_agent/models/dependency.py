"""依存関係マップのデータモデル。"""

from enum import Enum

from pydantic import BaseModel


class RelationType(str, Enum):
    """リソース間の関係タイプ。"""

    attached_to = "attached_to"
    uses = "uses"
    contains = "contains"
    routes_to = "routes_to"
    belongs_to = "belongs_to"
    governed_by = "governed_by"


class Node(BaseModel):
    """依存関係マップ内のノード。"""

    ocid: str
    name: str
    resource_type: str
    region: str
    compartment_name: str
    lifecycle_state: str
    is_external: bool = False


class Edge(BaseModel):
    """2つのリソース間の依存関係。"""

    source: str
    target: str
    relation_type: RelationType
    description: str


class DependencyMap(BaseModel):
    """リソース間の依存関係グラフ。"""

    root_ocid: str
    depth: int
    nodes: list[Node] = []
    edges: list[Edge] = []
