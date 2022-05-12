import boto3
from PIL import Image
from io import BytesIO
import io
import os
from botocore.exceptions import NoCredentialsError

class S3ImagesInvalidExtension(Exception):
    pass

class S3ImagesUploadFailed(Exception):
    pass

class S3Images(object):
    
    """Useage:
    
        images = S3Images(aws_access_key_id='fjrn4uun-my-access-key-589gnmrn90', 
                          aws_secret_access_key='4f4nvu5tvnd-my-secret-access-key-rjfjnubu34un4tu4', 
                          region_name='eu-west-1')
        im = images.from_s3('my-example-bucket-9933668', 'pythonlogo.png')
        im
        images.to_s3(im, 'my-example-bucket-9933668', 'pythonlogo2.png')
    """
    
    def __init__(self, aws_access_key_id, aws_secret_access_key, region_name):
        self.s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, 
                                     aws_secret_access_key=aws_secret_access_key, 
                                     region_name=region_name)

        self.resource = boto3.resource('s3', aws_access_key_id=aws_access_key_id, 
                                     aws_secret_access_key=aws_secret_access_key, 
                                     region_name=region_name)
        

    def from_s3_image(self, bucket, key):
        file_byte_string = self.s3.get_object(Bucket=bucket, Key=key)['Body'].read()
        return Image.open(BytesIO(file_byte_string))
    
    def from_s3_object(self, bucket, key):

        s3_connection = self.resource
        s3_object = s3_connection.Object(bucket, key)
        s3_response = s3_object.get()

        # opening binary stream using an in-memory bytes buffer
        stream = io.BytesIO(s3_response['Body'].read())

        # loading stream into image
        image = Image.open(stream)

        return image, stream

    def to_s3(self, img, bucket, key):

        try:
            self.s3.upload_file(img, bucket, key)
            print("Upload Successful")
            return True
        except FileNotFoundError:
            print("The file was not found")
            return False
        except NoCredentialsError:
            print("Credentials not available")
            return False

        """buffer = BytesIO()
        img.save(buffer, self.__get_safe_ext(key))
        buffer.seek(0)
        sent_data = self.s3.put_object(Bucket=bucket, Key=key, Body=buffer)
        if sent_data['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise S3ImagesUploadFailed('Failed to upload image {} to bucket {}'.format(key, bucket))"""
    
    def to_s3_csv(self, csv_buffer, bucket, key):
        self.s3.put_object(Body=csv_buffer.getvalue(), Bucket=bucket, Key=key)
        
    def __get_safe_ext(self, key):
        ext = os.path.splitext(key)[-1].strip('.').upper()
        if ext in ['JPG', 'JPEG']:
            return 'JPEG' 
        elif ext in ['PNG']:
            return 'PNG' 
        else:
            raise S3ImagesInvalidExtension('Extension is invalid') 