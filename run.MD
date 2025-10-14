# 1) Unzip into ghostfrog-python (so app.py sits at project root)
unzip ghostfrog_flask_site.zip -d ghostfrog-python
cd ghostfrog-python

# 2) Create & activate venv
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3) Install deps
pip install -r requirements.txt

# 4) Run
python app.py
# Open http://localhost:5000