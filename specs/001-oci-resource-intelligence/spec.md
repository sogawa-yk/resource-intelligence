# Feature Specification: OCI Resource Intelligence Agent

**Feature Branch**: `001-oci-resource-intelligence`
**Created**: 2026-03-24
**Status**: Draft
**Input**: User description: "RI_Resource_Intelligence_Spec.md に基づくOCIテナント全体のリソース検索・一覧化・依存関係マップ生成・作成者特定を行う読み取り専用エージェント"

## Clarifications

### Session 2026-03-24

- Q: 大規模テナント（1万リソース以上）での全リージョン横断検索の許容完了時間は？ → A: 10分以内（リージョン並列スキャンで達成可能なバランス型目標）
- Q: 依存関係マップの最大探索深度の上限は？ → A: 最大10（実用的な全依存チェーンをカバーしつつAPI呼び出し量を制御）
- Q: 検索結果・依存関係マップの履歴保持粒度は？ → A: 実行ごとに保持し、同日の重複実行は最新のみ保持（日次トレンド分析に最適）
- Q: 削除済み・終了済みリソースをデフォルトで検索結果に含めるか？ → A: デフォルトで全ライフサイクル状態を含む（lifecycle_statesフィルタで絞り込み可能）
- Q: 依存関係マップでクロスコンパートメント・クロスリージョンのエッジをどう扱うか？ → A: 境界外エッジを含むが、境界外ノードは参照のみ（OCID・名前・タイプのみ、詳細なし）

## User Scenarios & Testing *(mandatory)*

### User Story 1 - テナント横断リソース検索 (Priority: P1)

オーケストレーター（ORCH）またはピアエージェント（ENV、TA、CQ）が、OCIテナント内の全サブスクライブ済みリージョン・全コンパートメントを横断してリソースを検索・一覧化する。リソースタイプ、タグ、ライフサイクル状態などの条件でフィルタリングし、構造化されたリソースリストを取得する。

**Why this priority**: リソース検索はエージェントの基本機能であり、依存関係マップや作成者特定など他のすべてのスキルの前提となる。棚卸し（S1）、キャッチアップ（S2-B）、障害分析（S4）の全シナリオで利用される。

**Independent Test**: コンパートメントOCIDを指定してリソース検索を実行し、該当コンパートメント内のリソース一覧がJSON形式で返却されることを確認する。

**Acceptance Scenarios**:

1. **Given** テナントに複数リージョン・コンパートメントにリソースが存在する状態, **When** フィルタ条件なしでリソース検索を実行する, **Then** 全リージョン・全コンパートメントのリソースが一覧として返却される
2. **Given** テナントにタグ付きリソースが存在する状態, **When** タグフィルタ（例: `{"project": "alpha"}`）を指定して検索する, **Then** 該当タグを持つリソースのみが返却される
3. **Given** テナントに大量のリソースが存在する状態, **When** リソース検索を実行する, **Then** ページネーションにより全件が取得でき、部分的な結果にならない
4. **Given** 特定のリソースタイプとライフサイクル状態を指定する, **When** `resource_types: ["Instance"]` と `lifecycle_states: ["RUNNING"]` で検索する, **Then** 稼働中のインスタンスのみが返却される

---

### User Story 2 - リソース依存関係マップ生成 (Priority: P1)

オーケストレーターまたはTAエージェントが、特定のリソースまたはコンパートメントを起点として、リソース間の依存関係をグラフ構造（ノード・エッジ）として取得する。Compute→Subnet→VCN、LB→BackendSet→Instance、DbSystem→Subnetなどの関係性を可視化する。

**Why this priority**: 依存関係の把握は棚卸し（S1-F04）と障害分析（S4-F02、S4-F03）の両方で必須機能。障害時の影響範囲特定にも直結する。

**Independent Test**: 既知のComputeインスタンスのOCIDを起点として依存関係マップを生成し、接続先Subnet・VCN・Block Volumeなどのノードとエッジが正しく含まれることを確認する。

**Acceptance Scenarios**:

1. **Given** ComputeインスタンスがSubnetに接続しBlock Volumeがアタッチされている状態, **When** そのインスタンスのOCIDを起点に依存関係マップを生成する, **Then** Instance→Subnet（attached_to）、Instance→BlockVolume（uses）、Subnet→VCN（belongs_to）のエッジが含まれる
2. **Given** LoadBalancerがBackendSetを持ちバックエンドにInstanceが設定されている状態, **When** LBのOCIDを起点にマップ生成する, **Then** LB→BackendSet（contains）、BackendSet→Instance（routes_to）のエッジが含まれる
3. **Given** 探索深度（depth）を1に制限して依存関係マップを生成する, **When** 結果を確認する, **Then** 起点リソースから直接接続されたリソースのみが含まれ、間接的な依存は含まれない
4. **Given** コンパートメントOCIDを起点として依存関係マップを生成する, **When** 結果を確認する, **Then** コンパートメント内の全リソースとその関係性がマップに含まれる

---

### User Story 3 - リソース作成者特定 (Priority: P2)

オーケストレーターが棚卸しの一環として、指定されたリソースの作成者を特定する。まずタグ（`freeform_tags.created_by` または `defined_tags.*.CreatedBy`）を確認し、タグが存在しない場合はAudit Logから`CreateXxx`イベントを検索して作成者を特定する。

**Why this priority**: 作成者特定は棚卸し（S1-F05）で求められるが、リソース検索と依存関係マップが先に動作する必要がある。Audit Logの保持期間制約（90日）もあるため、補助的な位置づけ。

**Independent Test**: タグ付きリソースとタグなしリソースのOCIDリストを渡し、タグからの特定結果、Audit Logからの特定結果、未解決の3パターンが正しく返却されることを確認する。

**Acceptance Scenarios**:

1. **Given** `freeform_tags.created_by` が設定されたリソース, **When** 作成者特定を実行する, **Then** タグの値が `creator_user` として返却され `creator_source` が `freeform_tag` となる
2. **Given** タグが未設定だがAudit Logに作成イベントが残っているリソース, **When** 作成者特定を実行する, **Then** Audit Logから作成者が特定され `creator_source` が `audit_log` となる
3. **Given** タグが未設定かつAudit Logの保持期間（90日）を超過したリソース, **When** 作成者特定を実行する, **Then** `unresolved` に分類され理由として保持期間超過が記載される

---

### User Story 4 - ピアツーピアエージェント連携 (Priority: P2)

ENVエージェント（キャッチアップ時）、TAエージェント（障害分析時）、CQエージェント（コスト分析時）が、A2Aプロトコル経由でRIエージェントのスキルを直接呼び出し、必要な構成情報を取得する。

**Why this priority**: エージェント間連携はマルチエージェントシステムの中核機能だが、各スキルの単体動作が前提となるため、P2に位置づける。

**Independent Test**: ENVエージェントからresource-searchスキルを呼び出し、適切なレスポンスが返却されることを確認する。

**Acceptance Scenarios**:

1. **Given** ENVエージェントが新メンバーの環境質問に対応中, **When** RI.resource-searchを呼び出してコンパートメント内リソースを取得する, **Then** 構造化されたリソースリストが返却される
2. **Given** TAエージェントが障害分析中, **When** RI.dependency-mapを呼び出して障害対象リソースの依存関係を取得する, **Then** 依存関係グラフが返却される
3. **Given** CQエージェントがコスト要因分析中, **When** RI.resource-searchで高コストリソースの詳細を取得する, **Then** リソースの構成情報が返却される

---

### User Story 5 - エラーハンドリングと部分結果返却 (Priority: P3)

APIレート制限、認証エラー、リージョン到達不能などの障害発生時に、適切なエラーハンドリングを行い、可能な限り部分的な結果を返却する。

**Why this priority**: 正常系の全機能が動作した上で、異常系の堅牢性を確保する。

**Independent Test**: 到達不能なリージョンを含む検索を実行し、到達可能なリージョンの結果が部分結果として返却され、エラー情報が含まれることを確認する。

**Acceptance Scenarios**:

1. **Given** OCI APIがレート制限（429）を返す状態, **When** リソース検索を実行する, **Then** exponential backoffで最大3回リトライされ、成功すれば結果が返却される
2. **Given** 認証エラー（401/403）が発生する状態, **When** 操作を実行する, **Then** Taskが `failed` に遷移し、エラー詳細がArtifactに含まれる
3. **Given** 一部リージョンが到達不能な状態, **When** 全リージョン横断検索を実行する, **Then** 到達可能なリージョンの結果が部分結果として返却され、到達不能リージョンがエラー情報に含まれる

---

### Edge Cases

- 検索条件に一致するリソースが0件の場合、空のリソースリスト（`total_count: 0`）が返却されるか？
- 依存関係マップで循環参照（例: SecurityGroup相互参照）が存在する場合、無限ループにならないか？
- 非常に大規模なテナント（数万リソース）でページネーションが正しく動作するか？
- Audit Log APIの保持期間がデフォルト（90日）からカスタマイズされている場合、適切に処理されるか？
- コンパートメントが削除済み（DELETED状態）の場合でも、そのコンパートメント内のリソースはデフォルトで検索結果に含まれる（lifecycle_statesフィルタで除外可能）
- 依存関係マップの探索深度を0に設定した場合は起点ノードのみ返却し、最大値（10）を超える値が指定された場合は10にキャップする

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: システムはOCIテナント内の全サブスクライブ済みリージョンを横断してリソースを検索できること
- **FR-002**: システムはコンパートメント階層を横断してリソースを検索できること（未指定時はテナントルート配下全体）
- **FR-003**: システムはリソースタイプ、タグ、ライフサイクル状態、リージョンによるフィルタリングを提供すること。デフォルトでは全ライフサイクル状態（TERMINATED/DELETED含む）を返却し、`lifecycle_states`フィルタで絞り込み可能とすること
- **FR-004**: システムは検索結果をページネーション対応で返却し、大規模テナントでも完全な結果を保証すること
- **FR-005**: システムはリソース間の依存関係をノード・エッジのグラフ構造として生成できること。クロスコンパートメント・クロスリージョンのエッジを含むが、境界外ノードは参照情報（OCID・名前・タイプ）のみとすること
- **FR-006**: システムは以下の依存関係タイプを解析できること: Instance→Subnet（attached_to）、Instance→BlockVolume/BootVolume（uses）、LB→BackendSet（contains）、BackendSet→Instance（routes_to）、Subnet→VCN（belongs_to）、Subnet→SecurityList/RouteTable（governed_by）、DbSystem→Subnet（attached_to）、OkeCluster→VCN（uses）、OkeNodePool→Subnet（attached_to）
- **FR-007**: システムは依存関係マップの探索深度を制御できること（デフォルト: 3、最大: 10）
- **FR-008**: システムはリソース作成者をタグ（`freeform_tags.created_by` / `defined_tags.*.CreatedBy`）から特定できること
- **FR-009**: システムはタグが存在しない場合、Audit Logの`CreateXxx`イベントから作成者を特定できること
- **FR-010**: システムはタグ・Audit Logいずれでも作成者を特定できない場合、`unresolved`として理由とともに返却すること
- **FR-011**: システムは全操作が読み取り専用であること。リソースの作成・変更・削除は一切行わないこと
- **FR-012**: システムはA2Aプロトコル経由で他エージェント（ORCH、ENV、TA、CQ）からスキルを呼び出し可能であること
- **FR-013**: システムはAPIレート制限（429）に対してexponential backoff（最大3回）でリトライすること
- **FR-014**: システムは認証エラー（401/403）時にTaskを `failed` に遷移し、エラー詳細をArtifactに含めること
- **FR-015**: システムはリージョン到達不能時に到達可能なリージョンの部分結果を返却し、到達不能リージョンをエラー情報に含めること
- **FR-016**: システムは検索結果・依存関係マップを実行ごとに履歴として保持すること。同日の重複実行は最新結果のみ保持し、過去の結果と比較可能な形式で蓄積すること
- **FR-017**: システムはORCHから伝搬されたW3C traceparentを使用してトレーシングを実施すること

### Key Entities

- **Resource**: OCIテナント内の管理対象リソース。OCID、名前、リソースタイプ、コンパートメント、リージョン、ライフサイクル状態、タグ、作成日時を持つ
- **DependencyMap**: リソース間の依存関係を表すグラフ構造。ノード（リソース）とエッジ（関係性）で構成される
- **Edge**: 2つのリソース間の関係性。ソース、ターゲット、関係タイプ（attached_to、uses、contains、routes_to、belongs_to、governed_by）を持つ
- **Creator**: リソースの作成者情報。特定元（タグまたはAudit Log）と作成日時を含む
- **Artifact**: スキルの出力結果。タイプ（resource_list、dependency_map）、バージョン、エージェントID、データを含む

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 全サブスクライブ済みリージョン・コンパートメントのリソースを漏れなく一覧化でき、手動棚卸しと比較して100%のカバレッジを達成する
- **SC-002**: リソース検索が大規模テナント（1万リソース以上）でも10分以内に完了する
- **SC-003**: 依存関係マップが仕様定義の全10種類の関係タイプを正しく解析し、既知の構成と照合して95%以上の精度を達成する
- **SC-004**: タグ付きリソースの作成者特定が100%の精度で動作し、Audit Log範囲内のタグなしリソースでも90%以上の特定率を達成する
- **SC-005**: 他エージェント（ENV、TA、CQ）からのスキル呼び出しが正常に処理され、適切な形式のレスポンスが返却される
- **SC-006**: APIレート制限発生時のリトライにより、一時的なスロットリングが原因の検索失敗が発生しない
- **SC-007**: 検索結果と依存関係マップの履歴が13ヶ月以上保持され、過去データとの比較（トレンド分析）が可能である

## Assumptions

- OCI IAMポリシーにより、RIエージェントのDynamic Groupにテナント全体の読み取り権限およびAudit Log読み取り権限が付与されている
- Instance Principal または Resource Principal による認証が設定済みである
- Audit Logのデフォルト保持期間は90日とし、カスタマイズされた保持期間にも対応する
- 依存関係マップの探索深度のデフォルト値は3で、呼び出し側が変更可能
- 共有データストアが利用可能で、検索結果・依存関係マップの履歴保持に使用される
- A2Aプロトコルの基盤（エージェント間通信、Agent Card配信）は別途整備されている
