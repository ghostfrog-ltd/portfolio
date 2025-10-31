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
from Projects.CivilServiceMatcher.views import matcher_bp
app.register_blueprint(matcher_bp, url_prefix='/projects/civil-service-matcher-app')

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
@app.route('/webhooks/ebay', methods=['POST', 'GET'])
def ebay_webhook():
    """
    Endpoint that eBay calls.
    We grab the payload, optionally verify, then email it to you.
    Returns 200 immediately so eBay doesn't retry forever.
    """

    # 1. Raw body (bytes) in case we later want signature verification
    raw_body = request.get_data(cache=False, as_text=False)

    # 2. Try JSON first
    data_json = None
    try:
        data_json = request.get_json(silent=True)
    except Exception:
        data_json = None

    # 3. Fallback to form / query data
    form_data = request.form.to_dict(flat=True)
    args_data = request.args.to_dict(flat=True)

    # 4. Build a readable dump for the email body
    parts = []

    parts.append("🔔 eBay Webhook Hit\n")
    parts.append(f"Remote IP: {request.remote_addr}\n")
    parts.append(f"Headers:\n{json.dumps(dict(request.headers), indent=2)}\n")

    if data_json is not None:
        parts.append("JSON payload:\n")
        parts.append(json.dumps(data_json, indent=2))
        parts.append("\n")
    else:
        parts.append("JSON payload: <none or invalid JSON>\n")

    if form_data:
        parts.append("Form data:\n")
        parts.append(json.dumps(form_data, indent=2))
        parts.append("\n")

    if args_data:
        parts.append("Query string args:\n")
        parts.append(json.dumps(args_data, indent=2))
        parts.append("\n")

    # raw fallback
    parts.append("Raw body bytes (utf-8 best effort):\n")
    try:
        parts.append(raw_body.decode('utf-8', errors='replace'))
    except Exception:
        parts.append("<could not decode raw body as utf-8>")
    parts.append("\n")

    email_body = "\n".join(parts)

    # 5. Optional: verify signature if you configure it
    # eBay can sign callbacks depending on which webhook product you're using.
    # We'll wire the scaffold so you can turn it on later without touching the route.
    verification_note = ""
    try:
        expected_sig = os.environ.get('EBAY_WEBHOOK_SIGNATURE')  # shared secret YOU set
        header_sig = request.headers.get('X-Ebay-Signature')

        if expected_sig and header_sig:
            # Example HMAC-SHA256 check (you may need to adjust based on eBay spec)
            digest = hmac.new(
                expected_sig.encode('utf-8'),
                raw_body,
                hashlib.sha256
            ).hexdigest()

            if hmac.compare_digest(digest, header_sig):
                verification_note = "[OK] signature matched"
            else:
                verification_note = "[WARN] signature mismatch"
        else:
            verification_note = "[INFO] signature not checked (missing secret or header)"
    except Exception as sig_err:
        verification_note = f"[ERR] signature check error: {sig_err}"

    email_body = verification_note + "\n\n" + email_body

    # 6. Send email to you
    try:
        msg = Message(
            subject='[GhostFrog] eBay Webhook Event',
            sender=app.config['MAIL_USERNAME'],
            recipients=['garyconstable80@gmail.com', 'info@ghostfrog.co.uk'],
            body=email_body
        )
        mail.send(msg)
        mailed = True
    except Exception as e:
        print(f"[Webhook] Email send failed: {e}")
        mailed = False

    # 7. Return JSON so eBay gets a clean 200
    return jsonify({
        "status": "ok",
        "mailed": mailed,
        "note": verification_note
    }), 200


# 🚀 Run the App
if __name__ == '__main__':
    app.run(debug=True)
