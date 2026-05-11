# CS462 — Thai Handwritten Numeral Recognition Web Application
# กลุ่ม: VibeCode101 เลขไทย ๕๖–๖๐
# สมาชิก:
#   1. อนาวินธุ์ อักษรทิพย์         รหัส 1660701440
#   2. ดฤพล กรณ์ถาวรวงศ์         รหัส 1660703974
#   3. เอ็มเม็ต มีชัย แซลมอน       รหัส 1660704444
#   4. ธนวัฒน์ วิเศษชัยวรรณ        รหัส 1660703990

import os
import io
import base64
import numpy as np
import cv2
from flask import Flask, render_template, request, jsonify
from PIL import Image

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import tensorflow as tf

app = Flask(__name__)

CLASS_LABELS = ["๕๖", "๕๗", "๕๘", "๕๙", "๖๐"]
CLASS_NUMERIC = ["56", "57", "58", "59", "60"]
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "thai_ultimate_model_v4.h5")

_active_model = None
_model_info = {}


class _PatchedDense(tf.keras.layers.Dense):
    def __init__(self, *args, **kwargs):
        kwargs.pop("quantization_config", None)
        super().__init__(*args, **kwargs)


def load_original_model():
    global _active_model, _model_info
    _active_model = tf.keras.models.load_model(
        MODEL_PATH, custom_objects={"Dense": _PatchedDense}
    )
    _model_info = {
        "name": os.path.basename(MODEL_PATH),
        "is_original": True,
        "input_shape": str(_active_model.input_shape),
        "output_classes": len(CLASS_LABELS),
    }
    print(f"[OK] Loaded original model — input {_active_model.input_shape}")


def preprocess_canvas(image_data: str) -> np.ndarray:
    if "," in image_data:
        image_data = image_data.split(",")[1]
    raw = base64.b64decode(image_data)
    img = Image.open(io.BytesIO(raw)).convert("RGBA")

    # Composite on black background → grayscale
    bg = Image.new("RGBA", img.size, (0, 0, 0, 255))
    gray_np = np.array(Image.alpha_composite(bg, img).convert("L"), dtype=np.uint8)

    # Invert if background is light
    if gray_np.mean() > 127:
        gray_np = cv2.bitwise_not(gray_np)

    # Match Gradio inference preprocessing exactly:
    # binarize → thin strokes → single-step resize to 28×28
    _, gray_np = cv2.threshold(gray_np, 40, 255, cv2.THRESH_BINARY)
    kernel = np.ones((2, 2), np.uint8)
    gray_np = cv2.erode(gray_np, kernel, iterations=1)
    gray_np = cv2.resize(gray_np, (28, 28))  # INTER_LINEAR (cv2 default)

    arr = gray_np.astype(np.float32) / 255.0
    return arr.reshape(1, 28, 28, 1)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/admin")
def admin():
    return render_template("admin.html", model_info=_model_info)


@app.route("/api/model_info")
def api_model_info():
    return jsonify(_model_info)


@app.route("/api/predict", methods=["POST"])
def predict():
    data = request.get_json(force=True)
    if not data or "image" not in data:
        return jsonify({"error": "No image data provided"}), 400

    try:
        arr = preprocess_canvas(data["image"])

        # Return 28x28 preview so the frontend can show what the model sees
        preview_arr = (arr.reshape(28, 28) * 255).astype(np.uint8)
        preview_img = Image.fromarray(preview_arr, mode="L")
        # Scale up to 112x112 for readability
        preview_img = preview_img.resize((112, 112), Image.NEAREST)
        buf = io.BytesIO()
        preview_img.save(buf, format="PNG")
        preview_b64 = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

        preds = _active_model.predict(arr, verbose=0)[0]

        idx = int(np.argmax(preds))
        all_preds = [
            {
                "label": CLASS_LABELS[i],
                "numeric": CLASS_NUMERIC[i],
                "confidence": round(float(preds[i]), 4),
            }
            for i in range(len(CLASS_LABELS))
        ]

        return jsonify(
            {
                "predicted_label": CLASS_LABELS[idx],
                "predicted_numeric": CLASS_NUMERIC[idx],
                "confidence": round(float(preds[idx]), 4),
                "all_predictions": all_preds,
                "preview": preview_b64,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/upload_model", methods=["POST"])
def upload_model():
    global _active_model, _model_info

    if "model" not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file = request.files["model"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not (file.filename.endswith(".h5") or file.filename.endswith(".keras")):
        return jsonify({"error": "Only .h5 or .keras files are accepted"}), 400

    try:
        import tempfile
        suffix = ".keras" if file.filename.endswith(".keras") else ".h5"
        tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        file.save(tmp.name)
        tmp.close()
        new_model = tf.keras.models.load_model(
            tmp.name, custom_objects={"Dense": _PatchedDense}
        )
        os.unlink(tmp.name)

        out_classes = new_model.output_shape[-1]
        if out_classes != len(CLASS_LABELS):
            return jsonify(
                {
                    "error": (
                        f"Model has {out_classes} output classes; "
                        f"expected {len(CLASS_LABELS)}"
                    )
                }
            ), 400

        _active_model = new_model
        _model_info = {
            "name": file.filename,
            "is_original": False,
            "input_shape": str(_active_model.input_shape),
            "output_classes": out_classes,
        }

        return jsonify(
            {
                "success": True,
                "message": (
                    f'Model "{file.filename}" loaded successfully. '
                    "Note: this model lives in memory only — "
                    "restarting the server reverts to the original."
                ),
                "model_info": _model_info,
            }
        )
    except Exception as e:
        return jsonify({"error": f"Failed to load model: {e}"}), 500


@app.route("/api/reset_model", methods=["POST"])
def reset_model():
    load_original_model()
    return jsonify({"success": True, "message": "Reverted to original model.", "model_info": _model_info})


if __name__ == "__main__":
    print("Loading model…")
    load_original_model()
    print("Starting server on http://localhost:5000")
    import threading, webbrowser
    threading.Timer(1.0, lambda: webbrowser.open("http://localhost:5000")).start()
    app.run(debug=False, port=5000)
