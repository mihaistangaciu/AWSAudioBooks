import boto3
import os
import uuid


def lambda_handler(event, context):
    
    recordId = str(uuid.uuid4())
    voice = event["voice"]
    text = event["text"]
    sourceLanguage = event['sourceLang']
    destLanguage = event['destLang']
    
    translate = boto3.client('translate')
    result = translate.translate_text(Text=text, SourceLanguageCode=sourceLanguage, TargetLanguageCode=destLanguage)
    
    print('Generating new DynamoDB record, with ID: ' + recordId)
    print('Input Text: ' + text)
    print('Selected voice: ' + voice)
    print('Translated text:' + str(result))
    
    #Creating new record in DynamoDB table
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['DB_TABLE_NAME'])
    table.put_item(
        Item={
            'id' : recordId,
            'text' : result.get('TranslatedText'),
            'voice' : voice,
            'status' : 'PROCESSING'
        }
    )
    
    #Sending notification about new post to SNS
    client = boto3.client('sns')
    client.publish(
        TopicArn = os.environ['SNS_TOPIC'],
        Message = recordId
    )
    
    return recordId
