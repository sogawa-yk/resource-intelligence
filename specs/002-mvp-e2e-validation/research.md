# Research: MVP判定基準E2Eバリデーション

**Date**: 2026-03-25
**Branch**: `002-mvp-e2e-validation`

## 調査1: 全リソース検索タイムアウトの根本原因

### Decision
リソースタイプ未指定時に主要リソースタイプに限定するフォールバックをapp.py側で実装する。

### Rationale
- 前回テストで「全リソースを一覧して」系のクエリが7件失敗（A01, B01, B10, B11, B12, B14, B18）
- 失敗パターン: 全リージョン×全リソースタイプの検索 → 数千件取得 → タイムアウト → Podクラッシュ → ウェルカムメッセージ再表示
- OCI Resource Search APIはリソースタイプ未指定で全タイプを検索する仕様
- テナント全体で数千件のリソースが存在するため、全取得は現実的でない
- GenAIがresource_searchと判定し、resource_typesが空の場合にapp.py側で主要タイプ（Instance, Vcn, Subnet, LoadBalancer, DbSystem, Cluster）にフォールバックする

### Alternatives Considered
1. **GenAIプロンプト改善のみ**: GenAIに「全リソース」の場合でもタイプを推定させる → 不安定（LLMの出力制御は確実でない）
2. **検索結果の上限設定**: 各リージョン1000件まで → 根本解決にならない（全タイプ検索は依然遅い）
3. **タイムアウト設定**: リージョン別60秒タイムアウト → 部分結果は返せるが、全リソース検索自体が遅い問題は残る

## 調査2: 連続クエリ中のPod不安定性

### Decision
deployment.yamlのメモリリミットを512Mi→1Giに引き上げ、リクエストも256Mi→512Miに引き上げる。

### Rationale
- カテゴリF（連続クエリ）で4件失敗（F05, F06, F09, F14）
- F05（39s）で「検索中...」停止 → F06以降でウェルカムメッセージ返却
- パターン: 検索結果がメモリに蓄積 → Pod OOM → 再起動 → ウェルカムメッセージ
- 特にF05は「ap-tokyo-1のリソース」（タイプ未指定）で1119件の結果を返す重いクエリ
- メモリ不足によるPodクラッシュの可能性が高い
- メモリリミット引き上げ + 全リソース検索のフォールバック（調査1の修正）の組み合わせで解決見込み

### Alternatives Considered
1. **明示的なGC実行**: resource_search完了後にgc.collect() → Pythonの標準GCは通常十分、根本原因がOOMなら効果薄
2. **Podレプリカ数増加**: 2レプリカに → Chainlitはステートフルセッションのためレプリカ増加の効果が限定的
3. **結果のストリーミング**: 大量結果をChainlitストリーミングで返す → 大幅な実装変更が必要

## 調査3: 表記揺れ（ロードバランサー問題）

### Decision
GenAIのリソースタイプマッピングに長音あり/なしの両方を含める。app.py側でresource_typesの正規化は不要（GenAIが正しくマッピングすれば十分）。

### Rationale
- B19「ロードバランサーの一覧」がTIMEOUT
- 「ロードバランサ」（A05, A14等）は正常動作
- 「ロードバランサー」（長音あり）でGenAIが正しくLoadBalancerにマッピングできない可能性
- GenAIプロンプトに長音ありの例を追加するのが最小限の変更

### Alternatives Considered
1. **app.py側の正規化フィルター**: ユーザー入力の前処理 → GenAIの入力を改変すると他の意図解析に悪影響
2. **リソースタイプ別名マッピングテーブル**: 大掛かりすぎる

## 調査4: Playwright MCP テスト実行方式

### Decision
Playwright MCPツール（mcp__playwright__*）を使用し、ブラウザ操作でOKE上のChainlit UIをテスト。結果はplaywright/002-mvp-e2e-validation/に保存。

### Rationale
- ユーザー指定の実行方式
- Playwright MCPはブラウザのナビゲーション、クリック、テキスト入力、スクリーンショット取得が可能
- 既存のplaywright_e2e.pyスクリプトは参照用（テストケース定義・判定基準）として活用
- 実際のテスト実行はPlaywright MCPのブラウザ操作で手動的に実施
- 各テストごとにスクリーンショットを撮影し、結果をマークダウンレポートにまとめる

### Alternatives Considered
1. **既存スクリプト実行**: playwright_e2e.pyをそのまま実行 → ユーザーがPlaywright MCPを指定
2. **pytest + playwright**: pytest-playwrightで実行 → 追加依存が必要、MCPの方が直感的
