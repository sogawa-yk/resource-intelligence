# Implementation Plan: OCI Resource Intelligence Agent

**Branch**: `001-oci-resource-intelligence` | **Date**: 2026-03-24 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-oci-resource-intelligence/spec.md`
**スコープ**: MVPフェーズのみ（[開発フェーズ定義](../../docs/development-phases.md)参照）

## Summary

OCIテナント全体のリソース検索・依存関係マップ生成を行う読み取り専用エージェント。Python + Chainlit UIでOKEにデプロイする。MVPではresource-searchとdependency-mapの2スキルを実装し、履歴はローカルJSONファイルで保持する。マルチリージョン並列スキャンにより10分以内の完了を目標とする。

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: chainlit, oci（OCI Python SDK）, pydantic
**Storage**: ローカルJSONファイル（PersistentVolume上。Phase 3でAutonomous Databaseに移行予定）
**Testing**: pytest
**Target Platform**: OKE（Oracle Kubernetes Engine）上のLinuxコンテナ
**Project Type**: Web Service（Chainlit チャットUI）
**Performance Goals**: 全リージョン横断検索を10分以内に完了（1万リソース以上のテナント）
**Constraints**: 読み取り専用操作のみ。Instance Principal認証。OCIRシークレット名: `ocir`
**Scale/Scope**: OCI テナント全体（全リージョン・全コンパートメント、数万リソース規模）

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| 原則 | 状態 | 備考 |
|------|------|------|
| I. 日本語ドキュメント必須 | ✅ 準拠 | 全ドキュメント日本語。コード識別子は英語 |
| II. 包括的テスト戦略 | ✅ 準拠 | 単体・結合・パフォーマンス・E2Eの4レベル計画済み |
| III. Kubernetes環境テスト | ✅ 準拠 | OKEデプロイ後のテスト実行を計画。テスト用名前空間を分離 |
| IV. 可観測性 | ✅ 準拠 | 構造化ログ（structlog）、エラー時トレースID出力。MVP後にメトリクス追加 |
| V. シンプルさ | ✅ 準拠 | 単一プロジェクト構成。ストレージ抽象は最小限（MVP: JSON、将来: ADB） |

**Re-check after Phase 1**: 全原則に準拠。Constitution違反なし。

## Project Structure

### Documentation (this feature)

```text
specs/001-oci-resource-intelligence/
├── plan.md              # 本ファイル
├── research.md          # Phase 0 リサーチ結果
├── data-model.md        # Phase 1 データモデル
├── quickstart.md        # Phase 1 クイックスタート
├── contracts/           # Phase 1 コントラクト
│   ├── chainlit-ui.md   # Chainlit UIコントラクト
│   └── skill-api.md     # スキルAPI入出力コントラクト
└── tasks.md             # Phase 2 タスク一覧（/speckit.tasks で生成）
```

### Source Code (repository root)

```text
src/
└── ri_agent/
    ├── __init__.py
    ├── app.py                     # Chainlitエントリポイント
    ├── config.py                  # 設定管理
    ├── models/                    # Pydanticデータモデル
    │   ├── __init__.py
    │   ├── resource.py            # Resource, Tags
    │   ├── dependency.py          # DependencyMap, Node, Edge, RelationType
    │   └── artifact.py            # Artifact, SearchRequest, DependencyMapRequest
    ├── services/                  # ビジネスロジック
    │   ├── __init__.py
    │   ├── resource_search.py     # リソース検索サービス
    │   └── dependency_map.py      # 依存関係マップサービス
    ├── oci_client/                # OCI SDKラッパー
    │   ├── __init__.py
    │   ├── base.py                # 共通設定（リトライ、Instance Principal認証）
    │   ├── search.py              # Resource Search APIクライアント
    │   ├── compute.py             # Compute APIクライアント
    │   ├── network.py             # VCN/Networking APIクライアント
    │   ├── loadbalancer.py        # Load Balancer APIクライアント
    │   ├── database.py            # Database APIクライアント
    │   └── container.py           # Container Engine APIクライアント
    └── storage/                   # 履歴保存
        ├── __init__.py
        ├── base.py                # ストレージ抽象インターフェース
        └── local_json.py          # ローカルJSON実装（MVP）

tests/
├── unit/                          # 単体テスト（モック使用）
├── integration/                   # 結合テスト（OCI API連携）
├── performance/                   # パフォーマンステスト
└── e2e/                           # E2Eテスト（Chainlit経由）

k8s/
├── namespace.yaml                 # ri-agent名前空間
├── deployment.yaml                # Deployment（imagePullSecrets: ocir）
├── service.yaml                   # Service（port: 8000）
└── pvc.yaml                       # PersistentVolumeClaim（履歴保存用）

Dockerfile
requirements.txt
pyproject.toml
```

**Structure Decision**: 単一プロジェクト構成を採用。ChainlitがフロントエンドとバックエンドをPython単一プロセスで統合するため、分離は不要（Constitution V: シンプルさ）。

## Complexity Tracking

Constitution違反なし。複雑さの正当化は不要。
