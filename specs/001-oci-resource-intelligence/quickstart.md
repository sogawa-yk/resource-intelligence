# クイックスタートガイド

**ブランチ**: `001-oci-resource-intelligence`
**作成日**: 2026-03-24

---

## 前提条件

- Python 3.11以上
- Docker
- kubectl（OKEクラスタ接続済み）
- OCIRリポジトリ（手動作成が必要 → イメージ名は実装時に案内）
- OCI IAMポリシー設定済み:
  ```
  Allow dynamic-group ri-agent-dg to read all-resources in tenancy
  Allow dynamic-group ri-agent-dg to read audit-events in tenancy
  ```

## ローカル開発

```bash
# リポジトリクローン
git clone <repo-url> && cd resource-intelligence
git checkout 001-oci-resource-intelligence

# 仮想環境セットアップ
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# ローカル実行（開発用）
chainlit run src/ri_agent/app.py --port 8000
```

## OKEデプロイ

```bash
# 1. Dockerイメージビルド
docker build -t <ocir-region>.ocir.io/<namespace>/ri-agent:latest .

# 2. OCIRにプッシュ（リポジトリの手動作成が必要）
docker push <ocir-region>.ocir.io/<namespace>/ri-agent:latest

# 3. Kubernetesにデプロイ
kubectl apply -f k8s/

# 4. 動作確認
kubectl get pods -l app=ri-agent
kubectl logs -f deployment/ri-agent
```

## プロジェクト構造

```
resource-intelligence/
├── src/
│   └── ri_agent/
│       ├── __init__.py
│       ├── app.py                 # Chainlitアプリケーションエントリポイント
│       ├── config.py              # 設定管理
│       ├── models/                # Pydanticデータモデル
│       │   ├── __init__.py
│       │   ├── resource.py        # Resource, Tags
│       │   ├── dependency.py      # DependencyMap, Node, Edge
│       │   └── artifact.py        # Artifact, SearchRequest, DependencyMapRequest
│       ├── services/              # ビジネスロジック
│       │   ├── __init__.py
│       │   ├── resource_search.py # リソース検索サービス
│       │   └── dependency_map.py  # 依存関係マップサービス
│       ├── oci_client/            # OCI SDK ラッパー
│       │   ├── __init__.py
│       │   ├── base.py            # 共通クライアント設定（リトライ、認証）
│       │   ├── search.py          # Resource Search API クライアント
│       │   ├── compute.py         # Compute API クライアント
│       │   ├── network.py         # VCN/Networking API クライアント
│       │   ├── loadbalancer.py    # Load Balancer API クライアント
│       │   ├── database.py        # Database API クライアント
│       │   └── container.py       # Container Engine API クライアント
│       └── storage/               # 履歴保存
│           ├── __init__.py
│           ├── base.py            # ストレージ抽象インターフェース
│           └── local_json.py      # ローカルJSONファイル実装（MVP）
├── tests/
│   ├── unit/                      # 単体テスト
│   ├── integration/               # 結合テスト
│   ├── performance/               # パフォーマンステスト
│   └── e2e/                       # E2Eテスト
├── k8s/
│   ├── namespace.yaml             # 名前空間定義
│   ├── deployment.yaml            # Deploymentマニフェスト
│   ├── service.yaml               # Serviceマニフェスト
│   └── pvc.yaml                   # PersistentVolumeClaim（履歴保存用）
├── Dockerfile
├── requirements.txt
├── pyproject.toml
└── docs/
    └── development-phases.md      # 開発フェーズ定義
```

## テスト実行

```bash
# ローカル単体テスト（開発中）
pytest tests/unit/ -v

# Kubernetes環境テスト（マージ前必須）
kubectl apply -f k8s/test/
kubectl exec -it deploy/ri-agent-test -- pytest tests/ -v
```
