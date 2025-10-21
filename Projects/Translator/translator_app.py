# Projects/Translator/translator_app.py
from flask import Blueprint, render_template, request
import requests

translator_bp = Blueprint(
    'translator_app',
    __name__,
    url_prefix='/projects/translator-app',
    template_folder='templates'
)

TRANSLATE_URL = "https://translate.googleapis.com/translate_a/single"

LANGUAGES = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese"
}

@translator_bp.route('/', methods=['GET', 'POST'])
def translator():
    translated_text = ""
    original_text = ""
    source_lang = "en"
    target_lang = "fr"

    if request.method == 'POST':
        original_text = request.form['text']
        source_lang = request.form['source_lang']
        target_lang = request.form['target_lang']

        try:
            response = requests.get(TRANSLATE_URL, params={
                "client": "gtx",
                "sl": source_lang,
                "tl": target_lang,
                "dt": "t",
                "q": original_text
            })

            if response.status_code == 200:
                translated_text = response.json()[0][0][0]
            else:
                translated_text = '[Translation failed]'
        except Exception as e:
            translated_text = f'[Error: {str(e)}]'

    return render_template('translator.html',
                           translated_text=translated_text,
                           original_text=original_text,
                           source_lang=source_lang,
                           target_lang=target_lang,
                           languages=LANGUAGES)
