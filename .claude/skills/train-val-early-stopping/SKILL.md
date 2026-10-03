---
name: train-val-early-stopping
description: Mandatory convention for this project — any new training code must hold out part of the data as a validation split and use it for early stopping, rather than training on 100% of the data for a fixed number of epochs. Use this whenever writing, scaffolding, or reviewing a training script/loop/DataModule in this repo (COrAL variants, functional_description encoder fine-tuning, a future reranker trainer, or any other model training code) — even if the user doesn't say "validation" or "early stopping" explicitly (e.g. "write a training script for X", "add a trainer for the new encoder", "fine-tune model Y on this data").
---

# Train/val split + early stopping (project convention)

**Rule:** any training code written for this project must split off part of the training data as a validation set and use it to drive early stopping. Never wire a training loop that only sees a train split and runs for a fixed epoch count with no held-out signal — that produces overfit checkpoints with no way to detect it.

## Reference implementation

This pattern is already implemented once in this repo — reuse it as the template rather than inventing a new one:

- `論文/論文再現実装/COrAL/dataset/impact.py` (`IMPACTDataModule.__init__`, ~line 255-301): splits the full dataset with `torch.utils.data.random_split(full_ds, [n_train, n_val], generator=torch.Generator().manual_seed(42))`, `val_ratio=0.1` by default. Fixed seed → reproducible split across runs.
- `論文/論文再現実装/COrAL/main_impact.py` (~line 335-345): PyTorch Lightning `EarlyStopping(monitor="val/loss_total", patience=args.patience)` callback, plus a custom callback that prints `train_loss` vs `val_loss` per epoch so overfitting is visible in the log.

(Note: per CLAUDE.md, COrAL code lives on the Drive path and must be edited there, not the local mirror.)

## Checklist for any new training script

1. **Split before building DataLoaders.** Hold out a validation subset (10% is this project's default; adjust only if the user specifies otherwise). Use a fixed seed so the split is reproducible across reruns.
2. **Decide if the split needs to be stratified.** Plain `random_split` is fine for self-supervised / contrastive pretraining (as in COrAL). If the new training task is supervised over a categorical label (e.g. Locarno class), consider a stratified split instead so val isn't skewed.
3. **Compute a validation metric every epoch (or every N steps).** Same loss/metric the model is trained on, evaluated with `model.eval()` / `torch.no_grad()` on the held-out split, not the train split.
4. **Wire early stopping on that validation metric**, not on train loss:
   - Lightning: `pytorch_lightning.callbacks.EarlyStopping(monitor="val/<metric>", patience=<N>, mode="min"/"max")`.
   - Plain PyTorch loop: track the best validation metric seen so far, save a checkpoint whenever it improves, and break the loop after `patience` epochs with no improvement.
5. **Log train vs. val side by side** (print, CSV, or TensorBoard) so divergence between the two is visible without re-running anything.

## What's exempt

Pure inference/embedding scripts (`search.py`, `build_embeddings.py`, `generate_func_desc.py`) don't train a model and are not in scope here. This applies specifically to code that fits model parameters via gradient updates.
