"""
CS462 — Thai Digit Classifier — Evaluation Script
Loads the trained model and generates evaluation charts WITHOUT retraining.
Run:    python evaluate.py
Output: confusion_matrix.png  roc_curves.png  classification_report.txt

สมาชิก:
  1. อนาวินธุ์ อักษรทิพย์         รหัส 1660701440
  2. ดฤพล กรณ์ถาวรวงศ์          รหัส 1660703974
  3. เอ็มเม็ต มีชัย แซลมอน       รหัส 1660704444
  4. ธนวัฒน์ วิเศษชัยวรรณ        รหัส 1660703990
"""

import os, sys
sys.stdout.reconfigure(encoding="utf-8")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
    roc_curve,
    auc,
)
from sklearn.preprocessing import label_binarize
import tensorflow as tf

BASE = os.path.dirname(__file__)
DATASET_DIR = os.path.join(BASE, "dataset_thai_v4", "dataset_thai_v4")
MODEL_PATH  = os.path.join(BASE, "models", "thai_model.h5")
IMG_SIZE    = 28
SEED        = 42

# ── Load dataset (same split as train.py) ─────────────────────────────────────
CLASS_NAMES   = sorted(os.listdir(DATASET_DIR))   # Thai labels e.g. ๕๖
CLASS_NUMERIC = ["56", "57", "58", "59", "60"]    # ASCII labels for charts
print("Classes:", CLASS_NAMES)

X, y = [], []
for idx, cls in enumerate(CLASS_NAMES):
    cls_dir = os.path.join(DATASET_DIR, cls)
    files = [f for f in os.listdir(cls_dir) if f.lower().endswith((".png", ".jpg"))]
    print(f"  {cls} ({idx}) — {len(files)} images")
    for fname in files:
        img = Image.open(os.path.join(cls_dir, fname)).convert("L")
        img = img.resize((IMG_SIZE, IMG_SIZE), Image.LANCZOS)
        X.append(np.array(img, dtype=np.float32) / 255.0)
        y.append(idx)

X = np.array(X).reshape(-1, IMG_SIZE, IMG_SIZE, 1)
y = np.array(y, dtype=np.int32)
print(f"Dataset: {X.shape}")

# Same 80/20 split as train.py
_, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=SEED, stratify=y)
print(f"Test set: {len(X_test)} samples")

# ── Load model ────────────────────────────────────────────────────────────────
print("\nLoading model…")
model = tf.keras.models.load_model(MODEL_PATH)
print(f"Model loaded: {MODEL_PATH}")

# ── Predict ───────────────────────────────────────────────────────────────────
y_pred_prob = model.predict(X_test, verbose=0)
y_pred      = np.argmax(y_pred_prob, axis=1)

test_loss, test_acc = model.evaluate(X_test, y_test, verbose=0)
print(f"\n=== Test Accuracy: {test_acc:.4f}  Loss: {test_loss:.4f} ===\n")

report = classification_report(y_test, y_pred, target_names=CLASS_NAMES)
print("Classification Report:")
print(report)
with open(os.path.join(BASE, "classification_report.txt"), "w", encoding="utf-8") as f:
    f.write(f"Test Accuracy: {test_acc:.4f}   Loss: {test_loss:.4f}\n\n")
    f.write(report)
print("Saved: classification_report.txt")

# ── Confusion Matrix ──────────────────────────────────────────────────────────
cm   = confusion_matrix(y_test, y_pred)
disp = ConfusionMatrixDisplay(cm, display_labels=CLASS_NUMERIC)
fig, ax = plt.subplots(figsize=(7, 6))
disp.plot(ax=ax, colorbar=False, cmap="Blues")
ax.set_title(f"Confusion Matrix  (Test Accuracy = {test_acc:.2%})", fontsize=13)
plt.tight_layout()
plt.savefig(os.path.join(BASE, "confusion_matrix.png"), dpi=150)
plt.close()
print("Saved: confusion_matrix.png")

# ── ROC / AUC ─────────────────────────────────────────────────────────────────
y_test_bin = label_binarize(y_test, classes=list(range(len(CLASS_NAMES))))
fig2, ax2 = plt.subplots(figsize=(7, 6))
colors = ["#4C8BF5", "#EA4335", "#FBBC04", "#34A853", "#FF6D00"]
for i, (cls, color) in enumerate(zip(CLASS_NUMERIC, colors)):
    fpr, tpr, _ = roc_curve(y_test_bin[:, i], y_pred_prob[:, i])
    roc_auc = auc(fpr, tpr)
    ax2.plot(fpr, tpr, color=color, lw=2, label=f"{cls}  (AUC = {roc_auc:.3f})")
ax2.plot([0, 1], [0, 1], "k--", lw=1)
ax2.set_xlim([0, 1]); ax2.set_ylim([0, 1.02])
ax2.set_xlabel("False Positive Rate", fontsize=12)
ax2.set_ylabel("True Positive Rate", fontsize=12)
ax2.set_title("ROC Curves — One-vs-Rest", fontsize=13)
ax2.legend(loc="lower right", fontsize=11)
plt.tight_layout()
plt.savefig(os.path.join(BASE, "roc_curves.png"), dpi=150)
plt.close()
print("Saved: roc_curves.png")

# ── Dataset sample images (1 per class) ───────────────────────────────────────
fig3, axes = plt.subplots(1, len(CLASS_NAMES), figsize=(10, 2.5))
for ax, cls, num in zip(axes, CLASS_NAMES, CLASS_NUMERIC):
    cls_dir = os.path.join(DATASET_DIR, cls)
    sample  = os.listdir(cls_dir)[0]
    img     = Image.open(os.path.join(cls_dir, sample)).convert("L")
    ax.imshow(img, cmap="gray")
    ax.set_title(num, fontsize=14)
    ax.axis("off")
plt.suptitle("Training Data Samples (1 per class)", fontsize=12)
plt.tight_layout()
plt.savefig(os.path.join(BASE, "dataset_samples.png"), dpi=150)
plt.close()
print("Saved: dataset_samples.png")

print("\nDone. All evaluation charts generated.")
if test_acc >= 0.80:
    print(f"[PASS] Accuracy {test_acc:.2%} meets the 80% requirement.")
else:
    print(f"[WARN] Accuracy {test_acc:.2%} is below 80%.")
