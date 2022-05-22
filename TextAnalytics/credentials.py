from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
API_KEY = 'f3544e31cd4340d593e30b88f3b8cb21'
ENDPOINT = 'https://text-analytics-demo1111.cognitiveservices.azure.com/'

def client():
    try:
        client = TextAnalyticsClient(
            endpoint=ENDPOINT,
            credential=AzureKeyCredential(API_KEY)
        )
        return client
    except Exception as e:
        print(e)
        return "Error"