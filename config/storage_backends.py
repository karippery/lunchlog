from storages.backends.s3boto3 import S3Boto3Storage

class ReceiptImageStorage(S3Boto3Storage):
    bucket_name = 'my-bucket'
    custom_domain = False