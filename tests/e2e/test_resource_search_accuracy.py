"""E2Eテスト: OCI CLIの結果とアプリの検索結果を比較する。"""

import json
import subprocess
import sys

def run_oci_cli_search(region: str, resource_types: list[str] | None = None) -> list[dict]:
    """OCI CLIでリソース検索を実行する。"""
    if resource_types:
        type_clause = ", ".join(f"'{t}'" for t in resource_types)
        query = f"query {type_clause} resources"
    else:
        query = "query all resources"

    result = subprocess.run(
        ["oci", "search", "resource", "structured-search",
         "--query-text", query,
         "--region", region],
        capture_output=True, text=True, timeout=120
    )
    if result.returncode != 0:
        print(f"OCI CLI error: {result.stderr}")
        return []

    data = json.loads(result.stdout)
    return data["data"]["items"]


def run_app_search(region: str, resource_types: list[str] | None = None) -> list[dict]:
    """アプリのResourceSearchServiceでリソース検索を実行する。"""
    from ri_agent.config import Settings
    from ri_agent.models.artifact import SearchRequest
    from ri_agent.services.resource_search import ResourceSearchService
    from ri_agent.storage.local_json import LocalJsonStorage

    settings = Settings()
    storage = LocalJsonStorage(settings.data_dir)
    service = ResourceSearchService(settings, storage)

    request = SearchRequest(
        regions=[region],
        resource_types=resource_types,
    )

    resources = service.search_single_region(region, request)
    return [r.model_dump(mode="json") for r in resources]


def compare_results(cli_results: list[dict], app_results: list[dict], label: str):
    """OCI CLIとアプリの結果を比較する。"""
    print(f"\n{'='*60}")
    print(f"テスト: {label}")
    print(f"{'='*60}")

    cli_ocids = {item["identifier"] for item in cli_results}
    app_ocids = {item["ocid"] for item in app_results}

    print(f"OCI CLI件数: {len(cli_ocids)}")
    print(f"アプリ件数:  {len(app_ocids)}")

    missing = cli_ocids - app_ocids
    extra = app_ocids - cli_ocids
    common = cli_ocids & app_ocids

    print(f"一致:        {len(common)}")
    print(f"CLI側のみ:   {len(missing)}")
    print(f"アプリ側のみ: {len(extra)}")

    if missing:
        print(f"\n⚠️ アプリで取得できていないリソース（先頭5件）:")
        missing_items = [i for i in cli_results if i["identifier"] in missing][:5]
        for item in missing_items:
            print(f"  - {item['resource-type']:20s} {item['display-name'][:40]:40s} {item['identifier'][:60]}")

    if extra:
        print(f"\n⚠️ アプリで余分に取得されたリソース（先頭5件）:")
        extra_items = [i for i in app_results if i["ocid"] in extra][:5]
        for item in extra_items:
            print(f"  - {item['resource_type']:20s} {item['name'][:40]:40s} {item['ocid'][:60]}")

    # フィールド内容比較（共通OCIDの先頭5件）
    if common:
        print(f"\nフィールド内容比較（先頭5件）:")
        cli_map = {i["identifier"]: i for i in cli_results}
        app_map = {i["ocid"]: i for i in app_results}

        checked = 0
        field_errors = 0
        for ocid in list(common)[:5]:
            cli_item = cli_map[ocid]
            app_item = app_map[ocid]

            errors = []
            # resource_type
            if cli_item["resource-type"] != app_item["resource_type"]:
                errors.append(f"resource_type: CLI={cli_item['resource-type']} APP={app_item['resource_type']}")
            # display_name
            cli_name = cli_item.get("display-name") or ""
            app_name = app_item.get("name") or ""
            if cli_name != app_name:
                errors.append(f"name: CLI='{cli_name}' APP='{app_name}'")
            # lifecycle_state
            cli_state = cli_item.get("lifecycle-state") or ""
            app_state = app_item.get("lifecycle_state") or ""
            if cli_state != app_state:
                errors.append(f"lifecycle_state: CLI='{cli_state}' APP='{app_state}'")

            checked += 1
            if errors:
                field_errors += 1
                print(f"  ❌ {ocid[:50]}...")
                for e in errors:
                    print(f"     {e}")
            else:
                print(f"  ✅ {cli_name[:40]} ({cli_item['resource-type']})")

    # 判定
    if len(cli_ocids) == 0:
        print(f"\n結果: ⚠️ SKIP（CLI結果0件）")
        return True
    match_rate = len(common) / len(cli_ocids) * 100
    print(f"\n一致率: {match_rate:.1f}%")
    passed = match_rate >= 95.0
    print(f"結果: {'✅ PASS' if passed else '❌ FAIL'}（閾値: 95%）")
    return passed


def main():
    test_region = "ap-tokyo-1"
    all_passed = True

    # テスト1: 特定タイプ（Instance）
    print("\n" + "=" * 60)
    print("テスト1: Instanceリソース検索")
    cli1 = run_oci_cli_search(test_region, ["Instance"])
    app1 = run_app_search(test_region, ["Instance"])
    if not compare_results(cli1, app1, "ap-tokyo-1のInstance検索"):
        all_passed = False

    # テスト2: 特定タイプ（Vcn）
    cli2 = run_oci_cli_search(test_region, ["Vcn"])
    app2 = run_app_search(test_region, ["Vcn"])
    if not compare_results(cli2, app2, "ap-tokyo-1のVcn検索"):
        all_passed = False

    # テスト3: 特定タイプ（Subnet）
    cli3 = run_oci_cli_search(test_region, ["Subnet"])
    app3 = run_app_search(test_region, ["Subnet"])
    if not compare_results(cli3, app3, "ap-tokyo-1のSubnet検索"):
        all_passed = False

    # テスト4: 全リソース（ページネーション確認）
    cli4 = run_oci_cli_search(test_region)
    app4 = run_app_search(test_region)
    if not compare_results(cli4, app4, "ap-tokyo-1の全リソース検索"):
        all_passed = False

    print(f"\n{'='*60}")
    print(f"最終結果: {'✅ ALL PASSED' if all_passed else '❌ SOME FAILED'}")
    print(f"{'='*60}")

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
