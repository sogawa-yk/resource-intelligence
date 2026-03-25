# Playwright E2E Test Report
**Date**: 2026-03-25 12:14:25
**URL**: https://ri.sogawa-yk.com/
**Total**: 100 tests | Pass: 88 | Fail: 12

## Summary by Category
| Category | Tests | Pass | Fail |
|----------|-------|------|------|
| A: Resource Search - Type Specific | 20 | 19 | 1 |
| B: Resource Search - Natural Language | 20 | 13 | 7 |
| C: Dependency Map | 15 | 15 | 0 |
| D: Help & General | 15 | 15 | 0 |
| E: Edge Cases & Error Handling | 15 | 15 | 0 |
| F: Continuous Sequential | 15 | 11 | 4 |

## Test Results
### A: Resource Search - Type Specific
| ID | Input | Expected | Result | Time | Screenshot |
|----|-------|----------|--------|------|------------|
| A01 | 全リソースを一覧して | resource_search | FAIL: Resource Intelligence Agent へようこそ！ 自然言語でOCIリソースについて質問できます。例: 「全リソースを一覧して」 「ap-tokyo-1のインスタンスを表示」 「pr... | 121.46s | [A01.png](./A01.png) |
| A02 | ap-tokyo-1のインスタンスを表示して | resource_search | PASS: 🔍 リソースを検索中... 🔍 リソース検索結果（全4件） 名前	タイプ	リージョン	状態	コンパートメント 一時的なビルド用インスタンス	Instance	ap-tokyo-1	Stopped	yu... | 11.09s | [A02.png](./A02.png) |
| A03 | VCNを一覧して | resource_search | PASS: 🔍 リソースを検索中... 🔍 リソース検索結果（全55件） 名前	タイプ	リージョン	状態	コンパートメント vcn7	Vcn	us-chicago-1	AVAILABLE	 ai-apps	Vcn... | 13.1s | [A03.png](./A03.png) |
| A04 | サブネットを表示して | resource_search | PASS: 🔍 リソースを検索中... 🔍 リソース検索結果（全142件） 名前	タイプ	リージョン	状態	コンパートメント subnet20250523053600	Subnet	us-sanjose-1	AV... | 11.08s | [A04.png](./A04.png) |
| A05 | ロードバランサを表示 | resource_search | PASS: 🔍 リソースを検索中... 🔍 リソース検索結果（全13件） 名前	タイプ	リージョン	状態	コンパートメント 50bcec80-6a72-41b4-8274-0fbc17faaf69	LoadBal... | 11.08s | [A05.png](./A05.png) |
| A06 | ap-osaka-1のリソースを表示 | resource_search | PASS: 🔍 リソースを検索中... 🔍 リソース検索結果（全813件） 名前	タイプ	リージョン	状態	コンパートメント publicip20260325095101	PublicIp	ap-osaka-1	... | 30.14s | [A06.png](./A06.png) |
| A07 | us-ashburn-1のVCNを表示 | resource_search | PASS: 🔍 リソースを検索中... 🔍 リソース検索結果（全6件） 名前	タイプ	リージョン	状態	コンパートメント batch-demo	Vcn	us-ashburn-1	AVAILABLE	yuki.so... | 10.08s | [A07.png](./A07.png) |
| A08 | ca-toronto-1のサブネットを表示して | resource_search | PASS: 🔍 リソースを検索中... 🔍 リソース検索結果（全11件） 名前	タイプ	リージョン	状態	コンパートメント プライベート・サブネット-agent-factory-vcn	Subnet	ca-tor... | 10.08s | [A08.png](./A08.png) |
| A09 | eu-frankfurt-1のインスタンスを一覧 | resource_search | PASS: 🔍 リソースを検索中... 🔍 リソース検索結果（全1件） 名前	タイプ	リージョン	状態	コンパートメント oke-cziqbqgmfea-nkofqbei6ha-svef7z3jeca-0	Ins... | 11.09s | [A09.png](./A09.png) |
| A10 | uk-london-1のリソースを検索 | resource_search | PASS: 🔍 リソースを検索中... 🔍 リソース検索結果（全238件） 名前	タイプ	リージョン	状態	コンパートメント security_group_validate_VCN_flow_log_1	Log	... | 25.13s | [A10.png](./A10.png) |
| A11 | 稼働中のインスタンスを表示 | resource_search | PASS: 🔍 リソースを検索中... 🔍 リソース検索結果（全4件） 名前	タイプ	リージョン	状態	コンパートメント oke-cx4zgxumhxa-nhgig4ndiyq-s4koxxzxvwa-2	Ins... | 11.07s | [A11.png](./A11.png) |
| A12 | 停止中のインスタンスを表示して | resource_search | PASS: 🔍 リソースを検索中... 🔍 リソース検索結果（全18件） 名前	タイプ	リージョン	状態	コンパートメント oke-cxjftfzasja-ncni3mvuvbq-sn4z6n53zcq-0	In... | 12.09s | [A12.png](./A12.png) |
| A13 | RUNNINGのリソースを一覧 | resource_search | PASS: 🔍 リソースを検索中... 🔍 リソース検索結果（全4件） 名前	タイプ	リージョン	状態	コンパートメント oke-cx4zgxumhxa-nhgig4ndiyq-s4koxxzxvwa-2	Ins... | 10.07s | [A13.png](./A13.png) |
| A14 | us-chicago-1のロードバランサを表示 | resource_search | PASS: 🔍 リソースを検索中... 🔍 リソース検索結果（全2件） 名前	タイプ	リージョン	状態	コンパートメント 50bcec80-6a72-41b4-8274-0fbc17faaf69	LoadBala... | 10.08s | [A14.png](./A14.png) |
| A15 | ap-seoul-1のインスタンスを表示 | resource_search | PASS: 🔍 リソースを検索中... 🔍 リソース検索結果（全4件） 名前	タイプ	リージョン	状態	コンパートメント oke-cbqd3cnzlzq-n3yxl3sitka-sxux3swjzwa-3	Ins... | 11.08s | [A15.png](./A15.png) |
| A16 | us-phoenix-1のVCNを表示 | resource_search | PASS: 🔍 リソースを検索中... 🔍 リソース検索結果（全6件） 名前	タイプ	リージョン	状態	コンパートメント oke-vcn-quick-cluster1-2eee33a99	Vcn	us-phoen... | 11.08s | [A16.png](./A16.png) |
| A17 | ap-sydney-1のサブネットを一覧 | resource_search | PASS: 🔍 リソースを検索中... 🔍 リソース検索結果（全2件） 名前	タイプ	リージョン	状態	コンパートメント public-subnet	Subnet	ap-sydney-1	AVAILABLE	 k... | 11.08s | [A17.png](./A17.png) |
| A18 | us-sanjose-1のリソースを表示して | resource_search | PASS: 🔍 リソースを検索中... 🔍 リソース検索結果（全286件） 名前	タイプ	リージョン	状態	コンパートメント waascertificate20260322043028	WaasCertifica... | 18.11s | [A18.png](./A18.png) |
| A19 | me-jeddah-1のリソースを一覧 | resource_search | PASS: 🔍 リソースを検索中... 🔍 リソース検索結果（全20件） 名前	タイプ	リージョン	状態	コンパートメント waascertificate20260322043028	WaasCertificat... | 12.08s | [A19.png](./A19.png) |
| A20 | データベースを表示 | resource_search | PASS: 🔍 リソースを検索中... リソースが見つかりませんでした。 | 12.08s | [A20.png](./A20.png) |

### B: Resource Search - Natural Language
| ID | Input | Expected | Result | Time | Screenshot |
|----|-------|----------|--------|------|------------|
| B01 | リソースを全部見せて | resource_search | FAIL: Resource Intelligence Agent へようこそ！ 自然言語でOCIリソースについて質問できます。例: 「全リソースを一覧して」 「ap-tokyo-1のインスタンスを表示」 「pr... | 109.38s | [B01.png](./B01.png) |
| B02 | 東京リージョンのインスタンス一覧 | resource_search | PASS: 🔍 リソースを検索中... 🔍 リソース検索結果（全4件） 名前	タイプ	リージョン	状態	コンパートメント 一時的なビルド用インスタンス	Instance	ap-tokyo-1	Stopped	yu... | 10.08s | [B02.png](./B02.png) |
| B03 | 大阪のVCNは？ | resource_search | PASS: 🔍 リソースを検索中... 🔍 リソース検索結果（全6件） 名前	タイプ	リージョン	状態	コンパートメント oke-vcn-quick-cluster1-4c5498f5a	Vcn	ap-osaka... | 10.07s | [B03.png](./B03.png) |
| B04 | シカゴのサブネット数を教えて | resource_search | PASS: 🔍 リソースを検索中... 🔍 リソース検索結果（全19件） 名前	タイプ	リージョン	状態	コンパートメント for-pod	Subnet	us-chicago-1	AVAILABLE	yuki.s... | 10.08s | [B04.png](./B04.png) |
| B05 | 全リージョンのインスタンスを検索 | resource_search | PASS: 🔍 リソースを検索中... 🔍 リソース検索結果（全22件） 名前	タイプ	リージョン	状態	コンパートメント oke-cxjftfzasja-ncni3mvuvbq-sn4z6n53zcq-0	In... | 11.07s | [B05.png](./B05.png) |
| B06 | ネットワークリソースを表示 | resource_search | PASS: 🔍 リソースを検索中... 🔍 リソース検索結果（全549件） 名前	タイプ	リージョン	状態	コンパートメント oke-nodesubnet-quick-cluster-update-6d15e46... | 21.12s | [B06.png](./B06.png) |
| B07 | コンピュートリソースを一覧 | resource_search | PASS: 🔍 リソースを検索中... 🔍 リソース検索結果（全22件） 名前	タイプ	リージョン	状態	コンパートメント oke-cxjftfzasja-ncni3mvuvbq-sn4z6n53zcq-0	In... | 11.08s | [B07.png](./B07.png) |
| B08 | 使っているVCNを教えて | resource_search | PASS: 🔍 リソースを検索中... 🔍 リソース検索結果（全55件） 名前	タイプ	リージョン	状態	コンパートメント vcn-20250523-1421	Vcn	us-sanjose-1	AVAILABLE... | 12.09s | [B08.png](./B08.png) |
| B09 | アクティブなロードバランサは？ | resource_search | PASS: 🔍 リソースを検索中... 🔍 リソース検索結果（全13件） 名前	タイプ	リージョン	状態	コンパートメント 50bcec80-6a72-41b4-8274-0fbc17faaf69	LoadBal... | 11.08s | [B09.png](./B09.png) |
| B10 | 全てのリソースを検索して下さい | resource_search | FAIL: Resource Intelligence Agent へようこそ！ 自然言語でOCIリソースについて質問できます。例: 「全リソースを一覧して」 「ap-tokyo-1のインスタンスを表示」 「pr... | 104.36s | [B10.png](./B10.png) |
| B11 | OCIリソースの一覧を表示 | resource_search | FAIL: Resource Intelligence Agent へようこそ！ 自然言語でOCIリソースについて質問できます。例: 「全リソースを一覧して」 「ap-tokyo-1のインスタンスを表示」 「pr... | 84.3s | [B11.png](./B11.png) |
| B12 | テナントの全リソース | resource_search | FAIL: Resource Intelligence Agent へようこそ！ 自然言語でOCIリソースについて質問できます。例: 「全リソースを一覧して」 「ap-tokyo-1のインスタンスを表示」 「pr... | 97.31s | [B12.png](./B12.png) |
| B13 | ap-tokyo-1のリソース一覧を出して | resource_search | PASS: 🔍 リソースを検索中... 🔍 リソース検索結果（全1119件） 名前	タイプ	リージョン	状態	コンパートメント publicip20260325092527	PublicIp	ap-tokyo-1... | 50.2s | [B13.png](./B13.png) |
| B14 | 動いているリソースを見せて | resource_search | FAIL: (TIMEOUT) | 120.0s | [B14.png](./B14.png) |
| B15 | インスタンスは何台ある？ | resource_search | PASS: 🔍 リソースを検索中... 🔍 リソース検索結果（全22件） 名前	タイプ	リージョン	状態	コンパートメント oke-cxjftfzasja-ncni3mvuvbq-sn4z6n53zcq-0	In... | 11.08s | [B15.png](./B15.png) |
| B16 | VCNの一覧をお願い | resource_search | PASS: 🔍 リソースを検索中... 🔍 リソース検索結果（全55件） 名前	タイプ	リージョン	状態	コンパートメント vcn7	Vcn	us-chicago-1	AVAILABLE	 ai-apps	Vcn... | 11.08s | [B16.png](./B16.png) |
| B17 | サブネットの一覧を出力して | resource_search | PASS: 🔍 リソースを検索中... 🔍 リソース検索結果（全142件） 名前	タイプ	リージョン	状態	コンパートメント for-pod	Subnet	us-chicago-1	AVAILABLE	yuki.... | 12.1s | [B17.png](./B17.png) |
| B18 | 全リージョンの全リソースを表示 | resource_search | FAIL:  | 121.4s | [B18.png](./B18.png) |
| B19 | ロードバランサーの一覧 | resource_search | FAIL: (TIMEOUT) | 120.0s | [B19.png](./B19.png) |
| B20 | 稼働中のサーバーを一覧して | resource_search | PASS: 🔍 リソースを検索中... 🔍 リソース検索結果（全4件） 名前	タイプ	リージョン	状態	コンパートメント oke-cx4zgxumhxa-nhgig4ndiyq-s4koxxzxvwa-2	Ins... | 11.08s | [B20.png](./B20.png) |

### C: Dependency Map
| ID | Input | Expected | Result | Time | Screenshot |
|----|-------|----------|--------|------|------------|
| C01 | ocid1.instance.oc1.ap-tokyo-1.anxhiljrss... | dependency_map | PASS: 🗺️ 依存関係マップを生成中... 🗺️ 依存関係マップ（起点: anxhiljrssl65iqc6t6g、深度: 3） ノード数: 5、エッジ数: 4 一時的なビルド用インスタンス (Instanc... | 17.11s | [C01.png](./C01.png) |
| C02 | ocid1.instance.oc1.ap-tokyo-1.anxhiljrss... | dependency_map | PASS: 🗺️ 依存関係マップを生成中... 🗺️ 依存関係マップ（起点: anxhiljrssl65iqc6t6g、深度: 1） ノード数: 2、エッジ数: 1 一時的なビルド用インスタンス (Instanc... | 14.08s | [C02.png](./C02.png) |
| C03 | ocid1.instance.oc1.ap-tokyo-1.anxhiljrss... | dependency_map | PASS: 🗺️ 依存関係マップを生成中... 🗺️ 依存関係マップ（起点: anxhiljrssl65iqc6t6g、深度: 3） ノード数: 5、エッジ数: 4 一時的なビルド用インスタンス (Instanc... | 17.12s | [C03.png](./C03.png) |
| C04 | ocid1.instance.oc1.ap-tokyo-1.anxhiljrss... | dependency_map | PASS: 🗺️ 依存関係マップを生成中... 🗺️ 依存関係マップ（起点: anxhiljrssl65iqc6t6g、深度: 3） ノード数: 5、エッジ数: 4 一時的なビルド用インスタンス (Instanc... | 16.1s | [C04.png](./C04.png) |
| C05 | このリソースの依存関係を表示: ocid1.instance.oc1.ap-to... | dependency_map | PASS: 🗺️ 依存関係マップを生成中... 🗺️ 依存関係マップ（起点: anxhiljrssl65iqc6t6g、深度: 3） ノード数: 5、エッジ数: 4 一時的なビルド用インスタンス (Instanc... | 18.11s | [C05.png](./C05.png) |
| C06 | ocid1.instance.oc1.ap-tokyo-1.anxhiljrss... | dependency_map | PASS: 🗺️ 依存関係マップを生成中... 🗺️ 依存関係マップ（起点: anxhiljrssl65iqc6t6g、深度: 3） ノード数: 5、エッジ数: 4 一時的なビルド用インスタンス (Instanc... | 18.09s | [C06.png](./C06.png) |
| C07 | 依存関係マップをocid1.instance.oc1.ap-tokyo-1.an... | dependency_map | PASS: 🗺️ 依存関係マップを生成中... 🗺️ 依存関係マップ（起点: anxhiljrssl65iqc6t6g、深度: 3） ノード数: 5、エッジ数: 4 一時的なビルド用インスタンス (Instanc... | 17.11s | [C07.png](./C07.png) |
| C08 | ocid1.instance.oc1.ap-tokyo-1.anxhiljrss... | dependency_map | PASS: 🗺️ 依存関係マップを生成中... 🗺️ 依存関係マップ（起点: anxhiljrssl65iqc6t6g、深度: 2） ノード数: 5、エッジ数: 4 一時的なビルド用インスタンス (Instanc... | 18.09s | [C08.png](./C08.png) |
| C09 | depth 0でocid1.instance.oc1.ap-tokyo-1.an... | dependency_map | PASS: 🗺️ 依存関係マップを生成中... 🗺️ 依存関係マップ（起点: anxhiljrssl65iqc6t6g、深度: 0） ノード数: 1、エッジ数: 0 一時的なビルド用インスタンス (Instanc... | 13.08s | [C09.png](./C09.png) |
| C10 | ocid1.instance.oc1.ap-tokyo-1.anxhiljrss... | dependency_map | PASS: 🗺️ 依存関係マップを生成中... 🗺️ 依存関係マップ（起点: anxhiljrssl65iqc6t6g、深度: 3） ノード数: 5、エッジ数: 4 一時的なビルド用インスタンス (Instanc... | 18.1s | [C10.png](./C10.png) |
| C11 | ocid1.instance.oc1.ap-tokyo-1.anxhiljrss... | dependency_map | PASS: 🗺️ 依存関係マップを生成中... 🗺️ 依存関係マップ（起点: anxhiljrssl65iqc6t6g、深度: 5） ノード数: 5、エッジ数: 4 一時的なビルド用インスタンス (Instanc... | 17.1s | [C11.png](./C11.png) |
| C12 | ocid1.instance.oc1.ap-tokyo-1.anxhiljrss... | dependency_map | PASS: 🗺️ 依存関係マップを生成中... 🗺️ 依存関係マップ（起点: anxhiljrssl65iqc6t6g、深度: 3） ノード数: 5、エッジ数: 4 一時的なビルド用インスタンス (Instanc... | 16.09s | [C12.png](./C12.png) |
| C13 | ocid1.instance.oc1.ap-tokyo-1.anxhiljrss... | dependency_map | PASS: 🗺️ 依存関係マップを生成中... 🗺️ 依存関係マップ（起点: anxhiljrssl65iqc6t6g、深度: 3） ノード数: 5、エッジ数: 4 一時的なビルド用インスタンス (Instanc... | 16.1s | [C13.png](./C13.png) |
| C14 | ocid1.instance.oc1.ap-tokyo-1.anxhiljrss... | dependency_map | PASS: 🗺️ 依存関係マップを生成中... 🗺️ 依存関係マップ（起点: anxhiljrssl65iqc6t6g、深度: 3） ノード数: 5、エッジ数: 4 一時的なビルド用インスタンス (Instanc... | 17.1s | [C14.png](./C14.png) |
| C15 | show dependency map for ocid1.instance.o... | dependency_map | PASS: 🗺️ 依存関係マップを生成中... 🗺️ 依存関係マップ（起点: anxhiljrssl65iqc6t6g、深度: 3） ノード数: 5、エッジ数: 4 一時的なビルド用インスタンス (Instanc... | 16.09s | [C15.png](./C15.png) |

### D: Help & General
| ID | Input | Expected | Result | Time | Screenshot |
|----|-------|----------|--------|------|------------|
| D01 | 使い方を教えて | help | PASS: OCIリソースの検索や依存関係の確認ができます。リソースの検索には『resource_search』、依存関係マップの表示には『dependency_map』を使用します。具体的なリソースや条件を指定... | 11.07s | [D01.png](./D01.png) |
| D02 | ヘルプ | help | PASS: OCI Resource Intelligence Agentは、OCIリソースの検索、依存関係マップの生成、およびヘルプを提供します。 利用可能なアクション: resource_search: リソ... | 17.11s | [D02.png](./D02.png) |
| D03 | 何ができますか？ | help | PASS: OCIリソースの検索、依存関係マップの表示、およびヘルプの提供が可能です。 | 9.06s | [D03.png](./D03.png) |
| D04 | help | help | PASS: OCI Resource Intelligence Agentは、OCIリソースの検索、依存関係マップの生成、およびヘルプを提供します。 利用可能なアクション: resource_search: リソ... | 16.09s | [D04.png](./D04.png) |
| D05 | こんにちは | help | PASS: こんにちは！OCIリソースの検索や依存関係マップの作成をお手伝いします。具体的なリクエストをお願いします。 | 10.06s | [D05.png](./D05.png) |
| D06 | OCIとは何ですか？ | help | PASS: OCIはOracle Cloud Infrastructureの略で、Oracleが提供するクラウドサービスプラットフォームです。リソースの検索や依存関係の確認など、OCIリソースに関するお問い合わせ... | 11.06s | [D06.png](./D06.png) |
| D07 | このエージェントは何をするの？ | help | PASS: このエージェントは、OCIリソースの検索、依存関係マップの生成、およびヘルプの提供を行います。リソースの検索や依存関係の確認、使い方についてのお問い合わせに対応します。 | 10.06s | [D07.png](./D07.png) |
| D08 | どのような検索ができますか？ | help | PASS: OCIリソースの検索や依存関係マップの表示が可能です。リソース検索では、リソースタイプ、リージョン、ライフサイクル状態、タグ、コンパートメントOCIDを指定できます。依存関係マップでは、ルートリソース... | 12.07s | [D08.png](./D08.png) |
| D09 | 依存関係マップとは何ですか？ | help | PASS: 依存関係マップは、指定したリソース（root_ocid）を中心に、関連する他のリソースとの接続関係や依存関係を可視化したものです。depthパラメータで表示する深さを指定できます。 | 11.06s | [D09.png](./D09.png) |
| D10 | サポートしているリソースタイプは？ | help | PASS: サポートしているリソースタイプは、OCIの標準リソースタイプ（例: Instance, Vcn, Subnet, LoadBalancer, DbSystem, Clusterなど）です。具体的なリソ... | 11.08s | [D10.png](./D10.png) |
| D11 | 使い方がわかりません | help | PASS: OCI Resource Intelligence Agentは、OCIリソースの検索や依存関係マップの生成を支援します。 リソース検索: リソースタイプ、リージョン、状態、タグ、コンパートメントを指... | 14.07s | [D11.png](./D11.png) |
| D12 | リージョンの一覧を教えて | help | PASS: リージョンの一覧はOCIの公式ドキュメントで確認できます。具体的なリソースの検索や依存関係の確認をお手伝いできます。 | 10.07s | [D12.png](./D12.png) |
| D13 | このツールの機能を教えて | help | PASS: このツールは、OCIリソースの検索、依存関係マップの表示、およびヘルプの提供を行います。以下の機能があります： リソース検索: 指定された条件に基づいてOCIリソースを検索します。 依存関係マップ: ... | 13.08s | [D13.png](./D13.png) |
| D14 | 検索条件にはどんなものがありますか？ | help | PASS: リソース検索の条件には、リソースタイプ、リージョン、ライフサイクル状態、タグフィルター、コンパートメントOCIDがあります。 | 10.07s | [D14.png](./D14.png) |
| D15 | ありがとう | help | PASS: お役に立てて嬉しいです。何かご質問があれば、お気軽にお問い合わせください。 | 10.07s | [D15.png](./D15.png) |

### E: Edge Cases & Error Handling
| ID | Input | Expected | Result | Time | Screenshot |
|----|-------|----------|--------|------|------------|
| E01 | (empty) | error | PASS: (no response - empty input ignored) | 3.0s | [E01.png](./E01.png) |
| E02 | あああああ | error | PASS: 申し訳ありませんが、ご依頼の内容が不明確です。リソースの検索、依存関係マップの表示、または使い方についてご質問がありましたら、具体的な内容をお知らせください。 | 11.06s | [E02.png](./E02.png) |
| E03 | SELECT * FROM resources | error | PASS: Resource Intelligence Agent へようこそ！ 自然言語でOCIリソースについて質問できます。例: 「全リソースを一覧して」 「ap-tokyo-1のインスタンスを表示」 「pr... | 94.32s | [E03.png](./E03.png) |
| E04 | ocid1.invalid.xxxの依存関係 | error | PASS: 🗺️ 依存関係マップを生成中... 🗺️ 依存関係マップ（起点: xxx、深度: 3） ノード数: 1、エッジ数: 0 xxx (invalid) | 11.08s | [E04.png](./E04.png) |
| E05 | 🎉🎉🎉 | error | PASS: おめでとうございます！何かお手伝いできることがあればお知らせください。 | 10.07s | [E05.png](./E05.png) |
| E06 | a very long query with lots and lots and... | error | PASS: Please provide a clear and concise query related to OCI resources. If you need assistance with resou... | 10.07s | [E06.png](./E06.png) |
| E07 | ap-tokyo-1 | error | PASS: 🔍 リソースを検索中... 🔍 リソース検索結果（全1119件） 名前	タイプ	リージョン	状態	コンパートメント publicip20260325092527	PublicIp	ap-tokyo-1... | 24.12s | [E07.png](./E07.png) |
| E08 | Instance | error | PASS: 🔍 リソースを検索中... 🔍 リソース検索結果（全22件） 名前	タイプ	リージョン	状態	コンパートメント oke-cxjftfzasja-ncni3mvuvbq-sn4z6n53zcq-0	In... | 11.09s | [E08.png](./E08.png) |
| E09 | 全リソースを一覧して | error | PASS: Resource Intelligence Agent へようこそ！ 自然言語でOCIリソースについて質問できます。例: 「全リソースを一覧して」 「ap-tokyo-1のインスタンスを表示」 「pr... | 113.38s | [E09.png](./E09.png) |
| E10 | <script>alert('xss')</script> | error | PASS: 不正な入力です。OCIリソースの検索や依存関係マップの表示をご希望の場合は、適切な指示をお願いします。 | 10.06s | [E10.png](./E10.png) |
| E11 | "; DROP TABLE resources; -- | error | PASS: 不正な入力です。リソースの検索や依存関係マップの表示など、OCIリソースに関する操作を指定してください。 | 11.07s | [E11.png](./E11.png) |
| E12 | 依存関係 | error | PASS: 依存関係を表示するには、ルートリソースのOCIDを指定してください。例: 'ocid1.instance... の依存関係を表示' | 10.07s | [E12.png](./E12.png) |
| E13 | 12345 | error | PASS: 入力が不明確です。リソースの検索、依存関係マップの表示、または使い方についてお問い合わせください。 | 11.07s | [E13.png](./E13.png) |
| E14 | null | error | PASS: 入力が無効です。リソースの検索、依存関係マップの表示、または使い方についてお問い合わせください。 | 11.06s | [E14.png](./E14.png) |
| E15 | リソース リソース リソース | error | PASS: リソースの検索や依存関係マップの表示が可能です。具体的な操作を教えてください。 | 10.06s | [E15.png](./E15.png) |

### F: Continuous Sequential
| ID | Input | Expected | Result | Time | Screenshot |
|----|-------|----------|--------|------|------------|
| F01 | VCNを一覧して | resource_search | PASS: 🔍 リソースを検索中... 🔍 リソース検索結果（全55件） 名前	タイプ	リージョン	状態	コンパートメント vcn7	Vcn	us-chicago-1	AVAILABLE	 ai-apps	Vcn... | 12.09s | [F01.png](./F01.png) |
| F02 | サブネットを表示 | resource_search | PASS: 🔍 リソースを検索中... 🔍 リソース検索結果（全142件） 名前	タイプ	リージョン	状態	コンパートメント for-pod	Subnet	us-chicago-1	AVAILABLE	yuki.... | 11.1s | [F02.png](./F02.png) |
| F03 | インスタンスを表示して | resource_search | PASS: 🔍 リソースを検索中... 🔍 リソース検索結果（全22件） 名前	タイプ	リージョン	状態	コンパートメント oke-cxjftfzasja-ncni3mvuvbq-sn4z6n53zcq-0	In... | 11.1s | [F03.png](./F03.png) |
| F04 | ロードバランサを一覧 | resource_search | PASS: 🔍 リソースを検索中... 🔍 リソース検索結果（全13件） 名前	タイプ	リージョン	状態	コンパートメント 50bcec80-6a72-41b4-8274-0fbc17faaf69	LoadBal... | 10.1s | [F04.png](./F04.png) |
| F05 | ap-tokyo-1のリソース | resource_search | FAIL: 🔍 リソースを検索中... | 39.24s | [F05.png](./F05.png) |
| F06 | ap-osaka-1のインスタンス | resource_search | FAIL: Resource Intelligence Agent へようこそ！ 自然言語でOCIリソースについて質問できます。例: 「全リソースを一覧して」 「ap-tokyo-1のインスタンスを表示」 「pr... | 29.18s | [F06.png](./F06.png) |
| F07 | 使い方を教えて | help | PASS: OCIリソースの検索や依存関係の確認ができます。リソース一覧を表示したい場合は『リソース一覧を表示』と指示してください。特定の依存関係を確認したい場合は『OCID1234の依存関係を表示』のようにOC... | 12.13s | [F07.png](./F07.png) |
| F08 | VCNを一覧して | resource_search | PASS: 🔍 リソースを検索中... 🔍 リソース検索結果（全55件） 名前	タイプ	リージョン	状態	コンパートメント vcn7	Vcn	us-chicago-1	AVAILABLE	 ai-apps	Vcn... | 11.13s | [F08.png](./F08.png) |
| F09 | 全リソースを一覧して | resource_search | FAIL: Resource Intelligence Agent へようこそ！ 自然言語でOCIリソースについて質問できます。例: 「全リソースを一覧して」 「ap-tokyo-1のインスタンスを表示」 「pr... | 98.63s | [F09.png](./F09.png) |
| F10 | ocid1.instance.oc1.ap-tokyo-1.anxhiljrss... | dependency_map | PASS: 🗺️ 依存関係マップを生成中... 🗺️ 依存関係マップ（起点: anxhiljrssl65iqc6t6g、深度: 3） ノード数: 5、エッジ数: 4 一時的なビルド用インスタンス (Instanc... | 17.16s | [F10.png](./F10.png) |
| F11 | サブネットを表示 | resource_search | PASS: 🔍 リソースを検索中... 🔍 リソース検索結果（全142件） 名前	タイプ	リージョン	状態	コンパートメント subnet20250523053600	Subnet	us-sanjose-1	AV... | 12.16s | [F11.png](./F11.png) |
| F12 | ヘルプ | help | PASS: OCI Resource Intelligence Agentは、OCIリソースの検索や依存関係マップの生成をサポートします。 利用可能なアクション: resource_search: リソースの検索... | 16.16s | [F12.png](./F12.png) |
| F13 | 稼働中のインスタンス | resource_search | PASS: 🔍 リソースを検索中... 🔍 リソース検索結果（全4件） 名前	タイプ	リージョン	状態	コンパートメント oke-cx4zgxumhxa-nhgig4ndiyq-s4koxxzxvwa-2	Ins... | 11.13s | [F13.png](./F13.png) |
| F14 | ca-toronto-1のVCN | resource_search | FAIL: Resource Intelligence Agent へようこそ！ 自然言語でOCIリソースについて質問できます。例: 「全リソースを一覧して」 「ap-tokyo-1のインスタンスを表示」 「pr... | 10.12s | [F14.png](./F14.png) |
| F15 | ありがとう | help | PASS: お役に立てて嬉しいです。何かご質問があれば、お気軽にお問い合わせください。 | 10.12s | [F15.png](./F15.png) |
