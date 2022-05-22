import os
import io
import time

from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes, VisualFeatureTypes
import requests
from PIL import Image, ImageDraw

from storage import Storage


class ComputerVision:
    def __init__(self):
        self.API_key = '4af7d629eaf04c24aaa3099a37dd45e9'
        self.endpoint = 'https://cvhandwr.cognitiveservices.azure.com/'
        self.cv_client = self.init()

    def init(self):
        cv_client = ComputerVisionClient(self.endpoint, CognitiveServicesCredentials(self.API_key))

        return cv_client

    def identify_text_from_local_file(self, image_path):
        with open(image_path, 'rb') as image:
            response = self.cv_client.read_in_stream(
                image,
                Language='en',
                raw=True
            )

        operation_location = response.headers['Operation-Location']
        operation_id = operation_location.split('/')[-1]
        time.sleep(1)

        result = self.cv_client.get_read_result(operation_id)
        rr = result.analyze_result.read_results

        if result.status == OperationStatusCodes.succeeded:
            texts = ''
            for ar in rr:
                for line in ar.lines:
                    # print(line.text)
                    texts += line.text + '\n'
        else:
            texts = 'No hand write text found'

        return texts

    def identify_text_from_local_file_str(self, image_str):
        response = self.cv_client.read_in_stream(
                image_str,
                Language='en',
                raw=True
            )

        operation_location = response.headers['Operation-Location']
        operation_id = operation_location.split('/')[-1]
        time.sleep(1)

        result = self.cv_client.get_read_result(operation_id)
        rr = result.analyze_result.read_results

        if result.status == OperationStatusCodes.succeeded:
            texts = []
            for ar in rr:
                for line in ar.lines:
                    # print(line.text)
                    texts.append(line.text)
        else:
            texts = ['No hand written text found']

        image = Image.open(image_str)
        if result.status == OperationStatusCodes.succeeded:
            rr = result.analyze_result.read_results
            for ar in rr:
                for line in ar.lines:
                    x1, y1, x2, y2, x3, y3, x4, y4 = line.bounding_box
                    draw = ImageDraw.Draw(image)
                    draw.line(
                        ((x1, y1), (x2, y2), (x3, y3), (x4, y4), (x1, y1)),
                        fill=(128, 0, 0),
                        width=2
                    )

        # image.show()
        image.save('test.jpg')

        return texts

    def identify_text_from_url(self, image_url):
        response = self.cv_client.read(
                image_url,
                Language='en',
                raw=True
            )

        operation_location = response.headers['Operation-Location']
        operation_id = operation_location.split('/')[-1]
        time.sleep(1)

        result = self.cv_client.get_read_result(operation_id)
        rr = result.analyze_result.read_results

        if result.status == OperationStatusCodes.succeeded:
            texts = []
            for ar in rr:
                for line in ar.lines:
                    texts.append(line.text)
        else:
            texts = ['No hand written text found']

        respons = requests.get(image_url)
        image = Image.open(io.BytesIO(respons.content))
        if result.status == OperationStatusCodes.succeeded:
            rr = result.analyze_result.read_results
            for ar in rr:
                for line in ar.lines:
                    x1, y1, x2, y2, x3, y3, x4, y4 = line.bounding_box
                    draw = ImageDraw.Draw(image)
                    draw.line(
                        ((x1, y1), (x2, y2), (x3, y3), (x4, y4), (x1, y1)),
                        fill=(128, 0, 0),
                        width=5
                    )

        image_stream = io.BytesIO()
        image.save(image_stream, format='PNG')
        image_stream.seek(0)

        storage = Storage.storage('images')
        storage.upload_file_stream(image_stream)

        return texts


# if __name__ == '__main__':
#     cv = ComputerVision()
#
#     r = cv.identify_text_from_local_file(r'C:\Users\Virgil\Desktop\CC Lab\Tema4-CC\computer_vision\hw.jpg')
#     print(r)
