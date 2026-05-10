import sys, os
sys.stdout.reconfigure(encoding='utf-8')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
from PIL import Image
import numpy as np
import tensorflow as tf

BASE = os.path.dirname(os.path.abspath(__file__))
model = tf.keras.models.load_model(os.path.join(BASE, "models", "thai_ultimate_model_v4.h5"))
folder = os.path.join(BASE, "dataset_thai_v4", "dataset_thai_v4")
classes = sorted(os.listdir(folder))
labels = ['56','57','58','59','60']

print("Average confidence per class (100 training samples):")
print(f"{'True':>4} | {' | '.join(f'{l:>5}' for l in labels)}")
print("-" * 45)
for true_idx, cls in enumerate(classes):
    files = os.listdir(os.path.join(folder, cls))[:100]
    conf_sum = np.zeros(5)
    for f in files:
        arr = np.array(Image.open(os.path.join(folder, cls, f)).convert('L'), dtype=np.float32) / 255.0
        conf_sum += model.predict(arr.reshape(1, 28, 28, 1), verbose=0)[0]
    conf_avg = conf_sum / len(files)
    row = " | ".join(f"{conf_avg[i]:5.2f}" for i in range(5))
    print(f"{labels[true_idx]:>4} | {row}  <- predicted {labels[conf_avg.argmax()]}")
