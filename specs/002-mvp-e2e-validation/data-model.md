# Data Model: MVP判定基準E2Eバリデーション

**Date**: 2026-03-25
**Branch**: `002-mvp-e2e-validation`

## テスト関連エンティティ

### テストケース

| フィールド | 型 | 説明 |
|-----------|-----|------|
| test_id | string | テストID（例: T01, T02） |
| mvp_criterion | string | 対応するMVP判定基準（①〜④） |
| category | string | テストカテゴリ（resource_search, dependency_map, multi_region, deployment） |
| input_text | string | Chainlit UIに入力するテキスト |
| expected_behavior | string | 期待される動作の説明 |
| validation_keywords | list[string] | 応答に含まれるべきキーワード |

### テスト結果

| フィールド | 型 | 説明 |
|-----------|-----|------|
| test_id | string | テストID |
| passed | boolean | 合否 |
| response_summary | string | 応答の要約（100文字以内） |
| response_time_s | float | 応答時間（秒） |
| screenshot_path | string | スクリーンショットのファイルパス |
| error_msg | string | エラーメッセージ（失敗時） |
| timestamp | datetime | テスト実行日時 |

### MVP判定基準

| 基準ID | 基準内容 | 対応テストケース |
|--------|----------|-----------------|
| ① | Chainlit UIからリソース検索を実行し、結果が表示される | T01〜T05 |
| ② | Chainlit UIから依存関係マップ生成を実行し、ノード・エッジが表示される | T06〜T08 |
| ③ | 全サブスクライブ済みリージョンを横断した検索が動作する | T09〜T11 |
| ④ | OKE上にデプロイして動作する | T12〜T13（全テストがOKE上で実行されることで検証） |

## 既存データモデル（参照）

テスト対象のアプリケーションが使用するモデル:

- **Resource**: OCID、名前、タイプ、リージョン、状態、タグ、作成日時
- **Node**: OCID、名前、タイプ、リージョン、コンパートメント、外部フラグ
- **Edge**: ソースOCID、ターゲットOCID、関係タイプ、説明
- **Artifact**: タイプ、バージョン、作成日時、データ（検索結果またはマップ）
