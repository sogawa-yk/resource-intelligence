"""Chainlitアプリケーションエントリポイント。OCI GenAI Serviceで自然言語を理解する。"""

import re

import chainlit as cl
import structlog

from ri_agent.config import Settings, bind_request_id, configure_logging
from ri_agent.models.artifact import DependencyMapRequest, SearchRequest
from ri_agent.oci_client.genai import GenAIClient
from ri_agent.services.dependency_map import DependencyMapService
from ri_agent.services.resource_search import ResourceSearchService
from ri_agent.storage.local_json import LocalJsonStorage

settings = Settings()
configure_logging(settings)
log = structlog.get_logger(__name__)
storage = LocalJsonStorage(settings.data_dir)

# 遅延初期化（Instance Principal認証はPod起動後に利用可能になる）
_search_service = None
_dep_map_service = None
_genai_client = None


def _get_search_service() -> ResourceSearchService:
    global _search_service
    if _search_service is None:
        _search_service = ResourceSearchService(settings, storage)
    return _search_service


def _get_dep_map_service() -> DependencyMapService:
    global _dep_map_service
    if _dep_map_service is None:
        _dep_map_service = DependencyMapService(settings, storage)
    return _dep_map_service


def _get_genai_client() -> GenAIClient:
    global _genai_client
    if _genai_client is None:
        _genai_client = GenAIClient(settings)
    return _genai_client


@cl.on_chat_start
async def on_chat_start():
    """ウェルカムメッセージを表示する。"""
    await cl.Message(
        content=(
            "**Resource Intelligence Agent** へようこそ！\n\n"
            "自然言語でOCIリソースについて質問できます。例:\n"
            "- 「全リソースを一覧して」\n"
            "- 「ap-tokyo-1のインスタンスを表示」\n"
            "- 「productionコンパートメントの稼働中リソース」\n"
            "- 「ocid1.instance...の依存関係を表示」\n\n"
            "何をお手伝いしますか？"
        )
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    """ユーザー入力をGenAIで解析して処理する。"""
    request_id = bind_request_id()
    text = message.content.strip()
    log.info("user_message", text=text[:100])

    # GenAIでインテント解析
    try:
        intent = _get_genai_client().parse_user_intent(text)
    except Exception as e:
        log.error("genai_error", error=str(e))
        await cl.Message(content=f"❌ AI解析エラー: {e}").send()
        return

    action = intent.get("action", "help")
    log.info("parsed_intent", action=action)

    if action == "resource_search":
        await _handle_resource_search(intent.get("params", {}))
    elif action == "dependency_map":
        await _handle_dependency_map(intent.get("params", {}))
    else:
        msg = intent.get("message", "申し訳ありません。リソース検索や依存関係マップの生成をお試しください。")
        await cl.Message(content=msg).send()


async def _handle_resource_search(params: dict):
    """リソース検索を実行し結果を表示する。"""
    request = SearchRequest(
        compartment_ocid=params.get("compartment_ocid"),
        resource_types=params.get("resource_types"),
        tag_filters=params.get("tag_filters"),
        regions=params.get("regions"),
        lifecycle_states=params.get("lifecycle_states"),
    )

    await cl.Message(content="🔍 リソースを検索中...").send()

    try:
        artifact = _get_search_service().search_all_regions(request)
    except Exception as e:
        await cl.Message(content=f"❌ 検索エラー: {e}").send()
        return

    data = artifact.data
    resources = data.get("resources", [])
    errors = data.get("errors", [])
    total = data.get("total_count", 0)

    if errors:
        success_regions = set(r.get("region", "") for r in resources)
        fail_regions = [e.get("region", "不明") for e in errors]
        warning = (
            f"⚠️ 一部のリージョンで検索に失敗しました\n\n"
            f"成功: {', '.join(success_regions)}（計{total}件）\n"
            f"失敗: {', '.join(fail_regions)}\n\n"
            f"部分結果を表示しています。\n\n"
        )
    else:
        warning = ""

    if not resources:
        await cl.Message(content=f"{warning}リソースが見つかりませんでした。").send()
        return

    table = "| 名前 | タイプ | リージョン | 状態 | コンパートメント |\n"
    table += "|------|--------|-----------|------|------------------|\n"
    for r in resources[:50]:
        table += f"| {r['name']} | {r['resource_type']} | {r['region']} | {r['lifecycle_state']} | {r['compartment_name']} |\n"

    suffix = ""
    if total > 50:
        suffix = f"\n\n（上位50件を表示。全{total}件）"

    await cl.Message(
        content=f"{warning}🔍 リソース検索結果（全{total}件）\n\n{table}{suffix}"
    ).send()


async def _handle_dependency_map(params: dict):
    """依存関係マップを生成し結果を表示する。"""
    root_ocid = params.get("root_ocid")
    if not root_ocid:
        await cl.Message(
            content=(
                "❓ OCIDを指定してください。\n\n"
                "使用例:\n"
                "- 「ocid1.instance.oc1.ap-tokyo-1.xxxの依存関係を表示」\n"
                "- 「ocid1.compartment.oc1..xxxの依存関係を深度2で表示」"
            )
        ).send()
        return

    depth = params.get("depth", 3)
    request = DependencyMapRequest(root_ocid=root_ocid, depth=depth)

    await cl.Message(content="🗺️ 依存関係マップを生成中...").send()

    region = _extract_region_from_ocid(root_ocid) or "ap-tokyo-1"

    try:
        artifact = _get_dep_map_service().generate_map(request, region)
    except Exception as e:
        await cl.Message(content=f"❌ マップ生成エラー: {e}").send()
        return

    data = artifact.data
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    errors = data.get("errors", [])

    if errors:
        error_msg = "\n".join(
            f"- {e.get('ocid', '不明')}: {e.get('message', '')}" for e in errors
        )
        warning = f"⚠️ 一部のリソースで情報取得に失敗しました\n{error_msg}\n\n"
    else:
        warning = ""

    tree = _build_tree_text(nodes, edges, root_ocid)

    await cl.Message(
        content=(
            f"{warning}🗺️ 依存関係マップ（起点: {root_ocid.split('.')[-1][:20]}、深度: {depth}）\n\n"
            f"ノード数: {len(nodes)}、エッジ数: {len(edges)}\n\n"
            f"{tree}"
        )
    ).send()


def _extract_region_from_ocid(ocid: str) -> str | None:
    """OCIDからリージョンを抽出する。"""
    parts = ocid.split(".")
    for part in parts:
        if re.match(r"^[a-z]+-[a-z]+-\d+$", part):
            return part
    return None


def _build_tree_text(nodes: list[dict], edges: list[dict], root_ocid: str) -> str:
    """ノードとエッジからツリー形式のテキストを生成する。"""
    node_map = {n["ocid"]: n for n in nodes}
    children: dict[str, list[dict]] = {}
    for edge in edges:
        children.setdefault(edge["source"], []).append(edge)

    lines: list[str] = []
    root = node_map.get(root_ocid)
    if root:
        lines.append(f"{root['name']} ({root['resource_type']})")
        _build_subtree(root_ocid, children, node_map, lines, "", set())

    return "\n".join(lines) if lines else "（ノードなし）"


def _build_subtree(
    ocid: str,
    children: dict[str, list[dict]],
    node_map: dict[str, dict],
    lines: list[str],
    prefix: str,
    visited: set[str],
) -> None:
    """再帰的にサブツリーを構築する。"""
    if ocid in visited:
        return
    visited.add(ocid)

    child_edges = children.get(ocid, [])
    for i, edge in enumerate(child_edges):
        is_last = i == len(child_edges) - 1
        connector = "└── " if is_last else "├── "
        child_prefix = "    " if is_last else "│   "

        target = node_map.get(edge["target"], {})
        target_name = target.get("name", edge["target"][:20])
        target_type = target.get("resource_type", "")
        ext = " [外部]" if target.get("is_external") else ""

        lines.append(f"{prefix}{connector}[{edge['relation_type']}] → {target_name} ({target_type}){ext}")
        _build_subtree(edge["target"], children, node_map, lines, prefix + child_prefix, visited)
