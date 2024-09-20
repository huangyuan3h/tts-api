import json
import boto3
import edge_tts
from edge_tts import VoicesManager
import os
from uuid import uuid4
import asyncio
import random

s3 = boto3.client('s3')
bucket_name = os.environ['BUCKET_NAME']


async def generate_speech(event, context):

    body = json.loads(event['body'])
    text = body.get('text')
    language = body.get('language', 'en')

    output_file = f"/tmp/{uuid4()}.mp3"
    
    voices = await VoicesManager.create()
    voice = voices.find(Gender="Female", Language=language)

    # Use Edge-TTS to generate speech
    communicate = edge_tts.Communicate(text, random.choice(voice)["Name"])
    await communicate.save(output_file)
    
    # Upload to S3
    key = f"{uuid4()}.mp3"
    with open(output_file, "rb") as f:
        s3.put_object(
        Bucket=bucket_name,
        Key=key,
        Body=f,
        ContentType='audio/mpeg',
        ContentDisposition='attachment; filename="audio.mp3"'
    )

    # Generate S3 URL
    url = f"https://{bucket_name}.s3.amazonaws.com/{key}"


    response = {
        "statusCode": 200,
        "body": json.dumps({"url": url})
    }

    return response

def handler(event, context):
    return asyncio.run(generate_speech(event, context))