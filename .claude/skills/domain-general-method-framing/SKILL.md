---
name: domain-general-method-framing
description: Whenever proposing, designing, framing, or writing up a method/contribution for this project (research ideas, design docs, weekly reports, paper outlines, experiment plans, deep-research prompts, next-step recommendations) — place the work in the image captioning / visual description literature (describing an image so the right referent is identified), and keep the contribution domain-general and transferable to ordinary images, and treat the design-patent line drawings (IMPACT, white-background front-view drawings) as ONE testbed that provides evidence, never as the thing the method is tailored to. The user is targeting a top-tier vision/ML conference (CVPR-class main track), and a proposal that only works because the images are sparse black-and-white line art reads as an industry/application-track paper. Fires even when the user's request is narrow ("write the design doc", "what should we do next", "summarize this survey", "write a deep research prompt"), and even when a domain-specific trick is the cheapest thing that would work — offer it as an implementation detail or ablation, not as the contribution.
---

# Keep the contribution domain-general, not line-drawing-specific

The user's standing goal: a **top-tier conference main-track** contribution. Design patent drawings are the **evidence**, not the subject. A method whose core mechanism only makes sense for white-background line art (ink-density clustering, stroke extraction, figure-label stripping, binarization tricks) gets read as an application paper — which is explicitly not what the user wants.

## What this means in practice

**Frame the claim at the level of a general property of images and models**, then show design patents are a place where that property is extreme and measurable.

- Bad framing: "Patent line drawings have sparse ink, so we cluster ink density to find the discriminative region."
- Good framing: "The discriminative cue's spatial extent varies per instance — for some images the whole silhouette decides the label, for others a small part does. Models apply a fixed granularity. We measure this property, show it predicts failure, and route on it."

The second claim is testable on birds, cars, products, documents, medical images — and design drawings become the case where the contrast is cleanest.

## Where the work is positioned

The research is framed as **image captioning / visual description**, not as design-patent retrieval or classification. Naming the product in a drawing is one instance of "produce a description that identifies the referent among confusable alternatives" — the discriminative-captioning line (Dai & Lin; Luo et al.'s self-retrieval; speaker–listener and RSA work). The 8-choice benchmark is a listener test, so report it that way, and keep the vocabulary of that literature (distinctiveness, self-retrieval, listener accuracy, granularity of description) rather than retrieval-benchmark vocabulary (mAP, recall@k on patent figures).

## Rules

1. **The core mechanism must not require line art.** Anything that depends on white background, binary ink, or patent figure conventions belongs in preprocessing/implementation, an ablation, or a domain-adaptation paragraph — never in the method's definition.
2. **Every proposed method/metric gets a one-line generality check**: "what does this compute on a photograph?" If the answer is "nothing meaningful", redesign it.
3. **Evaluation plans include at least one non-line-drawing dataset.** Prefer standard fine-grained or perception benchmarks so reviewers can place the result (CUB, Stanford Cars, FGVC-Aircraft, MMVP, V*Bench, HR-Bench, or similar), alongside the design-patent benchmark.
4. **Position against the general literature, not the patent literature.** Novelty is argued against dynamic-inference / adaptive-granularity / visual-search work (GFNet, AdaFocus, V*, ZoomEye, ViCrop, FOCUS …), not against patent-retrieval papers. Patent-side work (DeepPatent, Density-Refine) is related work for the testbed, not the baseline being beaten.
5. **Domain-specific findings stay as motivation or analysis.** "Drawings with a common-looking housing fail more" is a finding; the contribution is the general property it exemplifies.
6. **When a domain trick is genuinely the fastest path to an answer**, say so explicitly and label it: "quickest diagnostic, not the contribution" — so it never silently becomes the paper's method.
7. **Design-doc / deep-research prompts inherit this.** When writing a survey prompt or design doc, ask for general mechanisms and general evaluation, with the line-drawing case as a stress test.

## Signals that the framing has drifted

- The method name contains "sketch", "line", "ink", "drawing", "patent".
- The pipeline's first step only exists because the background is white.
- The evaluation section lists only design-patent splits.
- Related work is dominated by patent-retrieval papers, and the captioning / visual-description line is missing.
- The stated contribution would be unfalsifiable on a photo dataset.

When any of these appear, flag it in the reply and offer the general reformulation alongside.
