import os
from google.cloud import storage


class FileUtil:
    def __init__(self):
        self.storage_client = storage.Client(os.getenv('GCP_PROJECT_NAME', 'football-scrape'))

    def upload_to_bucket(self, file_name, file, bucket_name):
        """ Upload data to a bucket"""
        bucket = self.storage_client.get_bucket(bucket_name)
        blob = bucket.blob(file_name)
        # blob.upload_from_file(file)
        blob.upload_from_filename(file)

        # returns a public url
        return blob.public_url

    def check_file_exists(self, file_name, bucket_name):
        bucket = self.storage_client.get_bucket(bucket_name)
        blob = bucket.blob(file_name)

        return blob.exists()

    def download_file(self, file_name, destination_file_name, bucket_name):
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        blob.download_to_filename(destination_file_name)

        return destination_file_name
