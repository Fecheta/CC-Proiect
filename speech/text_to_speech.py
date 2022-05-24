import io
import uuid

import azure.cognitiveservices.speech as speechsdk
from wtforms import StringField, RadioField, SelectField, TextAreaField, DateTimeField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm

from storage import Storage
from translate.translate import Translate
import requests


class TextToSpeech:
    def __init__(self):
        self.key = '636a7aca815f4814833e561fd4da33f2'
        # self.key = self.get_key()
        self.location = "northeurope"
        self.endpoint = "https://northeurope.tts.speech.microsoft.com/cognitiveservices/v1"

    def tts(self, text):
        params = {
            'api-version': '3.0',
        }

        headers = {
            'Ocp-Apim-Subscription-Key': self.key,
            'Ocp-Apim-Subscription-Region': self.location,
            'Content-type': 'application/ssml+xml',
            'X-Microsoft-OutputFormat': 'audio-24khz-96kbitrate-mono-mp3',
            'User_Agent': 'Documents Assistant'
        }

        detector = Translate()
        detected_language = detector.detect(text)

        voice = f"voice xml:lang='en-US' xml:gender='Male' name='en-US-ChristopherNeural'"

        if detected_language == 'ro':
            voice = f"voice xml:lang='ro-RO' xml:gender='Female' name='Microsoft Server Speech Text to Speech Voice (ro-RO, AlinaNeural)'"
        elif detected_language == 'de':
            voice = f"voice xml:lang='de-DE' xml:gender='Male' name='Microsoft Server Speech Text to Speech Voice (de-DE, ConradNeural)'"
        elif detected_language == 'es':
            voice = f"voice xml:lang='es-ES' xml:gender='Female' name='Microsoft Server Speech Text to Speech Voice (es-ES, ElviraNeural)'"
        elif detected_language == 'it':
            voice = f"voice xml:lang='it-IT' xml:gender='Male' name='Microsoft Server Speech Text to Speech Voice (it-IT, DiegoNeural)'"
        elif detected_language == 'fr':
            voice = f"voice xml:lang='fr-BE' xml:gender='Female' name='Microsoft Server Speech Text to Speech Voice (fr-BE, CharlineNeural)'"

        # You can pass more than one object in body.
        body = f"<speak version='1.0' xml:lang='en-US'><{voice}> {text} </voice></speak>"
        request = requests.post(self.endpoint, params=params, headers=headers, data=body.encode('utf-8'))
        f = open("static/speech.mp3", "wb")
        f.write(request.content)
        f.close()

        storage = Storage.storage('audio')
        storage.change_container('audio')
        name = 'audio' + str(uuid.uuid1()) + '.mp3'
        storage.upload_file_stream(io.BytesIO(request.content), name)

        return name


