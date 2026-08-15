# 🥗 AI Nutrition Coach

A GenAI-powered, image-based web application that analyzes a photo of your
meal and returns an instant nutrition breakdown — estimated calories, a
macronutrient split, and a personalized health tip — powered by IBM
watsonx.ai's Granite Vision model.

## Features

- 📸 Upload a photo of any meal directly from the browser
- 🧠 Vision-language model analysis via IBM watsonx.ai (Granite Vision)
- 🔢 Structured breakdown: identified foods, calories, macros, and a health tip
- 📝 Optional notes field (e.g. portion size, dietary goals) to personalize results
- ⚡ Simple Flask + Jinja frontend, no JavaScript framework required

## Tech Stack

| Layer          | Technology                          |
|----------------|--------------------------------------|
| Backend        | Python, Flask                        |
| AI / LLM       | IBM watsonx.ai — Granite Vision      |
| Image handling | Pillow                               |
| Frontend       | HTML, CSS (vanilla), Jinja2 templates|
| Response format| Markdown rendered to HTML            |

## Project Structure

```
ai-nutrition-coach/
├── app.py                # Flask app & watsonx.ai integration
├── requirements.txt      # Python dependencies
├── .env.example           # Template for required environment variables
├── templates/
│   └── index.html        # Main page (upload form + results)
└── static/
    └── style.css          # App styling
```

## Setup

### 1. Clone and install dependencies

```bash
git clone https://github.com/<your-username>/ai-nutrition-coach.git
cd ai-nutrition-coach
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment variables

Copy `.env.example` to `.env` and fill in your IBM watsonx.ai credentials:

```bash
cp .env.example .env
```

| Variable            | Description                                              |
|---------------------|------------------------------------------------------------|
| `FLASK_SECRET_KEY`  | Any random string, used to sign session/flash messages     |
| `WATSONX_API_KEY`   | Your IBM Cloud API key                                      |
| `WATSONX_PROJECT_ID`| Your watsonx.ai project ID                                  |
| `WATSONX_URL`       | Region endpoint (default: `us-south.ml.cloud.ibm.com`)      |
| `WATSONX_MODEL_ID`  | Vision model to use (default: `ibm/granite-vision-3-2-2b`)  |

You'll need an [IBM Cloud account](https://cloud.ibm.com) with watsonx.ai
access and a project set up in [watsonx.ai](https://dataplatform.cloud.ibm.com/wx).

### 3. Run the app

```bash
python app.py
```

Visit `http://127.0.0.1:5000` in your browser.

## How It Works

1. The user uploads a photo of their meal and optionally adds notes.
2. `app.py` resizes and base64-encodes the image.
3. The image + a structured prompt are sent to IBM watsonx.ai's Granite
   Vision model via a chat-style multimodal request.
4. The model's Markdown response is converted to HTML and rendered in the
   `result` section alongside the uploaded image preview.

## Deployment

The app is production-ready with `gunicorn`, included in
`requirements.txt`:

```bash
gunicorn app:app
```

Deployable to any platform that supports Python/Flask (Render, Railway,
IBM Cloud Code Engine, etc.). Remember to set the environment variables
listed above in your hosting platform's dashboard rather than committing
`.env` to source control.

## Roadmap / Ideas

- [ ] Store meal history per user (add a database)
- [ ] Daily calorie/macro tracking dashboard
- [ ] Support for multiple images per meal (e.g. plate + label)
- [ ] Export nutrition report as PDF

## License

MIT — feel free to fork and adapt.
