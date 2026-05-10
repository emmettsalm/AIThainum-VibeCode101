"""
CS462 — Thai Digit Classifier — Training Script
Classes: ๕๖ ๕๗ ๕๘ ๕๙ ๖๐  (56–60)
Run:    python train.py
Output: models/thai_model.h5  +  evaluation charts

สมาชิก:
  1. อนาวินธุ์ อักษรทิพย์         รหัส 1660701440
  2. ดฤพล กรณ์ถาวรวงศ์          รหัส 1660703974
  3. เอ็มเม็ต มีชัย แซลมอน       รหัส 1660704444
  4. ธนวัฒน์ วิเศษชัยวรรณ        รหัส 1660703990
"""

import os
import sys
sys.stdout.reconfigure(encoding="utf-8")

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import numpy as np
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
from tensorflow.keras import layers, models, callbacks

# ── Config ────────────────────────────────────────────────────────────────────
DATASET_DIR = os.path.join(
    os.path.dirname(__file__),
    "dataset_thai_v4",
    "dataset_thai_v4",
)
MODEL_OUT = os.path.join(os.path.dirname(__file__), "models", "thai_model.h5")
IMG_SIZE = 28
BATCH = 64
EPOCHS = 30
SEED = 42

CLASS_NAMES_SORTED = sorted(os.listdir(DATASET_DIR))   # Unicode-sorted → consistent indices
CLASS_NUMERIC = ["56", "57", "58", "59", "60"]
print("Class order:", CLASS_NAMES_SORTED)

# ── Load data ─────────────────────────────────────────────────────────────────
X, y = [], []
for idx, cls in enumerate(CLASS_NAMES_SORTED):
    cls_dir = os.path.join(DATASET_DIR, cls)
    files = [f for f in os.listdir(cls_dir) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    print(f"  {cls}  ({idx}) — {len(files)} images")
    for fname in files:
        img = Image.open(os.path.join(cls_dir, fname)).convert("L")
        img = img.resize((IMG_SIZE, IMG_SIZE), Image.LANCZOS)
        arr = np.array(img, dtype=np.float32) / 255.0
        X.append(arr)
        y.append(idx)

X = np.array(X).reshape(-1, IMG_SIZE, IMG_SIZE, 1)
y = np.array(y, dtype=np.int32)
print(f"\nDataset: {X.shape}  labels: {y.shape}")

# ── Split ──────────────────────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=SEED, stratify=y
)
X_train, X_val, y_train, y_val = train_test_split(
    X_train, y_train, test_size=0.1, random_state=SEED, stratify=y_train
)
print(f"Train: {len(X_train)}  Val: {len(X_val)}  Test: {len(X_test)}")

# ── CNN model ─────────────────────────────────────────────────────────────────
def build_model(num_classes: int):
    m = models.Sequential([
        layers.Input(shape=(IMG_SIZE, IMG_SIZE, 1)),

        layers.Conv2D(32, 3, padding="same", activation="relu"),
        layers.BatchNormalization(),
        layers.MaxPooling2D(2),
        layers.Dropout(0.25),

        layers.Conv2D(64, 3, padding="same", activation="relu"),
        layers.BatchNormalization(),
        layers.MaxPooling2D(2),
        layers.Dropout(0.25),

        layers.Conv2D(128, 3, padding="same", activation="relu"),
        layers.BatchNormalization(),
        layers.Dropout(0.3),

        layers.GlobalAveragePooling2D(),
        layers.Dense(256, activation="relu"),
        layers.Dropout(0.5),
        layers.Dense(num_classes, activation="softmax"),
    ])
    m.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return m


model = build_model(len(CLASS_NAMES_SORTED))
model.summary()

# ── Augmentation ──────────────────────────────────────────────────────────────
datagen = tf.keras.preprocessing.image.ImageDataGenerator(
    rotation_range=10,
    width_shift_range=0.1,
    height_shift_range=0.1,
    zoom_range=0.1,
)
datagen.fit(X_train)

# ── Train ─────────────────────────────────────────────────────────────────────
cb = [
    callbacks.EarlyStopping(patience=5, restore_best_weights=True, monitor="val_accuracy"),
    callbacks.ReduceLROnPlateau(factor=0.5, patience=3, verbose=1),
]

history = model.fit(
    datagen.flow(X_train, y_train, batch_size=BATCH),
    validation_data=(X_val, y_val),
    epochs=EPOCHS,
    callbacks=cb,
    verbose=1,
)

# ── Evaluate ──────────────────────────────────────────────────────────────────
test_loss, test_acc = model.evaluate(X_test, y_test, verbose=0)
print(f"\n=== Test Accuracy: {test_acc:.4f}  Loss: {test_loss:.4f} ===")

y_pred_prob = model.predict(X_test, verbose=0)
y_pred = np.argmax(y_pred_prob, axis=1)

print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=CLASS_NAMES_SORTED))

# Confusion matrix
cm = confusion_matrix(y_test, y_pred)
disp = ConfusionMatrixDisplay(cm, display_labels=CLASS_NAMES_SORTED)
fig, ax = plt.subplots(figsize=(7, 6))
disp.plot(ax=ax, colorbar=False)
ax.set_title(f"Confusion Matrix  (acc={test_acc:.2%})")
plt.tight_layout()
plt.savefig(os.path.join(os.path.dirname(__file__), "confusion_matrix.png"), dpi=150)
print("Saved: confusion_matrix.png")

# ROC / AUC (one-vs-rest)
y_test_bin = label_binarize(y_test, classes=list(range(len(CLASS_NAMES_SORTED))))
fig2, ax2 = plt.subplots(figsize=(7, 6))
for i, cls in enumerate(CLASS_NAMES_SORTED):
    fpr, tpr, _ = roc_curve(y_test_bin[:, i], y_pred_prob[:, i])
    roc_auc = auc(fpr, tpr)
    ax2.plot(fpr, tpr, label=f"{cls} (AUC={roc_auc:.2f})")
ax2.plot([0, 1], [0, 1], "k--")
ax2.set_xlabel("False Positive Rate")
ax2.set_ylabel("True Positive Rate")
ax2.set_title("ROC Curves (one-vs-rest)")
ax2.legend()
plt.tight_layout()
plt.savefig(os.path.join(os.path.dirname(__file__), "roc_curves.png"), dpi=150)
print("Saved: roc_curves.png")

# Training history
fig3, (ax3, ax4) = plt.subplots(1, 2, figsize=(12, 4))
ax3.plot(history.history["accuracy"], label="train")
ax3.plot(history.history["val_accuracy"], label="val")
ax3.set_title("Accuracy")
ax3.legend()
ax4.plot(history.history["loss"], label="train")
ax4.plot(history.history["val_loss"], label="val")
ax4.set_title("Loss")
ax4.legend()
plt.tight_layout()
plt.savefig(os.path.join(os.path.dirname(__file__), "training_history.png"), dpi=150)
print("Saved: training_history.png")

# ── Save model ────────────────────────────────────────────────────────────────
os.makedirs(os.path.dirname(MODEL_OUT), exist_ok=True)
model.save(MODEL_OUT)
print(f"\nModel saved → {MODEL_OUT}")

if test_acc >= 0.80:
    print(f"[PASS] Accuracy {test_acc:.2%} meets the 80% requirement.")
else:
    print(f"[WARN] Accuracy {test_acc:.2%} is below 80%. Consider more data or tuning.")
