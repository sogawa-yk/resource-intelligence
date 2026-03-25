# Tasks: OCI Resource Intelligence Agent（MVP）

**Input**: Design documents from `/specs/001-oci-resource-intelligence/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/
**スコープ**: MVPフェーズのみ（US1: リソース検索、US2: 依存関係マップ、US5: エラーハンドリング基本、Chainlit UI、OKEデプロイ）

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 並列実行可能（異なるファイル、依存関係なし）
- **[Story]**: 対応ユーザーストーリー（US1, US2, US5）

---

## Phase 1: Setup（プロジェクト初期化）

**Purpose**: プロジェクト構造の作成と依存関係の設定

- [x] T001 plan.mdのプロジェクト構造に従い、src/ri_agent/ 配下のディレクトリ構造（models/, services/, oci_client/, storage/）と各__init__.pyを作成する
- [x] T002 pyproject.tomlを作成し、プロジェクトメタデータ（name: ri-agent, python>=3.11）を定義する
- [x] T003 [P] requirements.txtを作成し、依存パッケージ（chainlit, oci, pydantic, structlog, pytest）を記載する
- [x] T004 [P] tests/ 配下のディレクトリ構造（unit/, integration/, performance/, e2e/）と各__init__.pyを作成する
- [x] T005 [P] .gitignoreを作成し、Python標準の除外パターン（__pycache__, .venv, *.pyc, /data/）を設定する

**Checkpoint**: プロジェクト構造が完成し、`pip install -r requirements.txt` が成功する

---

## Phase 2: Foundational（基盤構築）

**Purpose**: 全ユーザーストーリーに必要な共通基盤。このフェーズ完了まで後続作業は開始不可

**⚠️ CRITICAL**: ユーザーストーリーの実装はこのフェーズ完了後に開始すること

- [x] T006 src/ri_agent/config.pyに設定管理クラスを実装する。環境変数からテナントOCID、データディレクトリパス（デフォルト: /data/history）、ログレベルを読み込む。pydantic-settingsを使用する
- [x] T007 [P] src/ri_agent/models/resource.pyにResource, Tagsモデルを実装する。data-model.mdのフィールド定義に従い、Pydantic BaseModelで定義する
- [x] T008 [P] src/ri_agent/models/dependency.pyにDependencyMap, Node, Edge, RelationType（Enum）モデルを実装する。data-model.mdに従い、is_externalフラグを含める
- [x] T009 [P] src/ri_agent/models/artifact.pyにArtifact, SearchRequest, DependencyMapRequestモデルを実装する。artifact_typeは"resource_list"と"dependency_map"のリテラル型。DependencyMapRequestのdepthはge=0, le=10のバリデーション付き
- [x] T010 src/ri_agent/oci_client/base.pyにOCI SDK共通設定を実装する。Instance Principal認証（oci.auth.signers.InstancePrincipalsSecurityTokenSigner）、RetryStrategyBuilder（429に対してexponential backoff最大3回）、ローカル開発用のConfigFileAuthentication切り替えを含める
- [x] T011 src/ri_agent/storage/base.pyにストレージ抽象インターフェース（StorageBase ABC）を定義する。save_artifact(artifact_type, artifact)とload_artifact(artifact_type, date)の2メソッド
- [x] T012 src/ri_agent/storage/local_json.pyにLocalJsonStorageを実装する。StorageBaseを継承し、/data/history/{artifact_type}/{YYYY-MM-DD}.jsonに保存。同日の重複実行は上書き。ディレクトリ自動作成を含める
- [x] T013 src/ri_agent/oci_client/search.pyにResourceSearchClientラッパーを実装する。oci.resource_search.ResourceSearchClientを使用し、構造化クエリの組み立て、ページネーション（pageトークン）による全件取得、リージョン指定を含める
- [x] T014 src/ri_agent/oci_client/__init__.pyに全クライアントの初期化ファクトリ関数create_clients(config)を実装する。base.pyの認証設定を使用し、必要なクライアントを一括生成する

**Checkpoint**: 共通モデル・OCI認証・ストレージが動作し、Resource Search APIへの接続テストが可能

---

## Phase 3: User Story 1 - テナント横断リソース検索 (Priority: P1) 🎯 MVP

**Goal**: 全サブスクライブ済みリージョン・コンパートメントを横断してOCIリソースを検索・一覧化する

**Independent Test**: コンパートメントOCIDを指定してリソース検索を実行し、リソース一覧がJSON形式で返却されることを確認する

### Implementation for User Story 1

- [x] T015 [US1] src/ri_agent/services/resource_search.pyにResourceSearchServiceクラスを実装する。単一リージョンでのリソース検索メソッド（search_single_region）を作成し、SearchRequestのフィルタ条件（resource_types, tag_filters, lifecycle_states, compartment_ocid）をOCI Resource Search APIの構造化クエリに変換する。ページネーションで全件取得する
- [x] T016 [US1] src/ri_agent/services/resource_search.pyにマルチリージョン並列検索メソッド（search_all_regions）を追加する。oci.identity.IdentityClient.list_region_subscriptionsでサブスクライブ済みリージョン一覧を取得し、concurrent.futures.ThreadPoolExecutorで並列検索を実行する。各リージョンの結果をマージしてArtifact（resource_list）として返却する
- [x] T017 [US1] src/ri_agent/services/resource_search.pyに検索結果のフィルタリングとソートロジックを追加する。タグフィルタ（freeform/defined両対応）、ライフサイクル状態フィルタ（デフォルト全状態含む）をAPI結果に対してポストフィルタとして適用する
- [x] T018 [US1] src/ri_agent/services/resource_search.pyに履歴保存の呼び出しを追加する。検索完了後にLocalJsonStorage.save_artifactを呼び出し、結果をローカルJSONファイルに保存する

**Checkpoint**: ResourceSearchServiceが全リージョン横断検索を実行し、フィルタ付きのArtifactを返却できる

---

## Phase 4: User Story 2 - リソース依存関係マップ生成 (Priority: P1) 🎯 MVP

**Goal**: リソース間の依存関係をノード・エッジのグラフ構造として生成する。10種類の関係タイプに対応

**Independent Test**: ComputeインスタンスのOCIDを起点として依存関係マップを生成し、Subnet・VCN・BlockVolumeへのエッジが含まれることを確認する

### Implementation for User Story 2

- [x] T019 [P] [US2] src/ri_agent/oci_client/compute.pyにComputeClientラッパーを実装する。list_vnic_attachments（Instance→Subnet）、list_volume_attachments（Instance→BlockVolume）、list_boot_volume_attachments（Instance→BootVolume）を含める
- [x] T020 [P] [US2] src/ri_agent/oci_client/network.pyにVirtualNetworkClientラッパーを実装する。get_subnet（Subnet→VCN, SecurityList, RouteTable取得）、get_vcn、get_security_list、get_route_tableを含める
- [x] T021 [P] [US2] src/ri_agent/oci_client/loadbalancer.pyにLoadBalancerClientラッパーを実装する。get_load_balancer（LB→BackendSet→Backend取得）を含める
- [x] T022 [P] [US2] src/ri_agent/oci_client/database.pyにDatabaseClientラッパーを実装する。get_db_system（DbSystem→Subnet取得）を含める
- [x] T023 [P] [US2] src/ri_agent/oci_client/container.pyにContainerEngineClientラッパーを実装する。get_cluster（OkeCluster→VCN取得）、list_node_pools（OkeNodePool→Subnet取得）を含める
- [x] T024 [US2] src/ri_agent/services/dependency_map.pyにDependencyMapServiceクラスを実装する。BFS（幅優先探索）アルゴリズムで起点OCIDからdepth制御付きの依存関係探索を行う。visited setで循環参照を防止する。depthが0の場合は起点ノードのみ返却、10を超える場合は10にキャップする
- [x] T025 [US2] src/ri_agent/services/dependency_map.pyにリソースタイプごとの依存関係解決メソッド群（_resolve_instance_deps, _resolve_subnet_deps, _resolve_lb_deps, _resolve_db_deps, _resolve_oke_deps）を実装する。各メソッドはT019-T023のOCIクライアントを使用してエッジを生成する
- [x] T026 [US2] src/ri_agent/services/dependency_map.pyにクロスバウンダリノード処理を追加する。境界外（別コンパートメント・別リージョン）のターゲットノードはis_external=trueで追加し、OCID・名前・タイプのみ保持する。境界外ノードからの更なる探索は行わない
- [x] T027 [US2] src/ri_agent/services/dependency_map.pyにコンパートメント起点のマップ生成を追加する。root_ocidがコンパートメントの場合、まずResourceSearchServiceで配下リソースを取得し、各リソースを起点として依存関係を解析する
- [x] T028 [US2] src/ri_agent/services/dependency_map.pyに履歴保存の呼び出しを追加する。マップ生成完了後にLocalJsonStorage.save_artifactを呼び出す

**Checkpoint**: DependencyMapServiceが10種類の関係タイプを解析し、循環参照防止・深度制御・クロスバウンダリ参照付きのグラフを返却できる

---

## Phase 5: User Story 5 - エラーハンドリングと部分結果返却 (Priority: P3) 🎯 MVP基本対応

**Goal**: APIレート制限、認証エラー、リージョン到達不能に対する基本的なエラーハンドリングと部分結果返却

**Independent Test**: 到達不能なリージョンを含む検索で、到達可能リージョンの部分結果が返却されエラー情報が含まれることを確認する

### Implementation for User Story 5

- [x] T029 [US5] src/ri_agent/services/resource_search.pyのsearch_all_regionsメソッドにリージョン別エラーハンドリングを追加する。各リージョンの検索で例外が発生した場合、そのリージョンをスキップし、成功したリージョンの結果を部分結果として返却する。errors配列にリージョン名・エラータイプ・メッセージを含める
- [x] T030 [US5] src/ri_agent/services/dependency_map.pyにAPI呼び出しエラーハンドリングを追加する。個別のOCI APIエラー（ServiceError）をキャッチし、取得可能なノード・エッジのみで部分マップを返却する。errors配列にエラー情報を含める
- [x] T031 [US5] src/ri_agent/oci_client/base.pyの認証エラー（401/403）処理を確認し、リトライ対象外であることを明示的に設定する。認証エラー時は即座にOciAuthenticationErrorを発生させる

**Checkpoint**: APIエラー発生時に部分結果が返却され、エラー情報が含まれる

---

## Phase 6: Chainlit UI統合

**Purpose**: Chainlitフロントエンドの実装。US1・US2の結果をチャットUIで表示

- [x] T032 src/ri_agent/app.pyにChainlitアプリケーションのエントリポイントを実装する。@cl.on_chat_startでウェルカムメッセージを表示し、@cl.on_messageでユーザー入力を受け取る基本構造を作成する
- [x] T033 src/ri_agent/app.pyにリソース検索のチャットハンドラを実装する。ユーザーの自然言語入力からSearchRequestパラメータを抽出し（キーワードマッチング）、ResourceSearchServiceを呼び出し、結果をマークダウンテーブル形式でcl.Messageとして返却する。contracts/chainlit-ui.mdのレスポンス形式に従う
- [x] T034 src/ri_agent/app.pyに依存関係マップのチャットハンドラを実装する。ユーザー入力からDependencyMapRequestパラメータを抽出し、DependencyMapServiceを呼び出し、結果をツリー形式のテキストとしてcl.Messageで返却する。contracts/chainlit-ui.mdのレスポンス形式に従う
- [x] T035 src/ri_agent/app.pyにエラー表示ハンドラを追加する。部分結果のerrors配列が空でない場合、警告メッセージ（成功リージョン数・失敗リージョン名）を含めて結果を表示する
- [x] T036 [P] .chainlit/config.tomlを作成し、Chainlit設定（project_name: "Resource Intelligence", port: 8000）を定義する

**Checkpoint**: Chainlit UIからリソース検索と依存関係マップ生成が実行でき、結果が表示される

---

## Phase 7: 可観測性（構造化ログ）

**Purpose**: Constitution IV準拠の構造化ログ実装

- [x] T037 src/ri_agent/config.pyにstructlogの設定を追加する。JSON形式の構造化ログ出力、ログレベル制御、リクエストIDの自動付与を含める
- [x] T038 src/ri_agent/services/resource_search.pyとdependency_map.pyにstructlogによるログ出力を追加する。検索条件、リージョン数、結果件数、実行時間、エラー情報をログに記録する
- [x] T039 [P] src/ri_agent/oci_client/base.pyにAPI呼び出しログを追加する。API名、リージョン、レスポンスステータス、レイテンシをログに記録する

**Checkpoint**: 全操作が構造化ログとして記録され、JSON形式で出力される

---

## Phase 8: OKEデプロイ

**Purpose**: Dockerイメージ作成とKubernetesマニフェストによるOKEデプロイ

- [x] T040 Dockerfileを作成する。python:3.11-slimベースイメージ、requirements.txtからの依存インストール、src/をコピー、EXPOSE 8000、chainlit runコマンドをENTRYPOINTに設定する
- [x] T041 [P] k8s/namespace.yamlを作成する。ri-agent名前空間を定義する
- [x] T042 [P] k8s/pvc.yamlを作成する。履歴保存用のPersistentVolumeClaim（名前: ri-agent-history、容量: 1Gi）を定義する
- [x] T043 k8s/deployment.yamlを作成する。ri-agentのDeploymentを定義する。replicas: 1、imagePullSecretsにocirシークレットを指定、PVCをマウント（/data/history）、環境変数でOCI_TENANT_OCIDとDATA_DIRを設定する
- [x] T044 k8s/service.yamlを作成する。ri-agentのServiceを定義する。port: 8000、type: ClusterIP（MVP）

**Checkpoint**: `kubectl apply -f k8s/` でOKEにデプロイし、Chainlit UIにアクセスできる

⚠️ **OCIRイメージプッシュ**: Dockerイメージ名 `ri-agent` でOCIRリポジトリの手動作成が必要です。T040完了後にイメージビルド・プッシュを行います。

---

## Phase 9: Polish & 横断的改善

**Purpose**: 全体的な品質向上とドキュメント整備

- [x] T045 src/ri_agent/models/ 配下の全モデルに対し、不正入力時のバリデーションエラーメッセージを日本語で設定する
- [x] T046 src/ri_agent/app.pyに入力パース失敗時のユーザーフレンドリーなエラーメッセージ（使用例の表示）を追加する
- [x] T047 quickstart.mdの手順に従い、ローカル開発環境からの起動とOKEデプロイの動作確認を実施する

**Checkpoint**: MVPの全機能が動作し、OKE上でChainlit UIからリソース検索と依存関係マップ生成が確認できる

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1（Setup）**: 依存なし — 即座に開始可能
- **Phase 2（Foundational）**: Phase 1完了後に開始。**全ユーザーストーリーをブロック**
- **Phase 3（US1: リソース検索）**: Phase 2完了後に開始
- **Phase 4（US2: 依存関係マップ）**: Phase 2完了後に開始。US1のResourceSearchServiceを使用するため、T015-T016の完了が望ましい
- **Phase 5（US5: エラーハンドリング）**: Phase 3, 4のサービス実装後に追加
- **Phase 6（Chainlit UI）**: Phase 3, 4のサービス完了後に開始
- **Phase 7（可観測性）**: Phase 2完了後いつでも開始可能
- **Phase 8（OKEデプロイ）**: Phase 6（Chainlit UI）完了後に開始
- **Phase 9（Polish）**: 全Phase完了後

### User Story Dependencies

- **US1（リソース検索）**: Phase 2完了後に独立して開始可能
- **US2（依存関係マップ）**: US1のResourceSearchServiceに依存（コンパートメント起点マップ用）。ただし、単一リソース起点のマップはUS1なしでも動作
- **US5（エラーハンドリング）**: US1・US2のサービスが存在する前提で追加実装

### Within Each User Story

- モデル → サービス → UIの順で実装
- サービス内の依存関係解決メソッドは並列で実装可能

### Parallel Opportunities

- Phase 1: T003, T004, T005 は並列実行可能
- Phase 2: T007, T008, T009 は並列実行可能（モデル群）
- Phase 4: T019, T020, T021, T022, T023 は並列実行可能（OCIクライアントラッパー群）
- Phase 7: T039 は他のPhase 7タスクと並列実行可能
- Phase 8: T041, T042 は並列実行可能

---

## Parallel Example: User Story 2

```bash
# OCIクライアントラッパーを並列で作成:
Task: "T019 ComputeClientラッパー in src/ri_agent/oci_client/compute.py"
Task: "T020 VirtualNetworkClientラッパー in src/ri_agent/oci_client/network.py"
Task: "T021 LoadBalancerClientラッパー in src/ri_agent/oci_client/loadbalancer.py"
Task: "T022 DatabaseClientラッパー in src/ri_agent/oci_client/database.py"
Task: "T023 ContainerEngineClientラッパー in src/ri_agent/oci_client/container.py"

# 上記完了後、依存関係解析を実装:
Task: "T024 BFSベースの依存関係探索 in src/ri_agent/services/dependency_map.py"
```

---

## Implementation Strategy

### MVP First（US1 → US2 → US5 → UI → Deploy）

1. Phase 1: Setup完了
2. Phase 2: Foundational完了（全ストーリーのブロック解除）
3. Phase 3: US1（リソース検索）完了 → **単体で検証可能**
4. Phase 4: US2（依存関係マップ）完了 → **単体で検証可能**
5. Phase 5: US5（エラーハンドリング）追加
6. Phase 6: Chainlit UI統合 → **UIから全機能を確認**
7. Phase 7: 構造化ログ追加
8. Phase 8: OKEデプロイ → **本番環境で動作確認**
9. Phase 9: Polish

### 推奨停止ポイント

- **Phase 3完了後**: リソース検索がプログラム的に動作することを確認
- **Phase 6完了後**: Chainlit UIでの操作確認。ローカルで動作検証
- **Phase 8完了後**: OKE上での最終確認

---

## Notes

- [P]タスクは異なるファイルを対象とし、並列実行可能
- [Story]ラベルはトレーサビリティのために付与
- US3（作成者特定）、US4（A2A連携）はMVPスコープ外（Phase 2で対応予定）
- OCIRリポジトリの手動作成はT040完了時に案内する
- 全ドキュメントは日本語で作成（Constitution I準拠）
- テストタスクはMVPでは省略し、各Phaseのcheckpointで手動確認を行う
