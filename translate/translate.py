import requests, uuid, json
from key_vault_secrets import get_secret


class Translate:

    def __init__(self):
        self.key = 'd8261ea3fa0e46fcbfcaa2f40579978f'
        # self.key = self.get_key()
        self.location = "northeurope"
        self.endpointTranslate = "https://api.cognitive.microsofttranslator.com/translate"
        self.endpointDetect = "https://api.cognitive.microsofttranslator.com/detect"

    def get_key(self):
        key = get_secret('translate-key')
        return key

    def translate(self, text, toLanguage):
        params = {
            'api-version': '3.0',
            'to': [toLanguage]
        }

        headers = {
            'Ocp-Apim-Subscription-Key': self.key,
            'Ocp-Apim-Subscription-Region': self.location,
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }

        # You can pass more than one object in body.
        body = [{
            'text': f"{text}"
        }]

        request = requests.post(self.endpointTranslate, params=params, headers=headers, json=body)
        response = request.json()
        print(response)

        return response

    def detect(self, text):
        params = {
            'api-version': '3.0'
        }

        headers = {
            'Ocp-Apim-Subscription-Key': self.key,
            'Ocp-Apim-Subscription-Region': self.location,
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }

        # You can pass more than one object in body.
        body = [{
            'text': f"{text}"
        }]

        request = requests.post(self.endpointDetect, params=params, headers=headers, json=body)
        response = request.json()
        print(response)
        if response[0]['score'] > 0.9:
            language = response[0]['language']
        else:
            language = 'en'
        return language
