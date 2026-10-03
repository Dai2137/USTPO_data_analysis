---
name: japanese-responses
description: Every reply to the user in this project must be written in Japanese — including when the user's message is only a pasted English log, traceback, Colab output, or images with no text, and when the previous tool results were all English. Use on every turn before writing the reply text, especially turns where the user's message contains little or no Japanese (pasted output, screenshots, contact sheets) — those are exactly the turns where replies have drifted into English.
---

# ユーザーへの返答は必ず日本語で書く

このプロジェクトでは、ユーザーへの返答（ツール呼び出しの合間の短い報告も含む）を**必ず日本語で書く**。

## よく起きる失敗

ユーザーの発言に日本語がほとんどないターンで、英語で返してしまう。実際に起きた場面：

- Colab の英語の出力（`$ python order_blocks.py ...` のログ、トレースバック）だけが貼られたとき
- 画像（ブロックの一覧のシートなど）だけが送られたとき
- 直前のツールの結果が英語ばかりだったとき

ユーザーはこのたびに「日本語で話して」「だから日本語で教えて」と言い直す必要があった。**入力が英語や画像だけでも、返答の言語は日本語のまま変えない。**

## 書き方

- 説明・表の見出し・箇条書き・結論はすべて日本語
- コードの識別子、ファイル名、コマンド、モデル名、英語の製品名（図面のタイトル）は原文のまま
- 英語の出力を引用するときも、その意味は日本語で説明する
- 書き終えたら送る前に、日本語になっているかを確かめる

## 例外

ユーザーが別の言語での出力をはっきり求めたとき（英語の論文の文面、英語のプロンプト、コードのコメントなど）は、その成果物だけをその言語で書く。成果物を渡すときの説明は日本語で書く。
