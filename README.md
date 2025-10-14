# GhostFrog Flask Site

Simple Flask app to serve a static personal site.

## Local dev

```bash
cd ghostfrog-python   # if this repo is your working folder
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
# open http://localhost:5000
```

## Render deploy (quick)

1. Create a new **Web Service**.
2. Connect repo / or upload these files.
3. Set **Build Command**: `pip install -r requirements.txt`
4. Set **Start Command**: `gunicorn app:create_app() --bind 0.0.0.0:$PORT --workers 2 --threads 4`
5. Choose a Python runtime (e.g., Python 3.12).

## Project layout

```
.
├── app.py
├── requirements.txt
├── Procfile
├── static/
│   ├── styles.css
│   └── avatar-placeholder.png
└── templates/
    └── index.html
```

Replace `avatar-placeholder.png` with your own image and tweak `templates/index.html` and `static/styles.css` as needed.
