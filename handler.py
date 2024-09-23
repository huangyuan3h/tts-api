import json
import boto3
import edge_tts
import os
from uuid import uuid4
import asyncio
import tempfile

s3 = boto3.client('s3')
bucket_name = os.environ['BUCKET_NAME']


async def generate_speech(event, context):
    body = json.loads(event['body'])
    text = body.get('text')
    voice = body.get('voice', 'en-CA-LiamNeural')
    key = uuid4()

    # 使用 tempfile 创建临时文件
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(temp_file.name)

        temp_file.seek(0)
        s3.put_object(
            Bucket=bucket_name,
            Key=f"{key}.mp3",
            Body=temp_file.read(),
            ContentType='audio/mpeg',
            ContentDisposition='attachment; filename="audio.mp3"'
        )


    url = f"https://{bucket_name}.s3.amazonaws.com/{key}.mp3"

    response = {
        "statusCode": 200,
        "headers": {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Credentials': True,
        },
        "body": json.dumps({"url": url})
    }

    return response


def handler(event, context):
    return asyncio.run(generate_speech(event, context))