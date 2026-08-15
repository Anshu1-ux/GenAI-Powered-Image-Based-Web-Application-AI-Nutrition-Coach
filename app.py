"""
AI Nutrition Coach
------------------
A Flask web app that lets a user upload a photo of their meal and receive
an AI-generated nutrition breakdown (calories, macros, and a health tip)
using an IBM watsonx.ai Granite Vision model.
"""

import base64
import os
from io import BytesIO

import markdown
from flask import Flask, flash, redirect, render_template, request, url_for
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from PIL import Image

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")

# --- IBM watsonx.ai configuration (set these as environment variables) -----
WATSONX_API_KEY = os.environ.get("WATSONX_API_KEY")
WATSONX_PROJECT_ID = os.environ.get("WATSONX_PROJECT_ID")
WATSONX_URL = os.environ.get("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
WATSONX_MODEL_ID = os.environ.get("WATSONX_MODEL_ID", "ibm/granite-vision-3-2-2b")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
MAX_IMAGE_DIMENSION = 1024  # keep uploads reasonably sized before sending to the model


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def image_to_base64(file_storage) -> str:
    """Resize (if needed) and convert an uploaded image to a base64 JPEG string."""
    img = Image.open(file_storage).convert("RGB")
    img.thumbnail((MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION))
    buffer = BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def get_nutrition_analysis(image_b64: str, user_notes: str = "") -> str:
    """Send the image to watsonx.ai Granite Vision and return a Markdown response."""
    if not WATSONX_API_KEY or not WATSONX_PROJECT_ID:
        raise RuntimeError(
            "WATSONX_API_KEY and WATSONX_PROJECT_ID must be set as environment variables."
        )

    credentials = Credentials(url=WATSONX_URL, api_key=WATSONX_API_KEY)
    model = ModelInference(
        model_id=WATSONX_MODEL_ID,
        credentials=credentials,
        project_id=WATSONX_PROJECT_ID,
        params={"max_new_tokens": 600, "temperature": 0.3},
    )

    prompt_text = (
        "You are an AI nutrition coach. Look closely at the food in this image "
        "and respond in Markdown with the following sections:\n"
        "### Identified Food Items\n"
        "### Estimated Calories\n"
        "### Macronutrient Breakdown (protein, carbs, fat)\n"
        "### Health Tip\n"
        "Keep it concise and use bullet points where helpful."
    )
    if user_notes:
        prompt_text += f"\n\nAdditional context from the user: {user_notes}"

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt_text},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"},
                },
            ],
        }
    ]

    response = model.chat(messages=messages)
    return response["choices"][0]["message"]["content"]


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    if "food_image" not in request.files or request.files["food_image"].filename == "":
        flash("Please select an image to upload.")
        return redirect(url_for("index"))

    file = request.files["food_image"]
    user_notes = request.form.get("notes", "").strip()

    if not allowed_file(file.filename):
        flash("Unsupported file type. Please upload a PNG, JPG, or WEBP image.")
        return redirect(url_for("index"))

    try:
        image_b64 = image_to_base64(file)
        raw_markdown = get_nutrition_analysis(image_b64, user_notes)
        response_html = markdown.markdown(raw_markdown)
    except Exception as exc:  # noqa: BLE001 - surface any failure to the user
        flash(f"Something went wrong while analyzing your image: {exc}")
        return redirect(url_for("index"))

    return render_template(
        "index.html",
        response_html=response_html,
        image_preview=f"data:image/jpeg;base64,{image_b64}",
    )


if __name__ == "__main__":
    app.run(debug=True)
