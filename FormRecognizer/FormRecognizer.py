from azure.core.exceptions import ResourceNotFoundError
from azure.ai.formrecognizer import FormRecognizerClient, FormTrainingClient
from azure.core.credentials import AzureKeyCredential
from PdfCreator import pdfconv

API_KEY = '82cd94b78bdb45c7b5166be1a214701c'
ENDPOINT = 'https://proiectcc-formrecognizer.cognitiveservices.azure.com/'


def get_information_from_table(table_url):
    results = []
    form_recognizer_client = FormRecognizerClient(ENDPOINT, AzureKeyCredential(API_KEY))

    poller = form_recognizer_client.begin_recognize_content_from_url(table_url)
    form_result = poller.result()

    for page in form_result:
        temp = []
        for table in page.tables:
            temp.append('Column count: {0}'.format(table.column_count))
            temp.append('Row count: {0}'.format(table.row_count))
            for cell in table.cells:
                temp.append('Cell Value: {0}'.format(cell.text))
                #temp.append('Location: {0}'.format(cell.bounding_box))
                temp.append('Confidence Score: {0}'.format(cell.confidence))
            results.append(temp)
    return results


def get_information_from_receipt(receipt_url):
    form_recognizer_client = FormRecognizerClient(ENDPOINT, AzureKeyCredential(API_KEY))
    poller = form_recognizer_client.begin_recognize_receipts_from_url(receipt_url)
    result = poller.result()
    results = []
    for receipt in result:
        print(receipt.form_type)
        for name, field in receipt.fields.items():
            temp = []
            if name == 'Items':
                temp.append('Purchase Item')
                for index, item in enumerate(field.value):
                    temp.append('\t\t\t\t\tItem #{0}'.format(index + 1))
                    for item_name, item in item.value.items():
                        temp.append('\t\t\t\t\tItem name: {0}  Item Value: {1}  Confidence{2}'.format(item_name, item.value, item.confidence))
            else:
                temp.append('{0}: {1} - Confidence: {2}'.format(name, field.value, field.confidence))
            results.append(temp)
    return results


def extract_invoice_field_value(invoice, field_name):
    results = []
    try:
        if field_name == 'Items':
            for item in invoice.fields.get('Items').value:
                for key in item.value.keys():
                    results.append('Item:')
                    results.append('\t\t\t' + str(key))
                    results.append('-'*25)
                    results.append('\t\t\t' + str(item.value.get(key).value) + '|' + str(item.value.get(key).confidence))
        else:
            results.append(field_name)
            results.append('-' * 25)
            results.append(str(invoice.fields.get(field_name)) + '|' + str(invoice.fields.get(field_name).confidence))
    except AttributeError:
        results.append('Nothing is found')
    return results


def get_information_from_invoice(invoice_url):
    form_recognizer_client = FormRecognizerClient(ENDPOINT, AzureKeyCredential(API_KEY))
    poller = form_recognizer_client.begin_recognize_invoices_from_url(invoice_url)
    result = poller.result()

    result[0].fields.keys()
    results = []
    if poller.status() == 'succeeded':
        for page in result:
            field_keys = page.fields.keys()
            for field_key in field_keys:
                results.append(extract_invoice_field_value(page, field_key))
    print('gata')
    return results
