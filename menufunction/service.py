# -*- coding: utf-8 -*-

from __future__ import print_function
from boto3.dynamodb.conditions import Key, Attr

import boto3
import json
import time

print('Loading function')


def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }


def handler(event, context):
    
    print("Received event: " + json.dumps(event, indent=2))

    operations = {
        'DELETE': lambda dynamo, x: dynamo.delete_item(**x),
        'GET': lambda dynamo, x: dynamo.scan(**x),
        'POST': lambda dynamo, x: dynamo.put_item(**x),
        'PUT': lambda dynamo, x: dynamo.update_item(**x),
    }

    operation = event['httpMethod']
    
    if operation in operations:
        if operation == 'GET':
            payload = event['queryStringParameters']
            dynamo = boto3.resource('dynamodb').Table('menu')
            response = dynamo.scan(FilterExpression=Attr(payload['Attribute']).eq(payload['Value']))
            items = response['Items']
            print(items)
            return respond(None, items)

        elif operation == 'POST':
            payload = event['body']
            dyo = boto3.resource('dynamodb').Table('menu')
            responseo = dyo.put_item(
                Item={
                    'menu_id': payload['menu_id'],
                    'store_name': payload['store_name'],
                    'selection': payload['selection'],
                    'size': payload['size'],
                    'price': payload['price'],
                    'store_hours': payload['store_hours']
                }
            )
            dym = boto3.resource('dynamodb').Table('menu')
            responses = dym.get_item(
                Key = {
                    "menu_id":payload['menu_id']
                    }
            )
            return respond(None, "200 OK")
        elif operation == 'DELETE':
            payload = event['body']
            dynamo = boto3.resource('dynamodb').Table('menu')
            dynamo.update_item(
                    Key={
                         "menu_id":payload['menu_id']
                    }
            )
            return respond(None, "200 OK")
        elif operation == 'PUT':
            payload = event['body']
            dynamo = boto3.resource('dynamodb').Table('menu')
            dynamo.update_item(
                    Key={
                         "menu_id":payload['menu_id']
                    },
                    UpdateExpression = "set selection =:s",
                    ExpressionAttributeValues={
                            ':s':payload['selection']
                    },
                    ReturnValues="UPDATED_NEW"
                )
                return respond(None, "200 OK")

        else:
            return respond(ValueError('Unsupported method "{}"'.format(operation)))
    else:
        return respond(ValueError('Unsupported method "{}"'.format(operation)))
