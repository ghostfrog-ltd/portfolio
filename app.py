from flask import Flask, render_template, send_from_directory
import os

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')

    @app.after_request
    def add_header(response):
        if 'Cache-Control' not in response.headers:
            response.headers['Cache-Control'] = 'public, max-age=3600'
        return response

    @app.route('/')
    def home():
        return render_template('index.html')

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(
            os.path.join(app.root_path, 'static'),
            'favicon.ico',
            mimetype='image/vnd.microsoft.icon'
        )

    return app

# 👇 add this so `gunicorn app:app` works
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5050)), debug=True)
