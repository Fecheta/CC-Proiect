import io

from azure.storage.blob import BlobServiceClient


class Storage:
    storage_instance = None

    def __init__(self, container_name):
        self.connect_str = 'DefaultEndpointsProtocol=https;AccountName=ccprojectimages;AccountKey=XgNlfXYyIHzlkmtxo6Y8uVV8vLVfVlf1gT6fhX+7s4VcJYs4L5LrTRLu2GoO1xLeHyeS2nR/BvKvLwNrpLWXfQ==;EndpointSuffix=core.windows.net'
        self.container_name = container_name
        self.blob_service_client, self.container_client = self.connect()

    @staticmethod
    def storage(container_name):
        if Storage.storage_instance is None:
            Storage.storage_instance = Storage(container_name)

        return Storage.storage_instance

    def connect(self):
        blob_service_client = BlobServiceClient.from_connection_string(
            conn_str=self.connect_str)
        try:
            container_client = blob_service_client.get_container_client(
                container=self.container_name)
            container_client.get_container_properties()
        except Exception as e:
            print("Creating container...")
            container_client = blob_service_client.create_container(self.container_name)

        return blob_service_client, container_client

    def change_container(self, container_name):
        self.container_name = container_name
        self.blob_service_client, self.container_client = self.connect()

    def upload_file(self, file):
        try:
            self.container_client.upload_blob(file.filename,
                                              file)
        except Exception as e:
            print("Ignoring duplicate filenames")

    def upload_file_stream(self, stream: io.BytesIO, name):
        try:
            blob_client = self.container_client.get_blob_client(blob=name)

            blob_client.upload_blob(stream.read(),
                                    blob_type='BlockBlob')
            print(stream)
        except Exception as e:
            # print(e)
            print("Ignoring duplicate filenames")

    def get_images(self):
        blob_items = self.container_client.list_blobs()

        urls = []
        for blob in blob_items:
            blob_client = self.container_client.get_blob_client(blob=blob.name)
            urls.append(blob_client.url)
            # print(blob.name)

        return urls

    def get_image_by_name(self, name):
        blob_items = self.container_client.list_blobs()

        url = None
        for blob in blob_items:
            blob_client = self.container_client.get_blob_client(blob=blob.name)

            if blob.name == name:
                url = blob_client.url
                break

        return url
#
# if __name__ == '__main__':
#     pass
