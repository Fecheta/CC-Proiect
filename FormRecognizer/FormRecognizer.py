from azure.core.exceptions import ResourceNotFoundError
from azure.ai.formrecognizer import FormRecognizerClient, FormTrainingClient
from azure.core.credentials import AzureKeyCredential

API_KEY = '830a6fb237074e2986c8294d8c7b61b2'
ENDPOINT = 'https://formrecognizer1111.cognitiveservices.azure.com/'


def get_information(form_url):
    results = []
    form_recognizer_client = FormRecognizerClient(ENDPOINT, AzureKeyCredential(API_KEY))

    poller = form_recognizer_client.begin_recognize_content_from_url(form_url)
    form_result = poller.result()

    for page in form_result:
        for table in page.tables:
            results.append('Column count: {0}'.format(table.column_count))
            results.append('Row count: {0}'.format(table.row_count))
            for cell in table.cells:
                results.append('Cell Value: {0}'.format(cell.text))
                results.append('Location: {0}'.format(cell.bounding_box))
                results.append('Confidence Score: {0}'.format(cell.confidence))
    return results
