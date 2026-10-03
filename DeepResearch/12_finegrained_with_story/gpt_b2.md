# 条件を満たす手法の一覧  
現時点で、テスト時に画像ごとにLLMを用い、かつ出力語彙を事前に固定しない細粒度認識手法として確認できたのは、Fine-R1 (ICLR 2026)、DiVE-k (arXiv 2025)、SpeciaRL (arXiv 2026) の3本のみでした。これら以外には該当手法は見つかっていません。  

# 条件2を満たさない手法の一覧（判定と理由）  
- **Enhancing Cognition and Explainability of Multimodal Foundation Models with Self-Synthesized Data**（Shi et al., arXiv 2502.14044）  
  - **判定:** 条件2未達成。推論時プロンプトに「What is the *<上位カテゴリ>* in this image?」という形で上位カテゴリ（例: *bird*）を明示的に与えており、さらに生成した回答文に「正解ラベル*c* を含むこと」という制約を設けています。これは手法の核として既知のカテゴリ情報（粗カテゴリ）を前提にしているため、条件2を満たしません。  
  - **事後学習:** 行う（LLMをファインチューニング）  
  - **画像の扱い:** 全体画像（局所部位は特徴抽出のため用いるが、出力はグローバルな問いかけに対するもの）  
  - **評価:** Stanford Dogs など細粒度データセットで精度・説明生成性能を評価（説明の有無や妥当性にGPT-4oを用いた自動評価も実施）  

# 除外した手法の一覧（除外理由）  
- **Object Recognition as Next Token Prediction**（Yue et al., CVPR 2024） – *除外理由:* 1画像中の複数物体（複数カテゴリ）の同時認識を前提とした手法であり、細粒度認識（単一物体＋1カテゴリ）設定の範囲外と判断しました。本文でも「複数ラベルのトークンを並列にサンプリングし、確率で順位付けする」と記述されています。  
- **Why are Visually-Grounded Language Models Bad at Image Classification?**（Zhang et al., NeurIPS 2024） – *除外理由:* 一般画像分類モデルの性能分析を目的とした研究で、細粒度認識問題設定ではありません（ImageNetなど一般画像分類を扱う）。  
- **Efficient Vocabulary-Free FGVR (NeaR)**（Kuchibhotla et al., arXiv 2505.01064） – *除外理由:* 画像分類モデルとして最終的にCLIP系をファインチューニングして用いる手法で、推論時にLLMを動かしません。本文に「LLMで生成したラベルで下流CLIPモデルをファインチューニングする」とあり、実際のテスト時推論はCLIPによる類似度分類で行われます。  
- **Democratizing Fine-grained Visual Recognition (FineR)**（Liu et al., ICLR 2024） – *除外理由:* LLMを用いて概念を推論するものの、推論結果で得た概念リストをCLIP等で分類に用いる「ゼロショット画像分類」手法です。実際の推論ではCLIP（VLM）を用いており、LLMを直接動かしません。したがって推論時にLLMを実行する条件1を満たしません。  

# ベンチマーク・分析論文の一覧  
- **Why are Visually-Grounded Language Models Bad at Image Classification?**（Zhang et al., NeurIPS 2024） – VLM を画像分類器として評価した分析研究。CLIP と比べて大きく性能が劣る原因をデータ分布に求め、分類に特化したデータ追加で改善できることを示しました（詳しくは自由記述評価方法ではありませんが、VLMの画像分類性能の現状分析として参考になります）。  
- **Is CLIP the main roadblock for fine-grained open-world perception?**（Bianchi et al., arXiv 2404.03539） – CLIP埋め込みの限界を解析し、微細属性の分離性欠如が精緻な認識を妨げると報告した検証研究。オープンワールド検出の文脈ですが、CLIP潜在空間での細粒度情報の扱い方（自由語彙での概念表現）に関する示唆があります。