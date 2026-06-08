# IMPACT データ情報

    
---

# 🧠 ① 基本メタ情報（特許そのもの）

### ■ title

- 特許のタイトル（製品名・デザイン名）
- 例：`Bottle`, `Chair`

---

### ■ patent_id

- 特許番号（USPTOの一意ID）
- 例：`USD0939806`

---

### ■ publication_date

- 公開日（特許が成立した日）

---

### ■ application_date

- 出願日（申請した日）

👉 この2つで

**審査期間・時間分析ができる**

---

### ■ claim

- クレーム文（権利範囲の文章）
- design特許では短いことが多い

👉 NLP的には：

- テキスト特徴として使える
- ただしdesignでは重要度低め

---

# 🧠 ② 分類情報（カテゴリ）

### ■ locarno_class

- ロカルノ分類（国際デザイン分類）

👉 例：

- 家具
- 容器
- 衣類

👉 design系では最重要クラス

---

### ■ us_class

- US独自の分類コード

---

### ■ class_search

- 検索用分類（複数）
- CPCや補助分類が入る

👉 特徴：

- **多ラベル的**
- 類似検索で使える

---

# 🧠 ③ 人・企業情報

### ■ applicant_org

- 出願者（企業・組織）

---

### ■ assignee_org

- 権利保有者（企業）

👉 applicantとの違い：

- applicant = 出願
- assignee = 所有

---

### ■ inventor_names

- 発明者の名前（複数）

---

### ■ inventor_countries

- 発明者の国

---

### ■ applicant_countries

- 出願者の国

👉 分析用途：

- 国別トレンド
- 企業分析

---

# 🧠 ④ 図面情報（重要🔥）

### ■ no_figs

- 図の数（figure数）

---

### ■ sheets

- 図面シート数

👉 design特許の特徴：

- **1特許 = 複数view**
- (front / side / top)

---

### ■ file_names

- 画像ファイル名リスト

例：

```
USDxxxx-D00001.TIF
USDxxxx-D00002.TIF
```

👉 重要：

- マルチビュー学習に直結

---

### ■ fig_desc

- 図の説明文（XMLのdescription-of-drawings）

👉 例：

- "FIG.1 is a front view..."
- "FIG.2 is a side view..."

👉 かなり重要：

- **view情報（top/front/side）を含む**
- → DeepPatent2でも抽出対象

---

# 🧠 ⑤ フォルダ・パス系（実装寄り）

### ■ patent_folder_outer

- 外側フォルダ（週単位tar）

例：

```
I20220104
```

👉 USPTOの配布単位

---

### ■ patent_folder_inner

- 内側フォルダ（特許単位）

例：

```
USD0939806-20220104
```

👉 実際のデータ格納単位

---

# 🧠 まとめ構造（重要）

このCSVはこういう構造👇

```
[特許単位]
    ├─ 基本情報
    ├─ 分類
    ├─ 人・企業
    ├─ 図面メタ
    └─ ファイルパス
```

---

### ★重要

- title
- claim
- fig_desc
- locarno_class（us_classとの違い？）