from flask import Flask, render_template, request, redirect

from translate.translate import Translate



app = Flask(__name__)


@app.route('/translate', methods=['GET', 'POST'])
def translate():
    if request.method == "GET":
        return render_template('translate.html')
    if request.method == "POST":
        text = request.form["text"]
        to_language = request.form["select"]
        translation = Translate()
        result = translation.translate(text, toLanguage=to_language)
        return render_template('translate.html', result=result)
    return render_template('translate.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
