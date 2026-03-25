# Chainlit UI コントラクト

**ブランチ**: `001-oci-resource-intelligence`
**作成日**: 2026-03-24

---

## チャットインターフェース仕様

### ユーザー入力パターン

RIエージェントはChainlitチャットUIを通じて、以下のパターンの自然言語入力を受け付ける。

#### リソース検索

| 入力例 | 解釈 |
|--------|------|
| 「全リソースを一覧して」 | フィルタなし全リソース検索 |
| 「ap-tokyo-1のインスタンスを表示」 | リージョン: ap-tokyo-1、タイプ: Instance |
| 「productionコンパートメントの稼働中リソース」 | コンパートメント指定、状態: RUNNING |
| 「project=alphaタグのリソースを検索」 | タグフィルタ: project=alpha |

#### 依存関係マップ

| 入力例 | 解釈 |
|--------|------|
| 「web-server-01の依存関係を表示」 | リソース名から起点を特定しマップ生成 |
| 「ocid1.instance.oc1...の依存関係マップ」 | OCID直接指定でマップ生成 |
| 「productionの依存関係を深度2で表示」 | コンパートメント起点、depth=2 |

### レスポンス形式

#### リソース検索結果

```
🔍 リソース検索結果（全150件）

| 名前 | タイプ | リージョン | 状態 | コンパートメント |
|------|--------|-----------|------|-----------------|
| web-server-01 | Instance | ap-tokyo-1 | RUNNING | production |
| main-vcn | Vcn | ap-tokyo-1 | AVAILABLE | network |
| ... | ... | ... | ... | ... |

詳細をJSON形式で表示しますか？
```

#### 依存関係マップ結果

```
🗺️ 依存関係マップ（起点: web-server-01、深度: 3）

ノード数: 8、エッジ数: 7

web-server-01 (Instance)
├── [attached_to] → app-subnet (Subnet)
│   ├── [belongs_to] → main-vcn (Vcn)
│   ├── [governed_by] → default-sl (SecurityList)
│   └── [governed_by] → default-rt (RouteTable)
├── [uses] → boot-vol-01 (BootVolume)
└── [uses] → data-vol-01 (BlockVolume)

詳細をJSON形式で表示しますか？
```

### エラー表示

```
⚠️ 一部のリージョンで検索に失敗しました

成功: ap-tokyo-1, ap-osaka-1（計120件）
失敗: us-ashburn-1（接続タイムアウト）

部分結果を表示しています。
```

---

## Chainlit設定

| 項目 | 値 |
|------|------|
| ポート | 8000 |
| タイトル | Resource Intelligence |
| テーマ | デフォルト |
| ストリーミング | 有効 |
