---
name: impact-locarno-title-labels
description: Four data-quality facts about the IMPACT year-level CSVs (data/IMPACT/{year}.csv) that are easy to get wrong when building a label (e.g. image→title or image→category prediction task, or grouping patents by product type). (1) `locarno_class` is the true Locarno International Design Classification field — `class`/`class_search` is the unrelated USPTO design-patent classification (D-code); do not use `class` when the task calls for Locarno. (2) Most `locarno_class` values were corrupted by Excel auto-converting "class-subclass" strings (e.g. "01-01") into date literals (e.g. "1月1日" or "Jan-99") at some point in the data's history — must be reversed before grouping/filtering by Locarno class. (3) `title` has real semantic wording variation for the SAME referent — not just surface noise (plural/hyphen/word order), but true synonyms in different words ("Coffee Maker" / "Coffeemaker", "Bicycle" / "Bike"), full paraphrases ("Beverage cooler" / "Cooler for beverages"), and different granularity ("Chair" / "Office chair", "Vehicle" / "Automobile") — confirmed via embedding cosine similarity (0.8-1.0 sim despite near-zero lexical token overlap). String-level normalization cannot detect this; only semantic similarity can. (4) Generic/functional titles ("container", "handle", "clip", "lamp", "cover") are NOT wording-variation synonyms of each other across different Locarno major classes — they legitimately describe unrelated products that happen to share a generic name (verified: "container" alone spans 25 of the 32 Locarno major classes). When reporting or grouping by `locarno_major` or `locarno_class`, always attach the official Locarno class/subclass name (full tables included below, major class in English+Japanese, all 219 subclasses in Japanese) — never present bare 2-digit or 4-digit codes to the user. Use this whenever working with IMPACT's `locarno_class` or `class` columns, or designing a task/label scheme that uses `title` as a target (classification, captioning, retrieval-by-category).
---

# IMPACT: locarno_class corruption, class vs locarno_class, and title label noise

## 1. `class` ≠ Locarno classification

In `data/IMPACT/{year}.csv`, the column named **`class`** (values like `"D 1106, D1128"`) is the **USPTO design-patent classification (D-code)**, not Locarno. The actual Locarno International Design Classification lives in the **`locarno_class`** column (values like `"02-04"` = class-subclass). See `impact_data_information.md` line 52 vs line 66 for the documented distinction (`us_class` there = `class` in the CSV).

Don't group/filter by `class` when the task needs Locarno-level product categories — verified empirically: grouping "shoe"-titled patents by `class` scatters them across many USPTO D-codes, while grouping by the correctly-recovered `locarno_class` puts ~95% of them in Locarno major class `02` (clothing/footwear), as expected.

## 2. `locarno_class` is Excel-date-mangled for most rows

Reading `locarno_class` directly shows values like `'1月1日'`, `'6月7日'`, `'Jan-99'`, `'Feb-29'` instead of the expected `"NN-NN"` format. This is **not an encoding bug** — the values are genuinely stored as literal Japanese/short-form dates. Root cause: at some point the CSV was opened/saved in Excel, which auto-converted `"class-subclass"` strings that look like valid dates (e.g. `"01-01"` → Jan 1) into date values, displayed either as a Japanese long date (`M月D日`) or an English short date (`Mmm-YY`) depending on the cell/column format at conversion time. Only combinations that can't be parsed as a date (e.g. `"04-99"`, `"31-00"`) survived as plain text.

**Update (2026-08-15): resolved.** The corruption turned out to affect **only `data/IMPACT/2022.csv`**, not 2007–2021 (verified directly — those years' `locarno_class` was already clean `"NN-NN"` text). `2022.csv` was re-fetched from the original Hugging Face upload (which lacks a `locarno_class` column entirely — it's a locally-derived column, not part of the published dataset) and `locarno_class` was regenerated from scratch via `extract_locarno.py` (parses `<classification-locarno><main-classification>` straight out of each patent's XML — ground truth, no date-mangling risk). All 33,541 rows extracted with zero nulls. **As of this fix, every `data/IMPACT/{year}.csv` for 2007–2022 has clean, correct `locarno_class` values — `fix_locarno()` below is no longer required for current data, but keep it as a defensive parser** in case a CSV gets Excel-opened-and-saved again (a real risk: Excel auto-formats any `"NN-NN"`-shaped CSV cell as a date purely from double-click-opening it, and that becomes permanent the moment the file is saved from Excel — never double-click-open `data/IMPACT/*.csv`; if inspection is needed, use a text editor/pandas, or Excel's "データ→テキストまたはCSVから" import with the column's data type explicitly set to Text).

**Historical bug worth knowing about** (in case old cached results or old code still use the naive version): the straightforward "month=major, day=subclass" reversal is only correct when major≤12 (a valid month). For major 13–32, Excel's date parser falls back to treating the pair as day-month instead of month-day (since major>12 isn't a valid month), so the rendered date has month and day **swapped** relative to the major≤12 case. A naive fixer that always reads month=major, day=subclass silently corrupts every major-13–32 row (confirmed: 91% of the day>12 cases in old 2022.csv were affected, e.g. Locarno 14-04 "Graphical User Interface and Icons" was being misread as the nonexistent code "04-14"). The version below disambiguates using the known-subclass table (`LOCARNO_SUBCLASS_NAMES_JA` — see §4) whenever day>12: try both `"major-subclass"` and `"subclass-major"` and keep whichever is a real subclass code.

```python
import re

MONTH_ABBR = {m: i + 1 for i, m in enumerate(
    ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"])}
_date_pat = re.compile(r"^(\d{1,2})月(\d{1,2})日$")
_dash_pat = re.compile(r"^(\d{1,2})-(\d{1,2})$")
_abbr_pat = re.compile(r"^([A-Za-z]{3})-(\d{1,2})$")

def _disambiguate(month_num: int, day_num: int, known_subclasses: set[str]) -> str:
    if day_num <= 12:
        return f"{month_num:02d}-{day_num:02d}"  # unambiguous
    non_swapped = f"{month_num:02d}-{day_num:02d}"
    swapped = f"{day_num:02d}-{month_num:02d}"
    if swapped in known_subclasses and non_swapped not in known_subclasses:
        return swapped
    return non_swapped  # best-effort fallback if neither/both match

def fix_locarno(v, known_subclasses: set[str] = frozenset()):
    if not isinstance(v, str):
        return None
    if m := _dash_pat.match(v):
        return f"{int(m.group(1)):02d}-{int(m.group(2)):02d}"
    if m := _date_pat.match(v):
        return _disambiguate(int(m.group(1)), int(m.group(2)), known_subclasses)
    if (m := _abbr_pat.match(v)) and m.group(1) in MONTH_ABBR:
        return _disambiguate(MONTH_ABBR[m.group(1)], int(m.group(2)), known_subclasses)
    raise ValueError(f"unrecognized locarno_class value: {v!r}")
```

Always apply `fix_locarno()` (or equivalent) before using `locarno_class` for grouping, stratified sampling, or as a label — never read the raw column value at face value (defensive practice; not currently needed for `data/IMPACT/{year}.csv` post-fix, see above). This corruption is specific to the year-level CSVs (`data/IMPACT/{year}.csv`); the per-folder `processed_xml_{year}.csv` doesn't even have a `locarno_class` column. `extract_locarno.py` (project root) regenerates `locarno_class` from XML ground truth per year — the authoritative fix if a file ever gets re-corrupted, preferable over heuristic reconstruction.

## 3. `title` has real wording variation — don't treat it as a clean label

Motivation: a proposed task direction is "predict the title from the design image alone," since generic VLMs don't reliably recognize niche design-patent products (see `research_ideas.md`, "画像→タイトル/caption言い当てタスク"). Locarno class + title are the only usable label fields for this (caption is AI-generated post-hoc text, not a ground-truth label). Before treating `title` as a clean classification/generation target, its wording consistency for the *same* product was checked.

**Important distinction:** the interesting variation here is *not* surface-form noise (plural/singular, hyphenation, word order, articles) — that's a minor, easily-normalized layer. The real problem is titles describing **the same referent using entirely different words, sentence structure, or level of specificity** — i.e. true 表記ゆれ in the sense of "same thing, different expression," not "same word, different spelling."

**Confirmed via semantic embedding similarity** (`sentence-transformers/paraphrase-multilingual-mpnet-base-v2`, cosine sim on title pairs within the same correctly-recovered `locarno_class` subclass, filtered to low lexical token-overlap so surface-form matches don't dominate the results):

- **True synonyms, different words entirely**: `"Coffee Maker"` ↔ `"Coffeemaker"` (sim 0.98), `"Bicycle bag"` ↔ `"Bike bag"` (0.98), `"Automobile hood"` ↔ `"Car hood"` (0.98), `"Drink cup"` ↔ `"Drinking cup"` (0.98)
- **Full paraphrase / different sentence structure for the same object**: `"Beverage cooler"` ↔ `"Cooler for beverages"` (0.98), `"Beverage-making machine"` ↔ `"Machine for producing a beverage"` (0.98), `"Brewing apparatus"` ↔ `"Brewing device"` (0.98)
- **Different granularity (hypernym vs. hyponym) for an overlapping referent**: `"Shoe"` vs `"Footwear"` (0.927 — near-synonymous but different abstraction level), `"Chair"` vs `"Office chair"` (0.817 — generic vs. specific instance), `"Vehicle"` vs `"Automobile"` (0.874)

These pairs have token overlap as low as 0.00–0.33 (i.e. share almost no literal words) yet sit at 0.97+ cosine similarity — **string-level normalization (case-folding, depluralization, word-sorting) cannot detect this class of variation at all.** Only semantic/embedding similarity surfaces it.

Practical implications:
- Raw `title` string match — even after light normalization — is not usable as a canonical label; it undercounts true positives (same product, different wording treated as different classes) and will silently conflate different-abstraction-level titles as if they were unrelated.
- Any label design for an image→title task should either (a) canonicalize titles via embedding-based clustering (not string normalization) before treating them as classes, or (b) frame the task as retrieval/generation rather than closed-set classification, since the underlying "class" set is inherently fuzzy and multi-granular, not a clean partition.

## 4. Generic titles reuse across unrelated Locarno classes — and always attach the official class name

**Don't assume identical/near-identical `title` strings across different Locarno major classes are the same-referent wording variation described in §3.** Verified empirically across all 434,498 rows in `data/IMPACT/2007.csv`…`2022.csv`: 5.8% of exact-match title strings (8,700 distinct titles) appear under more than one Locarno major class, and this concentrates heavily in generic/functional part names, not specific product names:

| title (exact match) | # distinct Locarno major classes | row count |
| --- | --- | --- |
| container | 25 | 2,876 |
| cover | 20 | 99 |
| handle | 18 | 490 |
| connector | 18 | 584 |
| dispenser | 18 | 455 |
| holder | 15 | 121 |
| electronic device | 14 | 1,485 |
| clip | 14 | 193 |
| lamp | 11 | 1,104 |

Spot-checked by pulling actual cover-drawing images for "container" and "handle" across their different Locarno majors — these are genuinely different-looking products (e.g. a Class 01 food container vs. a Class 09 packaging container), not the same product mis-filed twice. So this is a *different* phenomenon from §3's true-synonym wording variation: it's word polysemy, not label noise. Working hypothesis for canonicalization (§3), **not yet empirically confirmed**: the safe canonicalization key is the pair (Locarno major, title/title-embedding) rather than title text alone — a raw title string is not a safe class label on its own when the title is a generic part name. Whether synonym-clustering should be scoped to *within* a Locarno major (vs. some other scoping) has not been tested; don't present that as decided.

**Official Locarno major class names (WIPO Locarno Classification, 32 classes) — English and Japanese, cross-verified from two independent sources** (Hong Kong IPD's English table and a local Japanese-language PDF of the 15th edition, `ロカルノ分類.pdf` at the project root — all 32 names matched exactly between sources). IMPACT's `locarno_major` (after `fix_locarno()`) also contains a handful of non-standard codes outside 01–32 (e.g. `77`, `99` seen in the data) that are not part of the official WIPO list — treat these as "unclassified/other", not an error.

```python
LOCARNO_CLASS_NAMES = {
    "01": {"en": "Foodstuffs", "ja": "食料品"},
    "02": {"en": "Articles of clothing and haberdashery", "ja": "衣料品及び裁縫用小物"},
    "03": {"en": "Travel goods, cases, parasols and personal belongings, not elsewhere specified", "ja": "旅行用具，ケース，日傘及び他に該当しない身の回り品"},
    "04": {"en": "Brushware", "ja": "ブラシ製品"},
    "05": {"en": "Textile piece goods, artificial and natural sheet material", "ja": "紡績用繊維，人工及び天然のシート材料"},
    "06": {"en": "Furnishing", "ja": "室内用品"},
    "07": {"en": "Household goods, not elsewhere specified", "ja": "家庭用品，他で明記されていないもの"},
    "08": {"en": "Tools and hardware", "ja": "工具及び金物類"},
    "09": {"en": "Packaging and containers for the transport or handling of goods", "ja": "物品の輸送又は荷扱いのための包装用容器及び容器"},
    "10": {"en": "Clocks and watches and other measuring instruments, checking and signalling instruments", "ja": "時計，携帯型時計及びその他の計測機器，検査機器及び信号機器"},
    "11": {"en": "Articles of adornment", "ja": "装飾用品"},
    "12": {"en": "Means of transport or hoisting", "ja": "輸送又は昇降の手段"},
    "13": {"en": "Equipment for production, distribution or transformation of electricity", "ja": "電気の生産，供給又は変流のための機器"},
    "14": {"en": "Recording, telecommunication or data processing equipment", "ja": "記録，電気通信又はデータ処理用の機器"},
    "15": {"en": "Machines, not elsewhere specified", "ja": "機械，他で明記されていないもの"},
    "16": {"en": "Photographic, cinematographic and optical apparatus", "ja": "写真撮影用，映画撮影用及び光学用機器"},
    "17": {"en": "Musical instruments", "ja": "楽器"},
    "18": {"en": "Printing and office machinery", "ja": "印刷機及び事務用機械"},
    "19": {"en": "Stationery and office equipment, artists' and teaching materials", "ja": "文房具及び事務機器，美術材料及び教材"},
    "20": {"en": "Sales and advertising equipment, signs", "ja": "販売及び広告機器，サイン"},
    "21": {"en": "Games, toys, tents and sports goods", "ja": "遊戯用具，玩具，テント及び運動用品"},
    "22": {"en": "Arms, pyrotechnic articles, articles for hunting, fishing and pest killing", "ja": "武器，火工品，狩猟，釣り及び害虫駆除のための物品"},
    "23": {"en": "Fluid distribution equipment, sanitary, heating, ventilation and air-conditioning equipment, solid fuel", "ja": "流体供給機器，衛生用，暖房用，換気用及び空調用の機器，固体燃料"},
    "24": {"en": "Medical and laboratory equipment", "ja": "医療用及び実験用器具"},
    "25": {"en": "Building units and construction elements", "ja": "建築用ユニット及び建築部材"},
    "26": {"en": "Lighting apparatus", "ja": "照明用機器"},
    "27": {"en": "Tobacco and smokers' supplies", "ja": "たばこ及び喫煙用の供給品"},
    "28": {"en": "Pharmaceutical and cosmetic products, toilet articles and apparatus", "ja": "医薬品及び化粧品，洗面室用品及び設備"},
    "29": {"en": "Devices and equipment against fire hazards, for accident prevention and for life saving", "ja": "防火用，事故防止用及び救命用器具及び設備"},
    "30": {"en": "Articles for the care and handling of animals", "ja": "動物の世話及び飼育用の物品"},
    "31": {"en": "Machines and appliances for preparing food or drink, not elsewhere specified", "ja": "飲食物を調理するための機械及び器具，他で明記されていないもの"},
    "32": {"en": "Graphic symbols and logos, surface patterns, ornamentation, arrangement of interiors and exteriors", "ja": "グラフィックシンボル及びロゴ，表面模様，装飾，内装及び外装の配置"},
}
```

Always look up `locarno_major` through this table (or an equivalent JSON/CSV copy) when presenting results — a bare code like `"09"` is meaningless to a reader; `"09 (Packaging and containers for the transport or handling of goods)"` is not.

**Official Locarno subclass names (Japanese, 15th edition, all 219 subclasses).** Extracted directly from `ロカルノ分類.pdf` at the project root (page-rendered and read visually, since the PDF's embedded text layer has a broken CJK font encoding that garbles every extraction library — `pypdf`, `PyMuPDF`, both tried and failed identically; render pages to PNG with PyMuPDF/`fitz` at ~200dpi and read them directly if this file needs re-parsing). English subclass names were not sourced (the WIPO English PDF has the same unparseable-text problem and was not resolved). `03-02`, `15-08`, `19-05`, `23-02` are blank/reserved in the 15th edition (printed as `[空欄]`) — expect no IMPACT rows to carry these subclass codes, or treat them as data noise if seen. Class 31 has only one subclass, `31-00`, not `31-01`.

```python
LOCARNO_SUBCLASS_NAMES_JA = {
    "01-01": "ベーカリー製品，ビスケット，ペーストリー，パスタ及びその他の穀物加工品，チョコレート，菓子，氷菓",
    "01-02": "果物，野菜及びそれらの加工品",
    "01-03": "チーズ，バター及びバター代用品，その他の乳製品",
    "01-04": "肉（豚肉製品を含む），魚",
    "01-05": "豆腐及び豆腐製品",
    "01-06": "飼料",
    "01-99": "その他",
    "02-01": "下着，婦人用下着，コルセット，ブラジャー，寝巻",
    "02-02": "衣類",
    "02-03": "帽子",
    "02-04": "履物，靴下及びストッキング",
    "02-05": "ネクタイ，スカーフ，ネッカチーフ及びハンカチ",
    "02-06": "手袋",
    "02-07": "裁縫用小物及び衣類付属品",
    "02-99": "その他",
    "03-01": "トランク，スーツケース，書類かばん，ハンドバッグ，キーホルダー，収容物に合うように特別に設計されたケース，財布及びこれらに類する物品",
    "03-03": "雨傘，日傘，日よけ及びつえ",
    "03-04": "扇子",
    "03-05": "乳児及び子供の運搬及び歩行用器具",
    "03-99": "その他",
    "04-01": "清掃用ブラシ及びほうき",
    "04-02": "化粧用ブラシ，衣類用ブラシ及び靴用ブラシ",
    "04-03": "機械用ブラシ",
    "04-04": "絵筆，調理用ブラシ",
    "04-99": "その他",
    "05-01": "紡績した物品",
    "05-02": "レース",
    "05-03": "刺しゅう布",
    "05-04": "リボン，組ひも及びその他の装飾用縁飾り",
    "05-05": "織物類",
    "05-06": "人工又は天然のシート材料",
    "05-99": "その他",
    "06-01": "腰掛け",
    "06-02": "ベッド",
    "06-03": "テーブル及び類する家具",
    "06-04": "収納用家具",
    "06-05": "複合家具",
    "06-06": "その他の家具及び家具用部品",
    "06-07": "鏡及び額縁",
    "06-08": "衣類用ハンガー",
    "06-09": "マットレス及びクッション",
    "06-10": "カーテン及び室内用日よけ",
    "06-11": "じゅうたん，マット及びラグ",
    "06-12": "つづれ織物",
    "06-13": "毛布及びその他の掛け布，家庭用リネン製品",
    "06-99": "その他",
    "07-01": "磁器，ガラス製品，皿及び類するその他の物品",
    "07-02": "調理用機械器具，用具及び容器",
    "07-03": "テーブルカトラリー",
    "07-04": "飲食物を調理するための手で扱う器具及び用具",
    "07-05": "アイロン，洗浄，清掃及び乾燥用の機器",
    "07-06": "その他の台所及び食卓用具",
    "07-07": "その他の家庭用容器",
    "07-08": "暖炉用器具",
    "07-09": "家庭用器具及び用具用スタンド及びホルダー",
    "07-10": "冷却及び冷凍器具並びに保温容器",
    "07-99": "その他",
    "08-01": "穴あけ，フライス削り又は掘削のための工具及び器具",
    "08-02": "ハンマー及びその他の類する工具及び器具",
    "08-03": "切削工具及び器具",
    "08-04": "ドライバー，スパナ，レンチ及びそれらの付属品",
    "08-05": "その他の工具及び器具",
    "08-06": "取手，ノブ及びちょうつがい",
    "08-07": "施錠又は閉鎖具",
    "08-08": "他の類に含まれない締め具，支持具，据え付け具",
    "08-09": "他の類又は小類に含まれないドア用，窓用及び家具用の取付け及び固定金具及び類する物品",
    "08-10": "自転車及び自動二輪車用ラック",
    "08-11": "カーテン用金具",
    "08-99": "その他",
    "09-01": "瓶，フラスコ，つぼ，ガラス瓶及び加圧式容器",
    "09-02": "格納缶，ドラム及びたる",
    "09-03": "箱，ケース，容器及び缶",
    "09-04": "ふた付きかご，木箱及びかご",
    "09-05": "バッグ，におい袋，チューブ及びカプセル",
    "09-06": "綱及び輪状の材料",
    "09-07": "閉塞具及び付属品",
    "09-08": "フォークリフト用のパレット及びプラットフォーム",
    "09-09": "くず及びごみ容器及びそのスタンド",
    "09-10": "包装用容器及び容器の運搬又は取扱い用取手及びグリップ",
    "09-99": "その他",
    "10-01": "時計及び目覚まし時計",
    "10-02": "携帯型時計及び腕時計",
    "10-03": "その他の計時機器",
    "10-04": "その他の計測機器",
    "10-05": "検査，安全又は試験のための機器",
    "10-06": "信号機器",
    "10-07": "計測，検査及び信号に用いられる機器の筐体，ケース，文字盤，針及びその他の全ての部品及び付属品",
    "10-99": "その他",
    "11-01": "宝飾品",
    "11-02": "装飾用小物，テーブル用，暖炉柵用及び壁面用装飾品，花瓶及びつぼ",
    "11-03": "メダル及びバッジ",
    "11-04": "造花，果物及び植物の模造品",
    "11-05": "旗，祝祭用装飾品",
    "11-99": "その他",
    "12-01": "動物によって引かれる荷車",
    "12-02": "手車，手押車",
    "12-03": "機関車及び鉄道車両並びにその他の全ての鉄道車両",
    "12-04": "空中ケーブル運搬機，いすリフト及びスキーリフト",
    "12-05": "積込み用，又は運搬用のエレベーター及び巻上機",
    "12-06": "船舶及びボート",
    "12-07": "航空機及び宇宙船",
    "12-08": "乗用自動車，バス及び貨物自動車",
    "12-09": "トラクター",
    "12-10": "道路走行車両トレーラー",
    "12-11": "自転車及び自動二輪車",
    "12-12": "乳母車，車いす，担架",
    "12-13": "特殊車両",
    "12-14": "その他の車両",
    "12-15": "車両用のタイヤ及びすべり止め用タイヤチェーン",
    "12-16": "車両用の部品，機器及び付属品で，他の類又は小類に含まれないもの",
    "12-17": "鉄道基盤構成部品",
    "12-99": "その他",
    "13-01": "発電機及び電動機",
    "13-02": "電力変圧器，整流器，電池及び蓄電池",
    "13-03": "電力の供給又は制御のための機器",
    "13-04": "太陽光機器",
    "13-99": "その他",
    "14-01": "音声又は映像の記録又は複製用の機器",
    "14-02": "自動データ処理機器及び周辺機器",
    "14-03": "電気通信機器，無線遠隔制御機器及び無線増幅器",
    "14-04": "グラフィカルユーザーインターフェース及びアイコン",
    "14-05": "記録及びデータ記憶媒体",
    "14-06": "電子機器用ホルダー，スタンド及び支持具，他の類に含まれないもの",
    "14-99": "その他",
    "15-01": "エンジン",
    "15-02": "ポンプ及び圧縮機",
    "15-03": "農業用及び林業用機械",
    "15-04": "建設及び採掘機械",
    "15-05": "洗浄，清掃及び乾燥用の機械",
    "15-06": "紡績用繊維，裁縫用，編み用及び刺しゅう用の機械並びにそれらに不可欠な部品",
    "15-07": "冷蔵機械及び機器",
    "15-09": "工作機械，研磨機及び鋳造機",
    "15-10": "袋詰め，梱包又は包装用機械",
    "15-99": "その他",
    "16-01": "写真撮影用及び映画撮影用カメラ",
    "16-02": "映写機及びビューアー",
    "16-03": "複写機及び引伸機",
    "16-04": "現像器具及び機器",
    "16-05": "写真撮影及び映画撮影用機器の付属品",
    "16-06": "光学用品",
    "16-99": "その他",
    "17-01": "けん盤楽器",
    "17-02": "管楽器",
    "17-03": "弦楽器",
    "17-04": "打楽器",
    "17-05": "機械式演奏楽器",
    "17-99": "その他",
    "18-01": "タイプライター及び計算機",
    "18-02": "印刷機",
    "18-03": "タイプ及びタイプフェイス",
    "18-04": "製本用機械，印刷機のステープル打ち具，断裁機及びトリマー（製本用）",
    "18-99": "その他",
    "19-01": "筆記用紙，通信及び通知用のカード",
    "19-02": "事務用機器",
    "19-03": "カレンダー",
    "19-04": "書籍及び類する外観を持つその他のもの",
    "19-06": "手書き，製図，絵画，彫刻，銅版画及びその他の美術技法のための材料及び用具",
    "19-07": "教材及び教育機器",
    "19-08": "その他の印刷物",
    "19-99": "その他",
    "20-01": "自動販売機",
    "20-02": "陳列及び販売機器",
    "20-03": "サイン，看板及び広告機器",
    "20-99": "その他",
    "21-01": "遊戯用具及び玩具",
    "21-02": "体操及び運動器具及び機器",
    "21-03": "その他の遊戯及び娯楽用品",
    "21-04": "テント及びその付属品",
    "21-99": "その他",
    "22-01": "発射体",
    "22-02": "その他の武器",
    "22-03": "鉄砲弾，ロケット及び火工品",
    "22-04": "標的及び付属品",
    "22-05": "狩猟及び釣りの機器",
    "22-06": "わな，害虫駆除のための物品",
    "22-99": "その他",
    "23-01": "流体供給機器",
    "23-03": "加熱機器",
    "23-04": "換気及び空調機器",
    "23-05": "固体燃料",
    "23-06": "身体衛生用器具",
    "23-07": "排尿及び排便用機器",
    "23-08": "他の類又は小類に含まれないその他の衛生機器及び付属品",
    "23-99": "その他",
    "24-01": "医療用及び実験用の機器及び器具",
    "24-02": "医療用及び実験用の手で扱う機器及び道具",
    "24-03": "人工装具",
    "24-04": "傷の被覆，看護及び治療のための材料",
    "24-05": "歩行補助具",
    "24-99": "その他",
    "25-01": "建築材料",
    "25-02": "プレハブ又はあらかじめ組立てられた建築部品",
    "25-03": "家屋，車庫及びその他の建築物",
    "25-04": "階段，はしご及び足場",
    "25-99": "その他",
    "26-01": "しょく台及び枝付きしょく台",
    "26-02": "懐中電灯，手持ちランプ及びランタン",
    "26-03": "公共照明備付品，屋外照明，舞台照明",
    "26-04": "光源，電気又は非電気によるもの",
    "26-05": "ランプ，フロアスタンドランプ，シャンデリア，壁面及び天井の照明，写真及び映画の映写機用ランプ",
    "26-06": "車両用の発光機器",
    "26-07": "照明器具用部品及び付属品，他の類及び小類に含まれないもの",
    "26-99": "その他",
    "27-01": "たばこ，葉巻たばこ及び紙巻きたばこ",
    "27-02": "パイプ，シガーホルダー及びシガレットホルダー",
    "27-03": "灰皿",
    "27-04": "マッチ",
    "27-05": "ライター",
    "27-06": "葉巻たばこ用容器，紙巻きたばこ用容器，シガレットケース及び刻みたばこ用入れ",
    "27-07": "電子たばこ及びその他の電子喫煙用品",
    "27-99": "その他",
    "28-01": "医薬品",
    "28-02": "化粧品",
    "28-03": "洗面室用品及び美容院用機器",
    "28-04": "かつら及び美容つけ用具",
    "28-05": "芳香剤",
    "28-06": "整髪器具及び用具",
    "28-99": "その他",
    "29-01": "防火用の機器及び器具",
    "29-02": "事故防止用及び救命用の機器及び器具で，他に明記されていないもの",
    "29-99": "その他",
    "30-01": "動物用衣料品",
    "30-02": "おり，かご，犬小屋及び類するシェルター",
    "30-03": "給餌器及び給水器",
    "30-04": "馬具",
    "30-05": "むち及び突き棒",
    "30-06": "動物用寝台，巣及び家具",
    "30-07": "とまり木及びその他のかご付属品",
    "30-08": "マーカー，付け札及びシャックル",
    "30-09": "つなぎ柱",
    "30-10": "動物用毛繕い用品",
    "30-11": "動物用トイレ及び動物排泄物除去のための器具",
    "30-12": "動物用玩具及び訓練機器",
    "30-99": "その他",
    "31-00": "飲食物を調理するための機械及び器具，他で明記されていないもの",
    "32-01": "グラフィックシンボル及びロゴ，表面模様，装飾",
    "32-02": "内装及び外装の配置",
}
```
