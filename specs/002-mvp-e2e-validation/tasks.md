# Tasks: MVP判定基準E2Eバリデーション

**Input**: Design documents from `/specs/002-mvp-e2e-validation/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/e2e-testing.md

**Tests**: E2EテストはPlaywright MCPで実施。テスト結果は`playwright/002-mvp-e2e-validation/`に保存。

**Organization**: タスクはMVP判定基準（ユーザーストーリー）ごとに整理。各基準は独立して検証可能。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 並列実行可能（異なるファイル、依存関係なし）
- **[Story]**: 対応するユーザーストーリー（US1〜US4）
- 正確なファイルパスを含む

---

## Phase 1: Setup（テスト環境準備）

**Purpose**: テスト結果ディレクトリ作成、Playwright MCP動作確認

- [x] T001 テスト結果ディレクトリ`playwright/002-mvp-e2e-validation/`を作成
- [x] T002 Playwright MCPでブラウザを起動し、https://ri.sogawa-yk.com/ へのアクセスを確認

---

## Phase 2: Foundational（現状確認 — 全MVP基準のベースライン取得）

**Purpose**: 修正前の現在の状態をPlaywright MCPで確認。各MVP基準の合否ベースラインを取得。

**⚠️ CRITICAL**: この結果をもとに修正対象を特定する

- [x] T003 Playwright MCPで https://ri.sogawa-yk.com/ にアクセスし、ウェルカムメッセージ表示を確認。スクリーンショットを`playwright/002-mvp-e2e-validation/T003-welcome.png`に保存
- [x] T004 Playwright MCPで「インスタンスを表示して」と入力し、リソース検索結果の表示を確認。スクリーンショットを`playwright/002-mvp-e2e-validation/T004-instance-search.png`に保存
- [x] T005 Playwright MCPで「全リソースを一覧して」と入力し、全リソース検索の動作を確認（前回失敗パターン）。スクリーンショットを`playwright/002-mvp-e2e-validation/T005-all-resources.png`に保存
- [x] T006 Playwright MCPで「{OCID}の依存関係を表示」と入力し、依存関係マップの表示を確認。OCIDは`ocid1.instance.oc1.ap-tokyo-1.anxhiljrssl65iqc6t6gig6qsh6gdbfkayn22mqr7q2hdzlo4d5lgn65ptgq`を使用。スクリーンショットを`playwright/002-mvp-e2e-validation/T006-dependency-map.png`に保存
- [x] T007 Playwright MCPで「全リージョンのインスタンスを検索」と入力し、マルチリージョン検索結果を確認。結果に2リージョン以上が含まれることを検証。スクリーンショットを`playwright/002-mvp-e2e-validation/T007-multi-region.png`に保存
- [x] T008 Phase 2のテスト結果を`playwright/002-mvp-e2e-validation/baseline-report.md`にマークダウンで記録。各テストの合否、応答時間、発見された問題を記載

**Checkpoint**: ベースライン取得完了。失敗テストの根本原因を特定し、修正フェーズへ進む

---

## Phase 3: US1 — Chainlit UIからリソース検索を実行し結果が表示される (Priority: P1) 🎯

**Goal**: Chainlit UIでリソース検索を実行し、全テストケースで結果が正しく表示されることを確認。前回失敗した「全リソース検索」問題を修正。

**Independent Test**: 「インスタンスを表示して」「VCNを一覧して」「全リソースを一覧して」を入力し、すべてでリソース一覧テーブルが表示される

### 修正: リソース検索のタイムアウト問題

- [x] T009 [US1] `src/ri_agent/app.py`の`_handle_resource_search`を修正: リソースタイプ未指定時（params.resource_typesが空）に主要リソースタイプ（Instance, Vcn, Subnet, LoadBalancer, DbSystem, Cluster）をデフォルト設定するフォールバック処理を追加
- [x] T010 [US1] `src/ri_agent/oci_client/genai.py`のシステムプロンプトを確認・修正: 「ロードバランサー」（長音あり）を正しくLoadBalancerにマッピングできるよう、リソースタイプ表記揺れの例をプロンプトに追加
- [x] T011 [US1] `k8s/deployment.yaml`を修正: メモリリミットを512Mi→1Gi、メモリリクエストを256Mi→512Miに引き上げ

### デプロイ

- [x] T012 [US1] Dockerイメージをビルド: `docker build -t yyz.ocir.io/orasejapan/ri-agent:latest .`
- [x] T013 [US1] OCIRにプッシュ: `docker push yyz.ocir.io/orasejapan/ri-agent:latest`
- [x] T014 [US1] OKEに再デプロイ: `kubectl apply -f k8s/ -n ri-agent` → Podが正常起動するまで待機

### 修正後テスト

- [x] T015 [US1] Playwright MCPで「インスタンスを表示して」と入力し、Instance一覧テーブルが表示されることを確認。「リソース検索結果」キーワードを検証。スクリーンショットを`playwright/002-mvp-e2e-validation/T015-instance-search-fix.png`に保存
- [x] T016 [US1] Playwright MCPで「VCNを一覧して」と入力し、VCN一覧テーブルが表示されることを確認。スクリーンショットを`playwright/002-mvp-e2e-validation/T016-vcn-search-fix.png`に保存
- [x] T017 [US1] Playwright MCPで「サブネットを表示して」と入力し、Subnet一覧テーブルが表示されることを確認。スクリーンショットを`playwright/002-mvp-e2e-validation/T017-subnet-search-fix.png`に保存
- [x] T018 [US1] Playwright MCPで「ロードバランサを表示」と入力し、LoadBalancer一覧テーブルが表示されることを確認。スクリーンショットを`playwright/002-mvp-e2e-validation/T018-lb-search-fix.png`に保存
- [x] T019 [US1] Playwright MCPで「全リソースを一覧して」と入力し、リソース一覧テーブルが表示されることを確認（前回失敗A01の修正確認）。スクリーンショットを`playwright/002-mvp-e2e-validation/T019-all-resources-fix.png`に保存
- [x] T020 [US1] Playwright MCPで「リソースを全部見せて」と入力し、リソース一覧テーブルが表示されることを確認（前回失敗B01の修正確認）。スクリーンショットを`playwright/002-mvp-e2e-validation/T020-all-resources-nl-fix.png`に保存
- [x] T021 [US1] Playwright MCPで「ロードバランサーの一覧」（長音あり）と入力し、一覧テーブルが表示されることを確認（前回失敗B19の修正確認）。スクリーンショットを`playwright/002-mvp-e2e-validation/T021-lb-longvowel-fix.png`に保存

**Checkpoint**: US1のリソース検索テスト全合格。「全リソース検索」「表記揺れ」問題が解決されている

---

## Phase 4: US2 — Chainlit UIから依存関係マップ生成を実行しノード・エッジが表示される (Priority: P1)

**Goal**: 依存関係マップ生成が正しく動作し、ノード・エッジ付きのASCIIツリーが表示されることを確認。前回テストで全合格（C01-C15）のため、修正不要の見込み。

**Independent Test**: 既知のインスタンスOCIDで依存関係マップを生成し、ノード数2以上・エッジ数1以上のツリーが表示される

### 検証テスト

- [x] T022 [US2] Playwright MCPで「ocid1.instance.oc1.ap-tokyo-1.anxhiljrssl65iqc6t6gig6qsh6gdbfkayn22mqr7q2hdzlo4d5lgn65ptgqの依存関係を表示」と入力し、ノード・エッジ付きツリーが表示されることを確認。「依存関係マップ」「ノード数」「エッジ数」キーワードを検証。スクリーンショットを`playwright/002-mvp-e2e-validation/T022-depmap-default.png`に保存
- [x] T023 [US2] Playwright MCPで「ocid1.instance.oc1.ap-tokyo-1.anxhiljrssl65iqc6t6gig6qsh6gdbfkayn22mqr7q2hdzlo4d5lgn65ptgqの依存関係を深度1で表示」と入力し、深度制御が動作することを確認。スクリーンショットを`playwright/002-mvp-e2e-validation/T023-depmap-depth1.png`に保存
- [x] T024 [US2] Playwright MCPで「ocid1.instance.oc1.ap-tokyo-1.anxhiljrssl65iqc6t6gig6qsh6gdbfkayn22mqr7q2hdzlo4d5lgn65ptgqの依存関係を深度5で表示して」と入力し、深い探索が動作することを確認。スクリーンショットを`playwright/002-mvp-e2e-validation/T024-depmap-depth5.png`に保存
- [x] T025 [US2] Playwright MCPで「ocid1.invalid.xxxの依存関係」と入力し、不正OCIDに対するエラーハンドリングを確認。スクリーンショットを`playwright/002-mvp-e2e-validation/T025-depmap-invalid.png`に保存

**Checkpoint**: US2の依存関係マップテスト全合格。ノード・エッジが正しく表示される

---

## Phase 5: US3 — 全サブスクライブ済みリージョンを横断した検索が動作する (Priority: P1)

**Goal**: マルチリージョン検索が動作し、2リージョン以上の結果が統合表示されることを確認。

**Independent Test**: リージョン指定なしでインスタンス検索を実行し、結果テーブルに2つ以上の異なるリージョン名が含まれる

### 検証テスト

- [x] T026 [US3] Playwright MCPで「全リージョンのインスタンスを検索」と入力し、結果テーブルに複数リージョン（例: ap-tokyo-1, ap-osaka-1等）のリソースが含まれることを確認。スクリーンショットを`playwright/002-mvp-e2e-validation/T026-multi-region-instance.png`に保存
- [x] T027 [US3] Playwright MCPで「ap-tokyo-1のインスタンスを表示」と入力し、東京リージョンのみの結果が表示されることを確認。スクリーンショットを`playwright/002-mvp-e2e-validation/T027-single-region-tokyo.png`に保存
- [x] T028 [US3] Playwright MCPで「ap-osaka-1のリソースを表示」と入力し、大阪リージョンの結果が表示されることを確認。スクリーンショットを`playwright/002-mvp-e2e-validation/T028-single-region-osaka.png`に保存
- [x] T029 [US3] Playwright MCPで「VCNを一覧して」と入力し、結果テーブルに複数リージョンのVCNが含まれることを確認（マルチリージョン統合検索の検証）。スクリーンショットを`playwright/002-mvp-e2e-validation/T029-multi-region-vcn.png`に保存

**Checkpoint**: US3のマルチリージョン検索テスト全合格。2リージョン以上の結果が統合表示される

---

## Phase 6: US4 — OKE上にデプロイして動作する (Priority: P1)

**Goal**: OKE上のアプリケーションが安定動作し、外部URLからアクセス可能であることを確認。連続クエリ安定性テストを含む。

**Independent Test**: https://ri.sogawa-yk.com/ にアクセスしてウェルカムメッセージが表示され、連続5クエリが安定して動作する

### 検証テスト

- [x] T030 [US4] Playwright MCPで https://ri.sogawa-yk.com/ にアクセスし、「Resource Intelligence Agent へようこそ」を含むウェルカムメッセージが表示されることを確認。スクリーンショットを`playwright/002-mvp-e2e-validation/T030-oke-welcome.png`に保存
- [x] T031 [US4] Playwright MCPで連続クエリ安定性テスト: ページリロードなしで「VCNを一覧して」→「サブネットを表示」→「インスタンスを表示して」→「ロードバランサを表示」→「ヘルプ」の5クエリを順次実行し、すべてで正常応答が得られることを確認。各クエリのスクリーンショットを`playwright/002-mvp-e2e-validation/T031-sequential-{1-5}.png`に保存
- [x] T032 [US4] Playwright MCPで連続クエリ安定性テスト（重いクエリ含む）: ページリロードなしで「ap-tokyo-1のリソースを表示」→「ap-osaka-1のインスタンス」→「VCNを一覧して」→「{OCID}の依存関係を表示」→「全リージョンのインスタンスを検索」の5クエリを順次実行し、すべてで正常応答が得られることを確認。各クエリのスクリーンショットを`playwright/002-mvp-e2e-validation/T032-sequential-heavy-{1-5}.png`に保存

**Checkpoint**: US4のOKEデプロイテスト全合格。連続クエリでもPodが安定動作する

---

## Phase 7: Polish & Cross-Cutting Concerns（最終確認・レポート生成）

**Purpose**: 全MVP判定基準の最終確認とレポート生成

- [x] T033 テスト中に修正が必要だった場合: 修正内容を確認し、コードの品質・一貫性をレビュー
- [x] T034 全テスト結果（T003〜T032）を集約し、MVP判定基準別の合否サマリーを含む最終レポートを`playwright/002-mvp-e2e-validation/test-report.md`に生成。以下を含む: (1) テスト実施日時・対象URL、(2) MVP判定基準4項目の合否、(3) 各テストケースの詳細（ID、入力、結果、スクリーンショットリンク）、(4) 修正内容サマリー（該当する場合）、(5) 最終MVP判定
- [x] T035 修正を実施した場合: 変更したファイル一覧とdiffを確認し、テストスクリプト（tests/e2e/）が変更されていないことを検証

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: 依存なし — 即座に開始可能
- **Phase 2 (Foundational)**: Phase 1完了後 — ベースライン取得
- **Phase 3 (US1)**: Phase 2完了後 — 修正が必要な場合はここで実施。修正後にデプロイ
- **Phase 4 (US2)**: Phase 3のデプロイ（T014）完了後 — US1の修正がデプロイされた状態でテスト
- **Phase 5 (US3)**: Phase 3のデプロイ（T014）完了後 — US4と並列実行可能
- **Phase 6 (US4)**: Phase 3のデプロイ（T014）完了後 — US3と並列実行可能
- **Phase 7 (Polish)**: Phase 4, 5, 6すべて完了後

### User Story Dependencies

- **US1 (リソース検索)**: 修正+デプロイが必要 → 他のUSに先行
- **US2 (依存関係マップ)**: US1のデプロイ完了後にテスト（修正不要の見込み）
- **US3 (マルチリージョン)**: US1のデプロイ完了後にテスト（US1の修正が効果を持つ）
- **US4 (OKEデプロイ)**: US1のデプロイ完了後にテスト（メモリ増加の効果を確認）

### Within Each User Story

- 修正タスク → デプロイタスク → テストタスクの順
- テストタスク内は順次実行（ブラウザセッション管理のため）

### Parallel Opportunities

- Phase 4 (US2) と Phase 5 (US3) は並列実行可能（独立したテスト）
- Phase 5 (US3) と Phase 6 (US4) は並列実行可能
- T009, T010, T011 は並列実行可能（異なるファイルの修正）

---

## Parallel Example: Phase 3修正タスク

```bash
# 並列実行可能な修正タスク:
Task T009: "app.pyのリソースタイプフォールバック修正"
Task T010: "genai.pyの表記揺れ対応"
Task T011: "deployment.yamlのメモリリミット引き上げ"
```

---

## Implementation Strategy

### MVP First (US1の修正 → 全US検証)

1. Phase 1 (Setup) 完了
2. Phase 2 (Foundational) 完了 → ベースライン取得
3. Phase 3 (US1) 完了 → 修正適用・デプロイ・テスト
4. **STOP and VALIDATE**: US1のリソース検索が全テスト合格
5. Phase 4-6 (US2-US4) → 残りのMVP基準テスト
6. Phase 7 (Polish) → 最終レポート生成

### 修正→再テストループ

US1テスト（T015-T021）で不合格がある場合:
1. 不合格テストの原因を分析
2. `src/`または`k8s/`を修正（テストスクリプトは変更しない）
3. 再ビルド・再デプロイ
4. 不合格テストを再実行
5. 全合格するまで繰り返し

---

## Notes

- [P] タスク = 異なるファイル、依存関係なし
- [Story] ラベルでMVP判定基準へのトレーサビリティを確保
- 各テストでスクリーンショットを保存（証跡）
- 修正対象: `src/`と`k8s/`のみ。`tests/e2e/`は変更しない
- Playwright MCPのブラウザ操作でテスト実行（既存スクリプトは実行しない）
- OCID: `ocid1.instance.oc1.ap-tokyo-1.anxhiljrssl65iqc6t6gig6qsh6gdbfkayn22mqr7q2hdzlo4d5lgn65ptgq`
