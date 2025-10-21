from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
import os
from dotenv import load_dotenv

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

# 🚀 Run the App
if __name__ == '__main__':
    app.run(debug=True)
