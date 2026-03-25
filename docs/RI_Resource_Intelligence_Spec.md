# RI: Resource Intelligence Agent 仕様書

| 項目 | 内容 |
|------|------|
| ドキュメントID | SPEC-RI-v1.0 |
| 対象エージェント | Resource Intelligence Agent (RI) |
| 開発フェーズ | Phase 1 |
| 自律度 | Read Only |
| 最終更新 | 2026-03-22 |

---

## 1. エージェント概要

### 1.1 役割

OCIテナント全体のリソース検索・一覧化・依存関係マップの生成・作成者特定を行う。リージョン・コンパートメント横断でリソースの構成情報を提供する読み取り専用エージェント。

### 1.2 Agent Card

```json
{
  "name": "Resource Intelligence",
  "description": "OCIテナント全体のリソース検索・一覧化・依存関係マップの生成を行う。リージョン・コンパートメント横断でリソースの構成情報を提供する。",
  "url": "https://<ri-endpoint>/.well-known/agent-card.json",
  "capabilities": {
    "streaming": true,
    "pushNotifications": false
  },
  "skills": [
    {
      "id": "resource-search",
      "name": "Resource Search",
      "description": "リージョン・コンパートメントを横断してリソースを検索・一覧化する"
    },
    {
      "id": "dependency-map",
      "name": "Dependency Map",
      "description": "リソース間の依存関係（Compute→VCN/Subnet, Block Volume→Compute, LB→Backend Set等）を解析し、構造化されたマップを生成する"
    },
    {
      "id": "resource-creator",
      "name": "Resource Creator Lookup",
      "description": "リソースの作成者をタグまたはAudit Logから特定する"
    }
  ],
  "defaultInputModes": ["text"],
  "defaultOutputModes": ["text", "data"]
}
```

### 1.3 利用シナリオ

| シナリオ | 利用パターン | 呼び出し元 |
|----------|-------------|------------|
| S1 棚卸し | オーケストレーターから委託（全リソース一覧、依存関係、作成者特定） | ORCH |
| S2-B キャッチアップ | ENVエージェントからピアツーピア（構成情報参照） | ENV |
| S4 障害分析 | TAエージェントからピアツーピア（システム構成把握） | TA |

---

## 2. スキル詳細仕様

### 2.1 resource-search（リソース検索）

#### 目的

リージョン・コンパートメントを横断してOCIリソースを検索・一覧化する。

#### Task入出力コントラクト

**Input（Message）**:

| パラメータ | 型 | 必須 | 説明 |
|------------|------|------|------|
| compartment_ocid | string | いいえ | 検索対象コンパートメント。未指定時はテナントルート配下全体 |
| resource_types | string[] | いいえ | 検索対象のリソースタイプ（例: `["Instance", "Vcn", "Subnet"]`）。未指定時は全タイプ |
| tag_filters | object | いいえ | タグによるフィルタ条件（例: `{"project": "alpha"}`） |
| regions | string[] | いいえ | 検索対象リージョン。未指定時は全サブスクライブ済みリージョン |
| lifecycle_states | string[] | いいえ | ライフサイクル状態フィルタ（例: `["RUNNING", "STOPPED"]`） |

**Output（Artifact）**:

```json
{
  "artifact_type": "resource_list",
  "version": "1.0",
  "agent_id": "RI",
  "created_at": "<ISO 8601>",
  "data": {
    "total_count": 150,
    "resources": [
      {
        "ocid": "ocid1.instance.oc1.ap-tokyo-1.xxx",
        "name": "web-server-01",
        "resource_type": "Instance",
        "compartment_ocid": "ocid1.compartment.oc1..xxx",
        "compartment_name": "production",
        "region": "ap-tokyo-1",
        "lifecycle_state": "RUNNING",
        "tags": {
          "defined": { "Operations": { "CostCenter": "42" } },
          "freeform": { "project": "alpha", "created_by": "user@example.com" }
        },
        "time_created": "2025-06-15T10:00:00Z"
      }
    ]
  }
}
```

#### 対応する要件

| 要件ID | 要件 |
|--------|------|
| S1-F03 | リージョン・コンパートメントを横断して全リソースを一覧化できること |

---

### 2.2 dependency-map（依存関係マップ）

#### 目的

リソース間の依存関係を解析し、構造化されたグラフ（ノード・エッジ）として生成する。

#### Task入出力コントラクト

**Input（Message）**:

| パラメータ | 型 | 必須 | 説明 |
|------------|------|------|------|
| root_ocid | string | はい | 起点リソースOCID、またはコンパートメントOCID |
| depth | int | いいえ | 探索深度（デフォルト: 3） |
| resource_types | string[] | いいえ | マップに含めるリソースタイプの制限 |

**Output（Artifact）**:

```json
{
  "artifact_type": "dependency_map",
  "version": "1.0",
  "agent_id": "RI",
  "created_at": "<ISO 8601>",
  "data": {
    "nodes": [
      {
        "ocid": "ocid1.instance.oc1.ap-tokyo-1.xxx",
        "name": "web-server-01",
        "resource_type": "Instance",
        "region": "ap-tokyo-1",
        "compartment_name": "production",
        "lifecycle_state": "RUNNING"
      },
      {
        "ocid": "ocid1.vcn.oc1.ap-tokyo-1.xxx",
        "name": "main-vcn",
        "resource_type": "Vcn",
        "region": "ap-tokyo-1",
        "compartment_name": "network",
        "lifecycle_state": "AVAILABLE"
      }
    ],
    "edges": [
      {
        "source": "ocid1.instance.oc1.ap-tokyo-1.xxx",
        "target": "ocid1.subnet.oc1.ap-tokyo-1.xxx",
        "relation_type": "attached_to",
        "description": "ComputeインスタンスがSubnetに接続"
      }
    ]
  }
}
```

#### 依存関係の解析対象

| ソース | ターゲット | 関係タイプ | 説明 |
|--------|-----------|------------|------|
| Instance | Subnet | attached_to | ComputeのVNIC接続先 |
| Instance | BlockVolume | uses | アタッチされたBlock Volume |
| Instance | BootVolume | uses | ブートボリューム |
| LoadBalancer | BackendSet | contains | LBのバックエンド構成 |
| BackendSet | Instance | routes_to | バックエンドサーバー |
| Subnet | Vcn | belongs_to | サブネットの所属VCN |
| Subnet | SecurityList | governed_by | 適用されたセキュリティリスト |
| Subnet | RouteTable | governed_by | 適用されたルートテーブル |
| DbSystem | Subnet | attached_to | DBシステムの接続先 |
| OkeCluster | Vcn | uses | OKEクラスタのVCN |
| OkeNodePool | Subnet | attached_to | ノードプールの配置先 |

#### 対応する要件

| 要件ID | 要件 |
|--------|------|
| S1-F04 | リソース間の依存関係・関連性を可視化できること |
| S4-F02 | 対象システムのリソース構成情報を自動取得できること |
| S4-F03 | ネットワーク構成を把握できること |
| LINK-03 | 棚卸しで構築したリソース依存関係マップを障害分析時に再利用 |

---

### 2.3 resource-creator（作成者特定）

#### 目的

リソースの作成者をタグまたはAudit Logから特定する。

#### Task入出力コントラクト

**Input（Message）**:

| パラメータ | 型 | 必須 | 説明 |
|------------|------|------|------|
| resource_ocids | string[] | はい | 作成者を特定したいリソースのOCIDリスト |

**Output（Artifact）**:

```json
{
  "artifact_type": "resource_list",
  "version": "1.0",
  "agent_id": "RI",
  "created_at": "<ISO 8601>",
  "data": {
    "creators": [
      {
        "resource_ocid": "ocid1.instance.oc1.ap-tokyo-1.xxx",
        "resource_name": "web-server-01",
        "creator_user": "user@example.com",
        "creator_source": "freeform_tag",
        "created_at": "2025-06-15T10:00:00Z"
      },
      {
        "resource_ocid": "ocid1.vcn.oc1.ap-tokyo-1.xxx",
        "resource_name": "main-vcn",
        "creator_user": "admin@example.com",
        "creator_source": "audit_log",
        "created_at": "2025-01-10T08:30:00Z"
      }
    ],
    "unresolved": [
      {
        "resource_ocid": "ocid1.subnet.oc1.ap-tokyo-1.xxx",
        "reason": "Audit log retention exceeded and no creator tag present"
      }
    ]
  }
}
```

#### 作成者特定ロジック

1. **タグ確認**: `freeform_tags.created_by` または `defined_tags.*.CreatedBy` を確認
2. **Audit Log照会**: タグが存在しない場合、Audit APIで該当リソースの `CreateXxx` イベントを検索
3. **未解決**: いずれでも特定できない場合は `unresolved` に分類し、理由を記載

#### 対応する要件

| 要件ID | 要件 |
|--------|------|
| S1-F05 | 各リソースの作成者を取得し、対応者を特定できること |

---

## 3. MCPツール（内部）

本エージェントが使用するOCI APIとMCPツールの一覧。

| MCPツール | OCI API | 用途 |
|-----------|---------|------|
| resource-search-query | OCI Resource Search API | テナント横断リソース検索 |
| list-instances | Core Services API (Compute) | インスタンス詳細取得 |
| list-vcns | Core Services API (VCN) | VCN情報取得 |
| list-subnets | Core Services API (Networking) | サブネット情報取得 |
| list-block-volumes | Core Services API (Block Volume) | ブロックボリューム情報取得 |
| list-load-balancers | Core Services API (Load Balancer) | LB情報取得 |
| list-vnic-attachments | Core Services API (Compute) | VNIC接続情報取得 |
| list-security-lists | Core Services API (Networking) | セキュリティリスト取得 |
| list-route-tables | Core Services API (Networking) | ルートテーブル取得 |
| list-audit-events | Audit API | 作成者特定用Auditイベント検索 |

---

## 4. ピアツーピア連携仕様

### 4.1 ENVエージェントからの呼び出し（S2-B）

**ユースケース**: 新メンバーが環境について質問した際、ENVがリソース構成情報を必要とする場合

**呼び出しパターン**:
- ENV → RI.resource-search（コンパートメント内のリソース一覧取得）
- ENV → RI.dependency-map（特定リソースの依存関係取得）

### 4.2 TAエージェントからの呼び出し（S4）

**ユースケース**: 障害分析時にシステム構成を把握する必要がある場合

**呼び出しパターン**:
- TA → RI.dependency-map（障害対象リソースの依存関係取得）
- TA → RI.resource-search（関連リソースの情報取得）

### 4.3 CQエージェントからの呼び出し（S1）

**ユースケース**: コスト要因のリソース詳細を取得する場合

**呼び出しパターン**:
- CQ → RI.resource-search（コスト高リソースの詳細情報取得）

---

## 5. 非機能要件

| ID | 要件 | 備考 |
|----|------|------|
| RI-NF01 | すべての操作はRead Only。リソースの作成・変更・削除は一切行わない | S1-NF01準拠 |
| RI-NF02 | 全サブスクライブ済みリージョンを対象に検索可能であること | |
| RI-NF03 | リソース検索結果はページネーションに対応し、大規模テナントでも完全な結果を返すこと | |
| RI-NF04 | Audit Logの検索はAPIの保持期間（デフォルト90日）の制約を受ける。保持期間を超えた検索は `unresolved` として返す | |

---

## 6. セキュリティ要件

| ID | 要件 |
|----|------|
| SEC-01 | 最小権限の原則に基づいた専用認証情報（Instance Principal / Resource Principal）を使用 |
| SEC-03 | エージェントの操作ログは監査証跡として記録 |
| SEC-05 | Read Only権限のみ。リソースのmutate系APIは一切呼び出さない |

### 6.1 必要なOCI IAMポリシー例

```
Allow dynamic-group ri-agent-dg to read all-resources in tenancy
Allow dynamic-group ri-agent-dg to read audit-events in tenancy
```

---

## 7. エラーハンドリング

| エラー種別 | 処理 |
|------------|------|
| OCI APIレート制限（429） | exponential backoffでリトライ（最大3回） |
| OCI API認証エラー（401/403） | Taskを `failed` に遷移。エラー詳細をArtifactに含める |
| リージョン到達不能 | 到達可能なリージョンの結果を部分結果として返し、到達不能リージョンをエラー情報に含める |
| ステップ数ガードレール超過 | 即座にTaskを `failed` に遷移。部分結果をArtifactに含める |

---

## 8. データ保持

| ID | 要件 |
|----|------|
| DATA-01 | リソース検索結果・依存関係マップは履歴として保持 |
| DATA-02 | 保持期間は最低13ヶ月（S1-NF03準拠） |
| DATA-03 | 過去の結果と比較可能な形式で蓄積（トレンド分析対応） |
| DATA-04 | 共有データストアに格納し、他エージェントから参照可能 |

---

## 9. Observability

| 項目 | 仕様 |
|------|------|
| トレーシング | ORCHから伝搬されたW3C traceparentを使用。各MCP呼び出しをスパンとして記録 |
| ロギング | API呼び出し、検索条件、結果件数をログに記録 |
| メトリクス | 検索実行時間、結果件数、APIエラー率を収集 |

---

## 10. 外部依存

| 依存先 | 種別 | 備考 |
|--------|------|------|
| OCI Resource Search API | MCP | リソース検索 |
| OCI Core Services API | MCP | リソース詳細取得 |
| OCI Audit API | MCP | 作成者特定 |
| ORCH Agent | A2A | Task受信元 |
| 共有データストア | 内部 | 結果履歴保持 |
