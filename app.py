from flask import Flask, render_template, request
import boto3
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)
dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)

table = dynamodb.Table('Students')
BUCKET_NAME = os.getenv("BUCKET_NAME")


@app.route('/')
def home():

    objects = s3.list_objects_v2(Bucket=BUCKET_NAME)

    files = []

    if 'Contents' in objects:
        for obj in objects['Contents']:
            files.append(obj['Key'])

    return render_template(
        'index.html',
        files=files
    )


@app.route('/upload', methods=['POST'])
def upload():

    name = request.form['name']
    email = request.form['email']

    file = request.files['resume']

    if file:

        s3.upload_fileobj(
            file,
            BUCKET_NAME,
            file.filename
        )

        table.put_item(
            Item={
                'email': email,
                'name': name,
                'resume': file.filename
            }
        )

        return f"✅ {file.filename} uploaded successfully!"

    return "No file selected"


if __name__ == '__main__':
    app.run(debug=True)