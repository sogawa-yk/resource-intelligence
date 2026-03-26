# Quickstart: MVP判定基準E2Eバリデーション

**Branch**: `002-mvp-e2e-validation`

## 前提条件

- OKEクラスタ稼働中、kubectl接続可能
- https://ri.sogawa-yk.com/ でChainlit UIがアクセス可能
- Playwright MCP利用可能
- OCIRへのプッシュ権限あり

## テスト実行手順

### 1. 現状確認テスト

Playwright MCPで https://ri.sogawa-yk.com/ にアクセスし、以下のテストケースを順次実行:

1. ページアクセス → ウェルカムメッセージ確認
2. 「インスタンスを表示して」→ リソース検索結果確認
3. 「VCNを一覧して」→ VCN一覧確認
4. 「{OCID}の依存関係を表示」→ 依存関係マップ確認
5. 「全リージョンのインスタンスを検索」→ マルチリージョン結果確認

各テストでスクリーンショットを`playwright/002-mvp-e2e-validation/`に保存。

### 2. 修正が必要な場合

修正対象:
- `src/ri_agent/app.py` — 全リソース検索のフォールバック
- `src/ri_agent/oci_client/genai.py` — 表記揺れ対応
- `k8s/deployment.yaml` — メモリリミット引き上げ

修正後のデプロイ:
```bash
# Dockerイメージビルド
docker build -t yyz.ocir.io/orasejapan/ri-agent:latest .

# OCIRプッシュ
docker push yyz.ocir.io/orasejapan/ri-agent:latest

# OKE再デプロイ
kubectl rollout restart deployment/ri-agent -n ri-agent
kubectl rollout status deployment/ri-agent -n ri-agent
```

### 3. 再テスト

全テストケース（T01〜T13）をPlaywright MCPで再実行し、全合格を確認。

### 4. レポート生成

`playwright/002-mvp-e2e-validation/test-report.md`にテスト結果をまとめる。
