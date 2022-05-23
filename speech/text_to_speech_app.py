from flask import Flask, render_template, request, redirect

from FormRecognizer import FormRecognizer
from database.query import Query
from storage import Storage
from computer_vision import ComputerVision
from TextAnalytics import TextAnalytics
from translate.translate import Translate
from speech import text_to_speech
from speech.text_to_speech import TextToSpeech


app = Flask(__name__)
app.config["SECRET_KEY"] = "mysecretkey"


@app.route('/texttospeech', methods=("GET", "POST"))
def text_to_speech_page():
    if request.method == "GET":
        return render_template('speech.html')
    if request.method == "POST":
        text = request.form["text"]
        textts = TextToSpeech()
        textts.tts(text)
        return redirect('/tts_result')
    return render_template('speech.html')


@app.route('/tts_result', methods=["GET"])
def get_speech():
    if request.method == "GET":
        return render_template('speech_result.html')
    return render_template('speech_result.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
