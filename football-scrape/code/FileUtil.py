import os
from google.cloud import storage


class FileUtil:
    def __init__(self):
        self.storage_client = storage.Client(os.getenv('GCP_PROJECT_NAME', 'football-scrape'))

    def upload_to_bucket(self, file_name, file, bucket_name):
        """ Upload data to a bucket"""
        self.storage_client.list_buckets()

        # print(buckets = list(storage_client.list_buckets())

        bucket = self.storage_client.get_bucket(bucket_name)
        blob = bucket.blob(file_name)
        # blob.upload_from_file(file)
        blob.upload_from_filename(file)

        # returns a public url
        return blob.public_url





