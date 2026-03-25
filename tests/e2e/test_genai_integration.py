"""E2Eテスト: OCI GenAI Serviceとの統合テスト。Pod内で実行する。"""

import json
import sys
import traceback

# テストシナリオ
SCENARIOS = [
    {
        "name": "シナリオ1: リソース検索（全件）",
        "input": "全リソースを一覧して",
        "expected_action": "resource_search",
    },
    {
        "name": "シナリオ2: リソース検索（リージョン+タイプ指定）",
        "input": "ap-tokyo-1のインスタンスを表示して",
        "expected_action": "resource_search",
    },
    {
        "name": "シナリオ3: リソース検索（タグフィルタ）",
        "input": "project=alphaタグのリソースを検索",
        "expected_action": "resource_search",
    },
    {
        "name": "シナリオ4: 依存関係マップ（OCID指定）",
        "input": "ocid1.instance.oc1.ap-tokyo-1.xxxの依存関係を表示",
        "expected_action": "dependency_map",
    },
    {
        "name": "シナリオ5: 依存関係マップ（深度指定）",
        "input": "ocid1.compartment.oc1..yyyの依存関係を深度2で表示",
        "expected_action": "dependency_map",
    },
    {
        "name": "シナリオ6: ヘルプ",
        "input": "使い方を教えて",
        "expected_action": "help",
    },
]


def run_tests():
    from ri_agent.config import Settings
    from ri_agent.oci_client.genai import GenAIClient

    settings = Settings()
    client = GenAIClient(settings)

    results = []
    passed = 0
    failed = 0

    for scenario in SCENARIOS:
        name = scenario["name"]
        user_input = scenario["input"]
        expected = scenario["expected_action"]

        print(f"\n{'='*60}")
        print(f"テスト: {name}")
        print(f"入力: {user_input}")
        print(f"期待アクション: {expected}")
        print("-" * 60)

        try:
            result = client.parse_user_intent(user_input)
            action = result.get("action", "unknown")
            print(f"結果: {json.dumps(result, ensure_ascii=False, indent=2)}")

            if action == expected:
                print(f"✅ PASS: アクション '{action}' が期待値と一致")
                passed += 1
                status = "PASS"
            else:
                print(f"❌ FAIL: アクション '{action}' != 期待値 '{expected}'")
                failed += 1
                status = "FAIL"

            # 追加バリデーション
            if action == "resource_search":
                params = result.get("params", {})
                print(f"   params: {json.dumps(params, ensure_ascii=False)}")
            elif action == "dependency_map":
                params = result.get("params", {})
                root_ocid = params.get("root_ocid", "")
                if not root_ocid:
                    print(f"   ⚠️ WARNING: root_ocidが空")
                else:
                    print(f"   root_ocid: {root_ocid}")
                    print(f"   depth: {params.get('depth', 3)}")
            elif action == "help":
                msg = result.get("message", "")
                print(f"   message: {msg[:100]}")

            results.append({"scenario": name, "status": status, "action": action})

        except Exception as e:
            print(f"❌ ERROR: {e}")
            traceback.print_exc()
            failed += 1
            results.append({"scenario": name, "status": "ERROR", "error": str(e)})

    print(f"\n{'='*60}")
    print(f"テスト結果サマリー: {passed} PASS / {failed} FAIL / {len(SCENARIOS)} TOTAL")
    print("=" * 60)

    for r in results:
        icon = "✅" if r["status"] == "PASS" else "❌"
        print(f"  {icon} {r['scenario']}: {r['status']}")

    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
