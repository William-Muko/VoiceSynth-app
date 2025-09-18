import json
import boto3
import uuid
import os
from datetime import datetime, timezone
import logging
import html

logger = logging.getLogger()
logger.setLevel(logging.INFO)

polly_client = boto3.client('polly')
s3_client = boto3.client('s3')
translate_client = boto3.client('translate')

BUCKET_NAME = os.environ.get('BUCKET_NAME', 'voicesynth-audio-files-021009501201')

def lambda_handler(event, context):
    try:
        # Parse request body
        if isinstance(event['body'], str):
            body = json.loads(event['body'])
        else:
            body = event['body']
        
        text = html.escape(body.get('text', '').strip())
        voice = html.escape(body.get('voice', 'Joanna'))
        language = html.escape(body.get('language', 'en-US'))
        
        logger.info(f"Received request - Text: {text[:50]}..., Voice: {voice}, Language: {language}")
        
        if not text:
            return create_response(400, {'error': 'Text is required'})
        
        if len(text) > 3000:
            return create_response(400, {'error': 'Text too long (max 3000 characters)'})
        
        # Validate voice parameter
        allowed_voices = [
            'Joanna', 'Matthew', 'Ivy', 'Justin',  # en-US
            'Amy', 'Brian', 'Emma',  # en-GB
            'Lucia', 'Enrique',  # es-ES
            'Celine', 'Mathieu',  # fr-FR
            'Marlene', 'Hans',  # de-DE
            'Carla', 'Giorgio',  # it-IT
            'Vitoria', 'Ricardo',  # pt-BR
            'Mizuki', 'Takumi'  # ja-JP
        ]
        if voice not in allowed_voices:
            logger.error(f"Invalid voice parameter: {voice}")
            return create_response(400, {'error': f'Invalid voice parameter: {voice}'})
        
        # Validate language parameter
        allowed_languages = ['en-US', 'en-GB', 'es-ES', 'fr-FR', 'de-DE', 'it-IT', 'pt-BR', 'ja-JP']
        if language not in allowed_languages:
            logger.error(f"Invalid language parameter: {language}")
            return create_response(400, {'error': f'Invalid language parameter: {language}'})
        
        # Translate text if target language is different from source
        translated_text = text
        target_language = language.split('-')[0]  # Extract language code (e.g., 'es' from 'es-ES')
        
        logger.info(f"Original text: {text[:50]}...")
        logger.info(f"Target language: {target_language}")
        
        try:
            # Always try to translate to target language (except English)
            if target_language != 'en':
                logger.info(f"Attempting translation to {target_language}")
                translate_response = translate_client.translate_text(
                    Text=text,
                    SourceLanguageCode='auto',
                    TargetLanguageCode=target_language
                )
                translated_text = translate_response['TranslatedText']
                detected_source = translate_response.get('SourceLanguageCode', 'unknown')
                logger.info(f"Translation successful: {detected_source} -> {target_language}")
                logger.info(f"Translated text: {translated_text[:50]}...")
            else:
                logger.info("Target is English, no translation needed")
        except Exception as e:
            logger.error(f"Translation failed: {str(e)}")
            logger.info("Using original text for synthesis")
            translated_text = text
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        filename = f"speech-{file_id}.mp3"
        
        # Synthesize speech with Polly
        # Try neural engine first, fallback to standard if not supported
        try:
            response = polly_client.synthesize_speech(
                Text=translated_text,
                OutputFormat='mp3',
                VoiceId=voice,
                Engine='neural',
                LanguageCode=language
            )
        except Exception as e:
            if 'does not support the selected engine' in str(e):
                logger.info(f"Neural engine not supported for {voice}, using standard engine")
                response = polly_client.synthesize_speech(
                    Text=translated_text,
                    OutputFormat='mp3',
                    VoiceId=voice,
                    Engine='standard',
                    LanguageCode=language
                )
            else:
                raise e
        
        # Upload to S3
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=filename,
            Body=response['AudioStream'].read(),
            ContentType='audio/mpeg',
            Metadata={
                'original_length': str(len(text)),
                'translated_length': str(len(translated_text)),
                'voice': html.escape(voice),
                'language': html.escape(language),
                'created': datetime.now(timezone.utc).isoformat()
            }
        )
        
        # Generate presigned URL for download
        audio_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': filename},
            ExpiresIn=3600  # 1 hour
        )
        
        return create_response(200, {
            'audioUrl': audio_url,
            'filename': filename,
            'voice': voice,
            'language': language,
            'originalText': text,
            'translatedText': translated_text
        })
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})

def create_response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        },
        'body': json.dumps(body)
    }