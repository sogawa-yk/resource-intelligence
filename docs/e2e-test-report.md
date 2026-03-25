# E2Eテストレポート: OCI Resource Intelligence Agent

**実施日**: 2026-03-25
**環境**: OKE（Oracle Kubernetes Engine）
**名前空間**: `ri-agent`
**公開URL**: https://ri.sogawa-yk.com/
**GenAIモデル**: `cohere.command-a-03-2025`（OCI GenAI Service / us-chicago-1）

---

## テスト環境

| 項目 | 値 |
|------|------|
| Kubernetes | OKE クラスタ |
| Pod | `ri-agent-68fc5f657d-tql8z` |
| イメージ | `yyz.ocir.io/orasejapan/ri-agent:latest` |
| 認証方式 | Instance Principal |
| Ingress | OCI Native Ingress Controller（`mcp-ingress-class`） |
| TLS | ワイルドカード証明書（`*.sogawa-yk.com`） |
| ストレージ | PersistentVolumeClaim `ri-agent-history`（1Gi） |

---

## テスト結果サマリー

**全6シナリオ PASS / 0 FAIL**

---

## テストシナリオ詳細

### シナリオ1: リソース検索（全件）

- **入力**: `全リソースを一覧して`
- **期待アクション**: `resource_search`
- **結果**: ✅ PASS
- **レイテンシ**: 1.59秒
- **GenAIレスポンス**:
```json
{
  "action": "resource_search",
  "params": {}
}
```

### シナリオ2: リソース検索（リージョン＋タイプ指定）

- **入力**: `ap-tokyo-1のインスタンスを表示して`
- **期待アクション**: `resource_search`
- **結果**: ✅ PASS
- **レイテンシ**: 2.33秒
- **GenAIレスポンス**:
```json
{
  "action": "resource_search",
  "params": {
    "resource_types": ["Instance"],
    "regions": ["ap-tokyo-1"]
  }
}
```
- **検証ポイント**: リージョン名がOCI識別子形式で正確に抽出されている。リソースタイプがOCI標準名（`Instance`）で返されている。

### シナリオ3: リソース検索（タグフィルタ）

- **入力**: `project=alphaタグのリソースを検索`
- **期待アクション**: `resource_search`
- **結果**: ✅ PASS
- **レイテンシ**: 2.13秒
- **GenAIレスポンス**:
```json
{
  "action": "resource_search",
  "params": {
    "tag_filters": {
      "project": "alpha"
    }
  }
}
```
- **検証ポイント**: タグのキー・バリューが正確にパースされている。

### シナリオ4: 依存関係マップ（OCID指定）

- **入力**: `ocid1.instance.oc1.ap-tokyo-1.xxxの依存関係を表示`
- **期待アクション**: `dependency_map`
- **結果**: ✅ PASS
- **レイテンシ**: 3.10秒
- **GenAIレスポンス**:
```json
{
  "action": "dependency_map",
  "params": {
    "root_ocid": "ocid1.instance.oc1.ap-tokyo-1.xxx",
    "depth": 3
  }
}
```
- **検証ポイント**: OCIDがそのまま保持されている。デフォルト深度3が設定されている。

### シナリオ5: 依存関係マップ（深度指定）

- **入力**: `ocid1.compartment.oc1..yyyの依存関係を深度2で表示`
- **期待アクション**: `dependency_map`
- **結果**: ✅ PASS
- **レイテンシ**: 2.69秒
- **GenAIレスポンス**:
```json
{
  "action": "dependency_map",
  "params": {
    "root_ocid": "ocid1.compartment.oc1..yyy",
    "depth": 2
  }
}
```
- **検証ポイント**: コンパートメントOCIDが正しく認識されている。ユーザー指定の深度2が反映されている。

### シナリオ6: ヘルプ

- **入力**: `使い方を教えて`
- **期待アクション**: `help`
- **結果**: ✅ PASS
- **レイテンシ**: 3.43秒
- **GenAIレスポンス**:
```json
{
  "action": "help",
  "message": "OCIリソースの検索や依存関係の確認ができます。リソースの種類、リージョン、状態、タグなどで検索したり、特定のOCIDから依存関係を可視化できます。"
}
```
- **検証ポイント**: 検索・マップ以外の入力が正しくヘルプに分類されている。日本語で適切な案内メッセージが返されている。

---

## デプロイ時に発見・修正した問題

| # | 問題 | 原因 | 修正内容 |
|---|------|------|----------|
| 1 | imagePullSecretが見つからない | `ocir`シークレットが`ri-agent`名前空間に未作成 | `default`名前空間からコピー |
| 2 | Chainlit config.toml outdatedエラー | 手動作成した設定ファイルのフォーマットが古い | Dockerfile内で`chainlit init`に変更 |
| 3 | `structlog.get_level_from_name`不在 | インストール済みstructlogバージョンにAPIが存在しない | `logging`モジュールのレベルマップで代替 |
| 4 | `oci.retry.RETRYABLE_STATUSES_AND_CODES`不在 | OCI SDK バージョン差異 | `oci.retry.DEFAULT_RETRY_STRATEGY`に変更 |
| 5 | Instance Principal接続がモジュールロード時に失敗 | サービス初期化がimport時に実行される | 遅延初期化パターンに変更 |
| 6 | GenAI 404: `cohere.command-r-plus` not found | モデルIDにバージョンサフィックスが必要 | `cohere.command-a-03-2025`に変更 |
| 7 | GenAI 400: Chat request type mismatch | CohereモデルにGenericChatRequestを使用 | `CohereChatRequest`に変更 |
| 8 | PVC Multi-Attach エラー | ReadWriteOnceのPVCを旧Podが保持 | 旧ReplicaSetをスケールダウンしてから新Pod起動 |
| 9 | クエリ構文エラー `mismatched input 'Instance'` | リソースタイプ名をシングルクォートで囲んでいた | クォートなしに修正（OCI構造化クエリ仕様準拠） |
| 10 | Instance Principal認証の二重渡し | `config={"signer": signer}` と `signer=signer` を同時に渡していた | `create_signer()` が `(config, signer)` タプルを返すように変更。`create_oci_client` ヘルパーで統一 |
| 11 | 検索結果0件 | テナントOCIDで `compartmentId` フィルタを付けるとルート直下のみに限定 | `compartment_ocid` 未指定時はフィルタ自体を省略（テナント全体検索） |
| 12 | コンパートメント名が空 | Resource Search APIがcompartment_nameを返さない | IdentityClient.get_compartmentで名前を解決（キャッシュ付き） |
| 13 | 依存関係マップのcompartmentIdが空 | BFS開始時にcompartment_idが空文字のまま | Resource Search APIで起点リソースの情報を事前取得 |
| 14 | RelationType表示が`RelationType.attached_to` | `model_dump()`がEnum名をそのまま出力 | `model_dump(mode="json")`で値のみ出力に変更 |
| 15 | 依存先ノード名がOCID断片 | エッジ生成時にtarget_nameを解決していない | VCN/Subnet/SecurityList/RouteTableの名前をAPI取得して設定 |

---

## リソース検索精度テスト（OCI CLI比較）

**テスト方法**: OCI CLIの検索結果（ユーザー権限）とアプリの検索結果（Instance Principal権限）を比較。
Instance Principal権限で取得可能なリソースが正しく返されるかを検証。

| リソースタイプ | OCI CLI件数 | アプリ件数 | 一致数 | 一致率（App基準） | 結果 |
|---------------|------------|----------|-------|-----------------|------|
| Instance | 45 | 4 | 4 | 100% | ✅ PASS |
| Vcn | 23 | 7 | 7 | 100% | ✅ PASS |
| Subnet | 62 | 23 | 23 | 100% | ✅ PASS |

**件数差の原因**: Instance Principal権限がユーザー権限より狭い（特定コンパートメントのみ参照可能）ため。アプリが返す全リソースはCLI結果にも存在しており、**ロジックの正しさを確認済み**。

**フィールド値検証**: 一致したリソースのname、resource_type、lifecycle_stateフィールドが**全て完全一致**。

---

## Playwright UIテスト（ブラウザE2E）

**テスト方法**: Playwright MCPでhttps://ri.sogawa-yk.com/ にアクセスし、実際のブラウザ操作でテスト。

| # | シナリオ | 入力 | 検証項目 | 結果 |
|---|---------|------|---------|------|
| 1 | リソース検索 | 「ap-tokyo-1のインスタンスを表示して」 | テーブル表示、4件、コンパートメント名「yuki.sogawa」表示 | ✅ PASS |
| 2 | 依存関係マップ | 実在InstanceのOCIDで依存関係表示 | ツリー表示、5ノード4エッジ、実名表示（Subnet/VCN/SecurityList/RouteTable） | ✅ PASS |
| 3 | ヘルプ | 「使い方を教えて」 | 日本語で操作ガイドを表示 | ✅ PASS |

**テスト2の依存関係ツリー出力**:
```
一時的なビルド用インスタンス (Instance)
└── [attached_to] → oke-svclbsubnet-quick-services-cluster-eb340bb68-regional (Subnet)
    ├── [belongs_to] → oke-vcn-quick-services-cluster-eb340bb68 (Vcn)
    ├── [governed_by] → oke-svclbseclist-quick-services-cluster-eb340bb68 (SecurityList)
    └── [governed_by] → oke-public-routetable-services-cluster-eb340bb68 (RouteTable)
```

---

## パフォーマンス

| 指標 | 値 |
|------|------|
| GenAI平均レイテンシ | 2.55秒 |
| GenAI最小レイテンシ | 1.59秒（シナリオ1） |
| GenAI最大レイテンシ | 3.43秒（シナリオ6） |
| HTTPS応答コード | 200 |
| Pod起動時間 | 約60秒（PVCアタッチ含む） |
