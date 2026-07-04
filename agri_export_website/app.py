from flask import Flask, render_template, request, make_response, redirect, url_for
from translations import TRANSLATIONS

app = Flask(__name__)

@app.route("/set-lang/<lang>")
def set_language(lang):
    referrer = request.referrer or url_for('home')
    response = make_response(redirect(referrer))
    if lang in TRANSLATIONS:
        response.set_cookie('lang', lang, max_age=30*24*60*60)
    return response

@app.context_processor
def inject_translate():
    lang = request.cookies.get('lang', 'en')
    if lang not in TRANSLATIONS:
        lang = 'en'
    def translate(key):
        return TRANSLATIONS[lang].get(key, TRANSLATIONS['en'].get(key, key))
    return dict(t=translate, current_lang=lang)

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)