# USPTOデータ取得先調査

## リンク一覧

| 用途 | URL |
|------|-----|
| APIホームページ | https://data.uspto.gov/home |
| APIキー発行 | https://data.uspto.gov/myodp/key-reveal |
| Bulk Data（特許付与） | https://data.uspto.gov/bulkdata/datasets/ptgrdt |
| Bulk Data（オフィスアクション） | https://data.uspto.gov/bulkdata/datasets/oact |
| 〜2017年オフィスアクション（静的） | https://data.uspto.gov/bulkdata/datasets/ptoffact |

## API概要

**2017年以降のオフィスアクションデータは以下3つのODP APIから取得可能**

---

### 1. Office Action Text Retrieval API

特許審査官が出願人に発行したオフィスアクションの全文情報を取得。

**エンドポイント：**
```
GET https://api.uspto.gov/api/v1/patent/oa/oa_actions/v1/records
```

> **補足**：v2の `oa_rejections/v2/records` は拒絶フラグ＋全文を統合したエンドポイント。`oa_actions/v1/records` は旧エンドポイントで、クレームレベルの拒絶フラグのみ返す可能性あり。

トップレベルフィールド：

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `obsoleteDocumentIdentifier` | String | （キー）IFWリポジトリの文書固有識別子 |
| `patentApplicationNumber` | String | 特許出願番号（シリーズコード2桁＋シリアル番号6桁） |
| `patentNumber` | String | 付与特許番号 |
| `patentApplicationConfirmationNumber` | Long | 出願提出確認番号 |
| `applicationStatusNumber` | Long | 出願を一意に識別する文字列 |
| `customerNumber` | Long | 連絡用顧客番号 |
| `groupArtUnitNumber` | Long | グループアートユニット番号（4桁） |
| `filingDate` | Date | 出願書類受領日 |
| `effectiveFilingDate` | Date | 有効出願日（PTO基準） |
| `grantDate` | Date | 特許付与日 |
| `submissionDate` | Date | 庁指令の発行日 |
| `applicationDeemedWithdrawnDate` | Date | 出願放棄とみなされた日付 |
| `createDateTime` | Date | データベース挿入日時 |
| `lastModifiedTimestamp` | Date | レコード最終更新日時 |
| `documentActiveIndicator` | Boolean | 文書のアクティブ状態（0=非アクティブ / 1=アクティブ） |
| `bodyText` | String | オフィスアクション本文テキスト |
| `inventionTitle` | String | 発明の名称 |
| `inventionSubjectMatterCategory` | String | 特許種別コード（UTL/DES/PLTなど） |
| `nationalClass` | String | USPCメインクラスコード |
| `nationalSubclass` | String | USPCサブクラスコード |
| `techCenter` | String | テクノロジーセンター番号（4桁、最初2桁がセンター） |
| `workGroup` | String | ワークグループ（アートユニット内の小チーム） |
| `examinerEmployeeNumber` | String | 審査官従業員番号 |
| `accessLevelCategory` | String | アクセスレベル（Private / Public / Internal） |
| `applicationTypeCategory` | String | 特許出願の種別 |
| `legacyDocumentCodeIdentifier` | String | 旧文書コード識別子 |
| `legacyCMSIdentifier` | String | `PATENT-<出願番号>-OACS-<obsoleteDocId>` 形式の識別子 |
| `sourceSystemName` | String | 文書の発信元システム名（OACS, EFSWebなど） |
| `id` | String | レコード固有識別子 |

セクション別フィールド（`sections.*`）：

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `sections.officeActionIdentifier` | String | レコード固有ID |
| `sections.obsoleteDocumentIdentifier` | String | IFWリポジトリの文書識別子 |
| `sections.patentApplicationNumber` | String | 特許出願番号 |
| `sections.legacyDocumentCodeIdentifier` | String | 文書コードテーブルのサロゲートキー |
| `sections.filingDate` | Date | 出願の公式提出日 |
| `sections.submissionDate` | Date | 申請受付開始日 |
| `sections.grantDate` | Date | 申請承認日 |
| `sections.techCenterNumber` | Date | テクノロジーセンター番号 |
| `sections.groupArtUnitNumber` | String | 審査官アートユニット番号 |
| `sections.nationalClass` | String | USPCメインクラスコード |
| `sections.nationalSubclass` | String | USPCサブクラスコード |
| `sections.workGroupNumber` | String | ワークグループ番号 |
| `sections.examinerEmployeeNumber` | String | 審査官従業員番号 |
| `sections.section101RejectionText` | String | §101拒絶理由テキスト |
| `sections.section102RejectionText` | String | §102拒絶理由テキスト（新規性欠如） |
| `sections.section103RejectionText` | String | §103拒絶理由テキスト（自明性） |
| `sections.section112RejectionText` | String | §112拒絶理由テキスト |
| `sections.section101RejectionFormParagraphText` | String | §101拒絶の標準化フォーム段落テキスト |
| `sections.section102RejectionFormParagraphText` | String | §102拒絶の標準化フォーム段落テキスト |
| `sections.section103RejectionFormParagraphText` | String | §103拒絶の標準化フォーム段落テキスト |
| `sections.section112RejectionFormParagraphText` | String | §112拒絶の標準化フォーム段落テキスト |
| `sections.summaryText` | String | 事務処理・決定の要約 |
| `sections.detailCitationText` | String | 「詳細アクション」ヘッダーのテキスト |
| `sections.withdrawalRejectionText` | String | 申請却下に対する控訴理由 |
| `sections.terminalDisclaimerStatusText` | String | 最終免責事項のステータス（提出済み・受理済み・保留中等） |
| `sections.specificationTitleText` | String | 明細書の状態 |
| `sections.proceedingAppendixText` | String | 付録の手続き |

---

### 2. Office Action Rejections API

オフィスアクションからの拒絶フラグデータを毎日更新・取得。

**エンドポイント：**
```
GET https://api.uspto.gov/api/v1/patent/oa/oa_rejections/v2/records
```

主なデータプロパティ：

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `obsoleteDocumentIdentifier` | String | IFWリポジトリの文書識別子 |
| `patentApplicationNumber` | String | 特許出願番号 |
| `legalSectionCode` | String | 拒絶根拠の法条項コード |
| `submissionDate` | Date | 庁指令の発行日 |
| `createDateTime` | Date | データベース挿入日時 |
| `groupArtUnitNumber` | String | グループアートユニット番号 |
| `nationalClass` | String | USPCメインクラスコード |
| `nationalSubclass` | String | USPCサブクラスコード |
| `actionTypeCategory` | String/Boolean | アクション種別（rejected / cancelled / allowed 等） |
| `legacyDocumentCodeIdentifier` | String | 旧文書コード識別子（CTNF / CTFR 等） |
| `hasRej101` | Float | §101拒絶の有無（1/0） |
| `hasRej102` | Float | §102拒絶の有無 — 新規性欠如（1/0） |
| `hasRej103` | Float | §103拒絶の有無 — 自明性（1/0） |
| `hasRej112` | Float | §112拒絶の有無（1/0） |
| `hasRejDP` | Float | 非法定二重特許拒絶の有無（1/0） |
| `cite103Max` | Long | §103拒絶で引用された先行技術の最大文献数 |
| `cite103EQ1` | Long | §103拒絶で引用文献が1件のみ（1/0） |
| `cite103GT3` | Long | §103拒絶で引用文献が3件超（1/0） |
| `aliceIndicator` | Boolean | アリス/メイヨーフレームワーク審査対象か |
| `mayoIndicator` | Boolean | メイヨー判決参照の有無 |
| `bilskiIndicator` | String/Boolean | ビルスキ判決参照の有無 |
| `myriadIndicator` | Boolean | ミリアド判決（天然物・遺伝物質）参照の有無 |
| `allowedClaimIndicator` | Boolean | 許可されたクレームを含むか |
| `claimNumberArrayDocument` | String | 関連クレーム番号の配列 |
| `paragraphNumber` | String | 参照されている段落番号 |
| `closingMissing` | Long | 最終段落（連絡先情報）の欠落（1/0） |
| `headerMissing` | Long | ヘッダーの欠落（1/0） |
| `formParagraphMissing` | Long | フォーム段落の欠落（1/0） |
| `rejectFormMissmatch` | Long | フォーム内容と想定形式の不一致（1/0）（スペルママ） |
| `id` | String | レコード固有識別子 |
| `createUserIdentifier` | String | 挿入ジョブの識別子 |

`legacyDocumentCodeIdentifier`（文書コード）の主な値：
- `CTNF`：Non-Final Office Action（最初の拒絶理由通知）
- `CTFR`：Final Office Action（最終拒絶理由通知）

**JSONレスポンスサンプル：**

```json
{
  "response": {
    "start": 0,
    "numFound": 4,
    "docs": [
      {
        "applicationDeemedWithdrawnDate": "2017-06-29T00:00:00",
        "workGroup": ["1710"],
        "filingDate": "2014-10-03T00:00:00",
        "documentActiveIndicator": ["0"],
        "legacyDocumentCodeIdentifier": ["CTFR"],
        "applicationStatusNumber": 161,
        "nationalClass": ["134"],
        "bodyText": ["The present application is being examined under the pre-AIA first to invent provisions....."],
        "obsoleteDocumentIdentifier": ["IOEU2JMBRXEAPX0"],
        "accessLevelCategory": ["PUBLIC"],
        "id": "e2dbe4766f92e4454cf57b18abc3de4c36070e1cd4239f94b50e79b5",
        "applicationTypeCategory": ["REGULAR"],
        "patentNumber": ["null"],
        "patentApplicationNumber": ["14390655"],
        "submissionDate": "2016-05-23T00:00:00",
        "customerNumber": 25944,
        "groupArtUnitNumber": 1711,
        "inventionTitle": ["METHOD FOR CLEANING SEMICONDUCTOR WAFER"],
        "nationalSubclass": ["002000"],
        "examinerEmployeeNumber": ["72492"],
        "createDateTime": "2024-12-05T09:29:15",
        "techCenter": ["1700"],
        "inventionSubjectMatterCategory": ["UTL"],
        "sourceSystemName": ["OACS"],
        "legacyCMSIdentifier": ["PATENT-14390655-OACS-IOEU2JMBRXEAPX0"]
      }
    ]
  }
}
```

> **注意**：JSONレスポンスのフィールドが `bodyText`・`inventionTitle` 等のText Retrieval系フィールドを含む。`oa_actions/v1/records`（旧エンドポイント）はクレームレベルの拒絶フラグを返し、`oa_rejections/v2/records`（v2）はアクション全文も含む形式に統合されたと考えられる。

---

### 3. Office Action Citation API

2017年10月1日以降に郵送されたオフィスアクションからの引用データを毎日更新。  
Form PTO-892・PTO-1449および庁指令本文の引用情報を使用。

**エンドポイント：**
```
GET https://api.uspto.gov/api/v1/patent/oa/oa_citations/v2/records
```

主なデータプロパティ：

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `obsoleteDocumentIdentifier` | String | （キー）IFWリポジトリの文書固有識別子 |
| `referenceIdentifier` | String | 引用文献の識別子（特許番号または公開番号）。PTO-892・PTO-1449のXMLを解析・結合して生成 |
| `parsedReferenceIdentifier` | String | `referenceIdentifier` の数値部分のみ |
| `patentApplicationNumber` | String | 特許出願番号（シリーズコード2桁＋シリアル番号6桁） |
| `officeActionCitationReferenceIndicator` | Boolean | 庁指令で参照された引用か。正（値1）の場合、`obsoleteDocumentIdentifier`・`actionTypeCategory`・`legalSectionCode` が該当庁指令を特定する |
| `examinerCitedReferenceIndicator` | Boolean | PTO-892（審査官）由来の引用か |
| `applicantCitedExaminerReferenceIndicator` | Boolean | PTO-1449（出願人提出）由来の引用か。2017年6月時点で審査中の出願はデータが不完全な場合あり |
| `actionTypeCategory` | String | アクション種別（rejected / cancelled / withdrawn / interpreted / objected / allowed 等） |
| `legalSectionCode` | String | 法条項コード（拒絶根拠の法的根拠条項） |
| `groupArtUnitNumber` | String | グループアートユニット番号（4桁、先頭2桁がテクノロジーセンター） |
| `techCenter` | String | テクノロジーセンター番号（4桁、先頭2桁が実質のセンター） |
| `workGroup` | String | ワークグループ（アートユニット内の小チーム） |
| `paragraphNumber` | String | 引用が参照している段落番号 |
| `createDateTime` | Date | データベース挿入日時 |
| `createUserIdentifier` | String | 挿入ジョブの識別子 |
| `id` | String | レコード固有識別子 |

**JSONレスポンスサンプル：**

```json
{
  "response": {
    "start": 0,
    "numFound": 2,
    "docs": [
      {
        "applicantCitedExaminerReferenceIndicator": false,
        "createUserIdentifier": "ETL_SYS",
        "workGroup": "1740",
        "officeActionCitationReferenceIndicator": false,
        "referenceIdentifier": "------- European Patent",
        "patentApplicationNumber": "14404075",
        "actionTypeCategory": "",
        "legalSectionCode": "",
        "groupArtUnitNumber": "1742",
        "createDateTime": "2025-07-09T15:40:52",
        "techCenter": "1700",
        "obsoleteDocumentIdentifier": "IXRYOH0ORXEAPX1",
        "parsedReferenceIdentifier": "",
        "id": "67d1e8f3956ca6cb0c9f6b54c2a7839f",
        "examinerCitedReferenceIndicator": true
      },
      {
        "applicantCitedExaminerReferenceIndicator": true,
        "createUserIdentifier": "ETL_SYS",
        "workGroup": "1740",
        "officeActionCitationReferenceIndicator": false,
        "referenceIdentifier": "------- European Patent",
        "patentApplicationNumber": "14404075",
        "actionTypeCategory": "",
        "legalSectionCode": "",
        "groupArtUnitNumber": "1742",
        "createDateTime": "2025-07-09T15:40:52",
        "techCenter": "1700",
        "obsoleteDocumentIdentifier": "IXRYOH0ORXEAPX1",
        "parsedReferenceIdentifier": "",
        "id": "6dfedff7ed31f51adaa9da15fc60ae0b",
        "examinerCitedReferenceIndicator": false
      }
    ]
  }
}

---

### 4. Patent File Wrapper API

特許出願の書誌情報・表紙データをユーザーフレンドリーな形式で検索。

**注意**：バルクデータを1件ずつ取得するのみ。審査中のアクションデータ（拒絶理由）はなく、引用文献もバルクダウンロードと情報量が同じため、大量取得にはBulk Dataの方が効率的。

---

### 5. Enriched Citations API

特許評価プロセスへの深い洞察を提供する拡張引用API。

**エンドポイント：**

```text
GET https://api.uspto.gov/api/v1/patent/oa/enriched_cited_reference_metadata/v3/records
```

主なデータプロパティ：

| フィールド | 型 | 説明 |
| --- | --- | --- |
| `citedDocumentIdentifier` | String | （キー）引用特許文献の識別子（特許番号または公開番号）。PTO-892・PTO-1449のXMLを解析・結合して生成 |
| `relatedClaimNumberText` | String | （キー）引用に関連するクレーム番号のコレクション（例：`"1,7"`） |
| `obsoleteDocumentIdentifier` | Boolean | （キー）IFWリポジトリの文書固有識別子 |
| `patentApplicationNumber` | String | 特許出願番号（シリーズコード2桁＋シリアル番号6桁） |
| `officeActionDate` | Date | オフィスアクションが記録された日付 |
| `officeActionCategory` | String | オフィスアクション種別（例：`CTNF`） |
| `citationCategoryCode` | Boolean | 検索レポートにおける引用文献の関連性カテゴリコード（X, Y, A, E, L, O, T, P, &, D） |
| `examinerCitedReferenceIndicator` | Boolean | PTO-892（審査官）由来の引用か |
| `applicantCitedExaminerReferenceIndicator` | Boolean | PTO-1449（出願人提出）由来の引用か |
| `qualitySummaryText` | String | 審査品質サマリー（分類コード#1〜#6、または`AOK`） |
| `passageLocationText` | String | 引用に関連するパッセージ位置（`\|`区切り） |
| `inventorNameText` | String | 引用文献の発明者名または企業名 |
| `groupArtUnitNumber` | String | グループアートユニット番号（4桁） |
| `techCenter` | String | テクノロジーセンター番号（最初の2桁） |
| `workGroupNumber` | String | ワークグループ番号 |
| `publicationNumber` | String | 引用文献の公開番号 |
| `countryCode` | String | 引用文献の国コード |
| `kindCode` | String | 文献種別コード（例：`A1`） |
| `nplIndicator` | Boolean | 非特許文献（NPL）か |
| `id` | String | レコード固有識別子 |
| `createDateTime` | Date | データベース挿入日時 |
| `createUserIdentifier` | String | 挿入ジョブの識別子 |

`qualitySummaryText` の分類コード：

- `AOK`：問題なし
- `#1`：892なし・IDSが取得された
- `#2`：アルゴリズムが先行技術を見落とした
- `#3`：先行技術（NPL）が正しく解決されなかった
- `#4`：先行技術（外国出願）が正しく解決されなかった
- `#5`：先行技術（米国出願）が正しく解決されなかった
- `#6`：NPLが拒絶理由に使用された

`citationCategoryCode` の意味（EPOサーチレポート準拠）：

- `X`：単独で新規性・進歩性に影響する文献
- `Y`：他の文献と組み合わせで進歩性に影響する文献
- `A`：技術水準を示す参考文献

**JSONレスポンスサンプル：**

```json
{
  "response": {
    "start": 0,
    "numFound": 3,
    "docs": [
      {
        "relatedClaimNumberText": "1,7",
        "officeActionDate": "2019-10-21T00:00:00",
        "patentApplicationNumber": "15739603",
        "officeActionCategory": "CTNF",
        "citedDocumentIdentifier": "US 20190165601 A1",
        "publicationNumber": "20190165601",
        "citationCategoryCode": "Y",
        "examinerCitedReferenceIndicator": true,
        "applicantCitedExaminerReferenceIndicator": false,
        "qualitySummaryText": "AOK",
        "groupArtUnitNumber": "2837",
        "techCenter": "2800",
        "inventorNameText": "Supriya; Amrit",
        "nplIndicator": false,
        "kindCode": "A1",
        "countryCode": "US",
        "passageLocationText": ["c. 112|figure 3|claim 9|..."],
        "obsoleteDocumentIdentifier": "K1V5RMZ8RXEAPX0",
        "id": "d7e95803517f677b3875dc476a61a817",
        "createDateTime": "2026-03-02T21:36:52"
      }
    ]
  }
}
```

---

---

### 6. Patent File Wrapper (PFW) Documents API

出願ごとのファイルラッパー内の**全文書**（メタデータ＋PDFダウンロードURL）を取得。

**エンドポイント：**
```
GET https://api.uspto.gov/api/v1/patent/applications/{applicationNumberText}/documents
```

- `applicationNumberText`：出願番号（意匠特許は `29/XXXXXX` 系列）
- 対象：2001年以降の公開出願・付与特許、日次更新
- APIキー必要

**取得できる文書種別（例）：**

| コード | 文書の種類 |
|---|---|
| `CTFR` / `CTNF` | Final / Non-Final Office Action（審査官発行） |
| `A..` | 出願人による応答（Remarks/Arguments を含む） |
| `IDS` | Information Disclosure Statement（先行技術開示） |
| `OATH` | 宣誓書 |
| `DRWG` | 図面 |

**重要な制約：**
- レスポンスはメタデータ＋PDFダウンロードURLのみ。**構造化テキストは返らない**
- 出願人のRemarksテキストを取得するにはPDFダウンロード→テキスト抽出（OCR）が必要
- IMPACT CSVの `id`（特許番号 `D0949851`）≠ 出願番号。File Wrapper検索APIで変換が必要

**出願番号の逆引き方法：**
```
GET https://api.uspto.gov/api/v1/patent/applications/search?patentNumber=D949851
```

---

### 意匠特許の「出願時新規性文書」について（調査メモ）

米国意匠特許の出願時提出物には、日本の「意匠の説明」に相当する**新規性を主張する文書が存在しない**。

- クレームは定型文「The ornamental design for [article], as shown and described.」のみ
- 新規性主張が言語化されるのは、審査中に§102/§103拒絶を受けた場合の**出願人応答（Remarks）**

| 文書 | タイミング | テキストAPI |
|---|---|---|
| OAへの応答Remarks（新規性主張の核心） | 審査中 | なし（PDF経由のみ） |
| IDS（先行技術開示リスト） | 出願時〜審査中 | なし（PDF経由のみ） |
| §102拒絶テキスト（審査官が何と対比したか） | 審査中 | **Office Action Text APIで取得可** |

→ 実用上は**§102拒絶テキスト**（審査官側）の方が構造化されており取得しやすい。出願人Remarksは価値があるが、PDF解析が必要でスケールしにくい。

---

## データアクセス方針まとめ

| データ種別 | 推奨取得方法 |
|-----------|------------|
| 〜2017年 オフィスアクション | Bulk Data静的ダウンロード（ptoffact） |
| 2017年〜 拒絶理由文（全文） | Office Action Text Retrieval API |
| 2017年〜 拒絶種別フラグ | Office Action Rejections API |
| 2017年〜 引用文献 | Office Action Citation API（またはBulk Data） |
| 書誌情報（少量） | Patent File Wrapper API |
| 書誌情報（大量） | Bulk Data（ptgrdt） |
| 拡張引用・品質情報 | Enriched Citations API |
