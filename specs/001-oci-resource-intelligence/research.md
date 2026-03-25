# リサーチ結果

**ブランチ**: `001-oci-resource-intelligence`
**作成日**: 2026-03-24

---

## R1: OCI Resource Search API によるテナント横断検索

**決定**: OCI Resource Search API（`oci.resource_search.ResourceSearchClient`）を使用し、構造化クエリ言語でリソースを検索する

**根拠**:
- Resource Search APIはテナント全体を対象とした横断検索を単一APIで提供する
- リソースタイプ、コンパートメント、ライフサイクル状態、タグによるフィルタをクエリ構文で表現可能
- ページネーション（`page`トークン）により大量結果の段階的取得が可能
- 各リージョンに対してリージョナルエンドポイントを指定して呼び出す必要がある

**検討した代替案**:
- 各サービスAPIの`list_*`を個別呼び出し → APIコール数が膨大になり非効率。リソースタイプごとに異なるクライアントが必要
- OCI Monitoring API → リソースのメタデータ取得には不適

---

## R2: マルチリージョン並列スキャン

**決定**: `asyncio`と`concurrent.futures.ThreadPoolExecutor`を組み合わせ、全サブスクライブ済みリージョンへの検索を並列実行する

**根拠**:
- OCI Python SDKは同期クライアントのため、`ThreadPoolExecutor`でI/Oバウンドな並列化を実現
- リージョン数は通常10〜30程度のため、スレッド数は管理可能
- `oci.identity.IdentityClient.list_region_subscriptions`でサブスクライブ済みリージョン一覧を動的取得

**検討した代替案**:
- 逐次実行 → リージョン数×ページネーション回数で10分の時間制約を超過するリスク
- `aiohttp`による完全非同期 → OCI SDKが非同期未対応のため追加の複雑さが生じる

---

## R3: 依存関係マップの解析戦略

**決定**: Resource Search APIで起点リソースを取得後、各リソースタイプに対応した個別サービスAPIで依存先を辿る。訪問済みノードセットで循環参照を防止する

**根拠**:
- Resource Search APIだけではリソース間の接続情報（VNICアタッチメント、ボリュームアタッチメント等）が取得できない
- BFS（幅優先探索）アルゴリズムで深度制御が容易
- 訪問済みOCIDの`set`で循環参照検出と無限ループ防止

**必要なサービスAPI**:
- `ComputeClient.list_vnic_attachments` → Instance→Subnet
- `ComputeClient.list_volume_attachments` → Instance→BlockVolume
- `ComputeClient.list_boot_volume_attachments` → Instance→BootVolume
- `LoadBalancerClient.get_load_balancer` → LB→BackendSet→Instance
- `VirtualNetworkClient.get_subnet` → Subnet→VCN、SecurityList、RouteTable
- `DatabaseClient.get_db_system` → DbSystem→Subnet
- `ContainerEngineClient.get_cluster` → OkeCluster→VCN
- `ContainerEngineClient.list_node_pools` → OkeNodePool→Subnet

**検討した代替案**:
- OCI Resource Manager依存関係グラフ → Resource Managerで管理されていないリソースは対象外
- 全リソースを先に取得してメモリ内で関係構築 → 大規模テナントではメモリ消費が過大

---

## R4: Chainlit フロントエンド統合

**決定**: Chainlitをフロントエンドとして使用し、チャットインターフェースから検索・マップ生成を自然言語で指示可能にする

**根拠**:
- Chainlitは Python ネイティブのチャットUIフレームワークで、バックエンドとの統合が容易
- `@cl.on_message`デコレータでメッセージハンドリングを実装
- `cl.Message`で構造化されたレスポンス（テーブル、JSON）を返却可能
- OKEデプロイ時はHTTPサービスとして公開

**検討した代替案**:
- Streamlit → チャットインターフェースに特化していない
- カスタムFastAPI + React → 複雑さがMVPに不適（Constitution V: シンプルさ）

---

## R5: MVP向けローカルストレージ

**決定**: 検索結果と依存関係マップの履歴をJSON形式でローカルファイルシステム（PersistentVolume）に保存する

**根拠**:
- MVP段階ではAutonomous Database不要（Constitution V: シンプルさ）
- ファイル名に日付を含め、同日重複実行は上書き
- パス例: `/data/history/resource_search/2026-03-24.json`
- OKEデプロイ時はPersistentVolumeClaimで永続化

**検討した代替案**:
- SQLite → 追加依存が発生し、将来のADB移行時にスキーマ変換が必要
- メモリ内のみ → Pod再起動で履歴喪失

---

## R6: OKEデプロイ戦略

**決定**: 単一Deployment + Service構成。OCIRからイメージをプル、Instance Principalで認証

**根拠**:
- 単一Podで十分（MVPではスケールアウト不要）
- `imagePullSecrets`に`ocir`シークレットを指定
- Instance Principalにより追加の認証情報管理が不要
- Chainlitのデフォルトポート（8000）でService公開

**検討した代替案**:
- Helm Chart → MVP段階では過剰（Constitution V: シンプルさ）
- Knative → 追加の複雑さ、常時起動が適切

---

## R7: エラーハンドリングとリトライ

**決定**: OCI SDK組み込みのリトライ設定（`oci.retry.RetryStrategyBuilder`）を使用。429に対してexponential backoff（最大3回）

**根拠**:
- OCI Python SDKはリトライ戦略を組み込みで提供
- `RetryStrategyBuilder`でリトライ回数、バックオフ係数、対象ステータスコードを設定可能
- 認証エラー（401/403）はリトライ対象外とし、即座にエラーレスポンス

**検討した代替案**:
- カスタムリトライロジック → SDKの機能を再実装する必要はない
- tenacity ライブラリ → 追加依存。SDK組み込みで十分
