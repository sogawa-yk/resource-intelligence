# データモデル

**ブランチ**: `001-oci-resource-intelligence`
**作成日**: 2026-03-24

---

## エンティティ一覧

### Resource（リソース）

OCIテナント内の管理対象リソースを表現する。

| フィールド | 型 | 必須 | 説明 |
|------------|------|------|------|
| ocid | string | はい | OCI リソース識別子 |
| name | string | はい | リソース表示名 |
| resource_type | string | はい | リソースタイプ（例: Instance, Vcn, Subnet） |
| compartment_ocid | string | はい | 所属コンパートメントOCID |
| compartment_name | string | はい | 所属コンパートメント表示名 |
| region | string | はい | リージョン識別子（例: ap-tokyo-1） |
| lifecycle_state | string | はい | ライフサイクル状態（RUNNING, STOPPED, TERMINATED等） |
| tags | Tags | はい | タグ情報 |
| time_created | datetime | はい | リソース作成日時（ISO 8601） |

**一意性**: `ocid` がグローバルに一意

---

### Tags（タグ）

リソースに付与されたタグ情報。

| フィールド | 型 | 必須 | 説明 |
|------------|------|------|------|
| defined | dict[str, dict[str, str]] | いいえ | 定義済みタグ（名前空間→キー→値） |
| freeform | dict[str, str] | いいえ | フリーフォームタグ（キー→値） |

---

### DependencyMap（依存関係マップ）

リソース間の依存関係を表すグラフ構造。

| フィールド | 型 | 必須 | 説明 |
|------------|------|------|------|
| root_ocid | string | はい | 探索起点のOCID |
| depth | int | はい | 実行時の探索深度 |
| nodes | list[Node] | はい | グラフのノード一覧 |
| edges | list[Edge] | はい | グラフのエッジ一覧 |

---

### Node（ノード）

依存関係マップ内のノード。リソースの要約情報。

| フィールド | 型 | 必須 | 説明 |
|------------|------|------|------|
| ocid | string | はい | リソースOCID |
| name | string | はい | リソース表示名 |
| resource_type | string | はい | リソースタイプ |
| region | string | はい | リージョン |
| compartment_name | string | はい | コンパートメント名 |
| lifecycle_state | string | はい | ライフサイクル状態 |
| is_external | bool | はい | 境界外参照ノードの場合true |

**備考**: `is_external: true` のノードはOCID・名前・タイプのみ保持し、詳細情報は含まない

---

### Edge（エッジ）

2つのリソース間の依存関係。

| フィールド | 型 | 必須 | 説明 |
|------------|------|------|------|
| source | string | はい | ソースリソースOCID |
| target | string | はい | ターゲットリソースOCID |
| relation_type | RelationType | はい | 関係タイプ |
| description | string | はい | 関係の説明文 |

---

### RelationType（関係タイプ列挙）

| 値 | 説明 | ソース例 | ターゲット例 |
|----|------|----------|-------------|
| attached_to | 接続関係 | Instance, DbSystem, OkeNodePool | Subnet |
| uses | 使用関係 | Instance, OkeCluster | BlockVolume, BootVolume, VCN |
| contains | 包含関係 | LoadBalancer | BackendSet |
| routes_to | ルーティング関係 | BackendSet | Instance |
| belongs_to | 所属関係 | Subnet | VCN |
| governed_by | 適用関係 | Subnet | SecurityList, RouteTable |

---

### Artifact（出力アーティファクト）

スキル実行結果の共通ラッパー。

| フィールド | 型 | 必須 | 説明 |
|------------|------|------|------|
| artifact_type | string | はい | `resource_list` または `dependency_map` |
| version | string | はい | スキーマバージョン（`1.0`） |
| agent_id | string | はい | 常に `RI` |
| created_at | datetime | はい | 生成日時（ISO 8601） |
| data | dict | はい | スキル固有のデータ |

---

### SearchRequest（検索リクエスト）

resource-searchスキルの入力パラメータ。

| フィールド | 型 | 必須 | デフォルト | 説明 |
|------------|------|------|------------|------|
| compartment_ocid | string | いいえ | テナントルート | 検索対象コンパートメント |
| resource_types | list[str] | いいえ | 全タイプ | リソースタイプフィルタ |
| tag_filters | dict[str, str] | いいえ | なし | タグフィルタ条件 |
| regions | list[str] | いいえ | 全リージョン | 検索対象リージョン |
| lifecycle_states | list[str] | いいえ | 全状態 | ライフサイクル状態フィルタ |

---

### DependencyMapRequest（マップ生成リクエスト）

dependency-mapスキルの入力パラメータ。

| フィールド | 型 | 必須 | デフォルト | 説明 |
|------------|------|------|------------|------|
| root_ocid | string | はい | - | 起点リソースまたはコンパートメントのOCID |
| depth | int | いいえ | 3 | 探索深度（最小0、最大10） |
| resource_types | list[str] | いいえ | 全タイプ | マップに含めるリソースタイプの制限 |

---

## 履歴ストレージ構造（MVP: ローカルJSON）

```
/data/history/
├── resource_search/
│   ├── 2026-03-24.json    # 同日最新のみ保持
│   └── 2026-03-25.json
└── dependency_map/
    ├── 2026-03-24.json
    └── 2026-03-25.json
```

各JSONファイルはArtifact形式で保存される。
