# スキルAPIコントラクト

**ブランチ**: `001-oci-resource-intelligence`
**作成日**: 2026-03-24

---

## resource-search スキル

### 入力

```json
{
  "compartment_ocid": "ocid1.compartment.oc1..xxx",
  "resource_types": ["Instance", "Vcn", "Subnet"],
  "tag_filters": {"project": "alpha"},
  "regions": ["ap-tokyo-1"],
  "lifecycle_states": ["RUNNING", "STOPPED"]
}
```

全パラメータ任意。未指定時はテナント全体・全タイプ・全リージョン・全状態。

### 出力

```json
{
  "artifact_type": "resource_list",
  "version": "1.0",
  "agent_id": "RI",
  "created_at": "2026-03-24T10:00:00Z",
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
          "defined": {},
          "freeform": {"project": "alpha"}
        },
        "time_created": "2025-06-15T10:00:00Z"
      }
    ],
    "errors": []
  }
}
```

### エラー

`data.errors` に部分エラー情報を含む:

```json
{
  "errors": [
    {
      "region": "us-ashburn-1",
      "error_type": "connection_timeout",
      "message": "リージョンus-ashburn-1に接続できませんでした"
    }
  ]
}
```

---

## dependency-map スキル

### 入力

```json
{
  "root_ocid": "ocid1.instance.oc1.ap-tokyo-1.xxx",
  "depth": 3,
  "resource_types": ["Instance", "Vcn", "Subnet"]
}
```

`root_ocid` のみ必須。`depth` デフォルト3（最大10）。`resource_types` 未指定時は全タイプ。

### 出力

```json
{
  "artifact_type": "dependency_map",
  "version": "1.0",
  "agent_id": "RI",
  "created_at": "2026-03-24T10:00:00Z",
  "data": {
    "root_ocid": "ocid1.instance.oc1.ap-tokyo-1.xxx",
    "depth": 3,
    "nodes": [
      {
        "ocid": "ocid1.instance.oc1.ap-tokyo-1.xxx",
        "name": "web-server-01",
        "resource_type": "Instance",
        "region": "ap-tokyo-1",
        "compartment_name": "production",
        "lifecycle_state": "RUNNING",
        "is_external": false
      },
      {
        "ocid": "ocid1.vcn.oc1.ap-osaka-1.yyy",
        "name": "peered-vcn",
        "resource_type": "Vcn",
        "region": "ap-osaka-1",
        "compartment_name": "network-other",
        "lifecycle_state": "",
        "is_external": true
      }
    ],
    "edges": [
      {
        "source": "ocid1.instance.oc1.ap-tokyo-1.xxx",
        "target": "ocid1.subnet.oc1.ap-tokyo-1.xxx",
        "relation_type": "attached_to",
        "description": "ComputeインスタンスがSubnetに接続"
      }
    ],
    "errors": []
  }
}
```

### バリデーション

- `depth` が0の場合: 起点ノードのみ返却（エッジなし）
- `depth` が10を超える場合: 10にキャップ
- `root_ocid` が無効な場合: エラーレスポンス
