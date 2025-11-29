from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_mail import Mail, Message
import os
from dotenv import load_dotenv
import json
import hmac
import hashlib

# Load environment variables
load_dotenv()

# Initialize app only ONCE
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# 📦 Register Translator Blueprint
from Projects.Translator.translator_app import translator_bp
app.register_blueprint(translator_bp)

# 📦 Register Interview Assistant Blueprint
from Projects.InterviewAssistant.interview_assistant_app import interview_assistant_bp
app.register_blueprint(interview_assistant_bp)

# 📦 Register Civil Service matcher Blueprint
#from Projects.CivilServiceMatcher.views import matcher_bp
#app.register_blueprint(matcher_bp, url_prefix='/projects/civil-service-matcher-app')

# 📧 Gmail SMTP Config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

mail = Mail(app)

# 🌍 Page Routes
@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html', title='Portfolio of Gary Constable – experienced web developer specialising in Python, AI apps, Magento, and tools for Civil Service job seekers. View projects, try free tools, and get in touch.')

@app.route('/generic', methods=['GET', 'POST'])
def generic():
    return render_template('generic.html', title='Generic')

@app.route('/elements', methods=['GET', 'POST'])
def elements():
    return render_template('elements.html', title='Elements')

@app.route('/translator', methods=['GET', 'POST'])
def translator():
    return render_template('pages/translator.html', title='Free AI Translator | Instant Language Translation Tool – Gary Constable')

@app.route('/interview-assistant', methods=['GET', 'POST'])
def interviewAssistant():
    return render_template('pages/interview-assistant.html', title='Free Civil Service Interview STAR Answer Generator – Gary Constable')

@app.route('/civil-service-job-matcher', methods=['GET', 'POST'])
def interviewAssistantPage():
    return render_template('pages/civil-service-matcher.html', title='AI-Powered Civil Service Job Matcher | Generate STAR Responses from Your CV')

@app.route("/hire-me")
def hire_me():
    return render_template("hire-me.html")

@app.route('/downloads/civil-service-job-matcher.zip')
def download_job_matcher():
    return redirect(url_for('static', filename='downloads/CivilServiceMatcher.zip'))


# 📬 Contact Form Handler
@app.route('/contact-form', methods=['POST'])
def contact_form():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    if not name or not email or not message:
        flash('Please fill out all fields.')
        return redirect(request.referrer or url_for('home'))

    try:
        msg = Message(
            subject=f'New Contact Form Submission from {name}',
            sender=app.config['MAIL_USERNAME'],
            recipients=['garyconstable80@gmail.com'],
            body=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
        )
        mail.send(msg)
        flash('Thanks! Your message was sent.')
    except Exception as e:
        print(f"Email sending failed: {e}")
        flash('Error sending message. Please try again.')

    return redirect(request.referrer or url_for('home'))

# ❌ 404 Page
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', title='404 – Not Found'), 404

# 🐸 eBay Webhook Receiver
@app.route('/webhooks/ebay', methods=['GET', 'POST'])
def ebay_webhook():
    """
    Unified eBay webhook endpoint.
    - Handles any event eBay POSTs (listing, test ping, or account deletion)
    - Optionally verifies a shared verification token
    - Emails full payload to Gary for visibility
    """

    # --- 1️⃣ Optional token verification ---
    expected_token = os.environ.get('EBAY_WEBHOOK_VERIFICATION_TOKEN', '').strip()
    incoming_token = (
        request.args.get('verificationToken')
        or request.form.get('verificationToken')
        or (request.get_json(silent=True) or {}).get('verificationToken')
    )

    if expected_token and incoming_token and incoming_token != expected_token:
        print(f"[Webhook] Invalid verification token: {incoming_token!r}")
        return jsonify({"error": "invalid verification token"}), 403

    # --- 2️⃣ Capture all possible body formats ---
    raw_body = request.get_data(cache=False, as_text=True)
    json_body = request.get_json(silent=True)
    form_data = request.form.to_dict(flat=True)
    args_data = request.args.to_dict(flat=True)

    # --- 3️⃣ Build email body ---
    parts = []
    parts.append("🔔 eBay Webhook Received\n")
    parts.append(f"Remote IP: {request.remote_addr}\n")
    parts.append(f"Headers:\n{json.dumps(dict(request.headers), indent=2)}\n")

    if expected_token:
        parts.append(f"Token check: {'PASSED' if incoming_token == expected_token else 'SKIPPED'}\n\n")

    if json_body:
        parts.append("JSON payload:\n" + json.dumps(json_body, indent=2) + "\n\n")
    if form_data:
        parts.append("Form data:\n" + json.dumps(form_data, indent=2) + "\n\n")
    if args_data:
        parts.append("Query string:\n" + json.dumps(args_data, indent=2) + "\n\n")

    parts.append("Raw body (UTF-8 best effort):\n" + raw_body[:2000] + "\n")
    email_body = "".join(parts)

    # --- 4️⃣ Send email to you ---
    try:
        recipients_env = os.environ.get('EBAY_WEBHOOK_RECIPIENTS', '').strip()
        recipients = [r.strip() for r in recipients_env.split(',') if r.strip()] or ['garyconstable80@gmail.com']

        msg = Message(
            subject='[GhostFrog] eBay Webhook Event',
            recipients=recipients,
            body=email_body,
        )
        mail.send(msg)
        mailed = True
    except Exception as e:
        print(f"[Webhook] Email send failed: {e}")
        mailed = False

    # --- 5️⃣ Respond to eBay immediately ---
    return jsonify({"status": "ok", "mailed": mailed}), 200

# -----------------------------------------
# 📝 Simple Blog System (Markdown-based)
# -----------------------------------------
from markdown import markdown
from pathlib import Path
import re

BLOG_POSTS_DIR = Path("content/blog")


def load_post(slug: str):
    """
    Load a markdown post by slug (filename without .md)
    """
    filepath = BLOG_POSTS_DIR / f"{slug}.md"
    if not filepath.exists():
        return None

    raw = filepath.read_text(encoding="utf-8")

    # Extract optional YAML front matter
    meta = {
        "title": slug.replace("-", " ").title(),
        "date": None,
        "summary": "",
    }

    m = re.match(r"---\n(.*?)\n---\n(.*)$", raw, re.S)
    if m:
        raw_meta, content = m.groups()
        for line in raw_meta.split("\n"):
            if ":" in line:
                key, val = line.split(":", 1)
                meta[key.strip()] = val.strip().strip('"')
    else:
        content = raw

    html_content = markdown(content)

    return {"meta": meta, "content": html_content, "slug": slug}


def list_posts():
    posts = []
    for file in BLOG_POSTS_DIR.glob("*.md"):
        slug = file.stem
        post = load_post(slug)
        if post:
            posts.append(post)
    # newest first
    posts.sort(key=lambda p: p["meta"].get("date", ""), reverse=True)
    return posts


@app.route("/blog")
def blog_index():
    posts = list_posts()
    return render_template(
        "blog/index.html",
        posts=posts,
        title="Blog – AI, Python, Magento, Agentic Systems | Gary Constable"
    )


@app.route("/blog/<slug>")
def blog_post(slug):
    post = load_post(slug)
    if not post:
        return render_template("404.html"), 404

    return render_template(
        "blog/post.html",
        post=post,
        title=post["meta"]["title"] + " – Blog | Gary Constable"
    )

# 🚀 Run the App
if __name__ == '__main__':
    app.run(debug=True)
