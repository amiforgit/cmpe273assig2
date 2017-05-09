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
            dynamo = boto3.resource('dynamodb').Table('pizzaorder')
            response = dynamo.scan(FilterExpression=Attr(payload['Attribute']).eq(payload['Value']))
            items = response['Items']
            print(items)
            return respond(None, items)

        elif operation == 'POST':
            payload = event['body']
            dyo = boto3.resource('dynamodb').Table('pizzaorder')
            responseo = dyo.put_item(
                Item={
                    'menu_id': payload['menu_id'],
                    'order_id': payload['order_id'],
                    'customer_name': payload['customer_name'],
                    'customer_email': payload['customer_email'],
                    'order_status': "processing",
                    'order':{"selection":"empty",
                             "size":"empty",
                             "cost":"empty",
                             "order_time":"empty"}
                }
            )
            dym = boto3.resource('dynamodb').Table('menu')
            responses = dym.get_item(
                Key = {"menu_id":payload['menu_id']}
            )
            item =responses['Item']
            s = item['selection']
            msg = 'Hi '+payload['customer_name']+', please choose one of these selection:  1 '+s[0]+' 2 '+s[1]+' 3 '+s[2]
            data ={'message':msg}
            jdata = json.dumps(data)
            print (data)
            return respond(None, jdata)
        elif operation == 'PUT':
            payload = event['body']
            #get the selection number
            num =int(payload['input'])
            #get the order_id and chenck its order
            order_id =event['Value']
            print (order_id)
            dyo = boto3.resource('dynamodb').Table('pizzaorder')
            oresponses = dyo.get_item(
                Key={"order_id": order_id}
            )
            oitem = oresponses['Item']
            order = oitem['order']
            print (order['selection'])
            #get the menu detail
            menu_id = oitem['menu_id']
            dym = boto3.resource('dynamodb').Table('menu')
            mresponses = dym.get_item(
                Key={"menu_id": menu_id}
            )
            mitem = mresponses['Item']

            if order['selection'] =="empty":

                dyo.update_item(

                    Key={
                        "order_id": order_id
                    },
                    ExpressionAttributeNames={
                        "#o": "order"
                    },
                    UpdateExpression = "set #o.selection =:val",
                    ExpressionAttributeValues={
                            ':val':mitem['selection'][num-1]
                    },
                    ReturnValues="UPDATED_NEW"
                )
                s = mitem['size']
                msg = 'Hi ' + oitem['customer_name'] + ', please choose one of these selection:  1 ' + s[0] + ' 2 ' + \
                      s[1] + ' 3 ' + s[2] +' 4 '+s[3] + ' 5 '+s[4]
                data = {'message': msg}
                jdata = json.dumps(data)
                print(data)
                return respond(None, jdata)

            elif order['size'] =="empty":
                localtime = time.asctime(time.localtime(time.time()))
                dyo.update_item(

                    Key={
                        "order_id": order_id
                    },
                    ExpressionAttributeNames={
                        "#o": "order"
                    },
                    UpdateExpression="set #o.size =:val",
                    ExpressionAttributeValues={
                        ':val': mitem['size'][num-1]
                    },
                    ReturnValues="UPDATED_NEW"
                )
                #get the price
                dyo.update_item(
                    Key={
                        'order_id': order_id
                    },
                    ExpressionAttributeNames={
                        "#o": "order"
                    },
                    UpdateExpression="set #o.cost =:val",
                    ExpressionAttributeValues={
                        ':val': mitem['price'][num - 1]
                    },
                    ReturnValues="UPDATED_NEW"
                )
                #get the localtime
                dyo.update_item(
                    Key={
                        'order_id': order_id
                    },
                    ExpressionAttributeNames={
                        "#o": "order"
                    },
                    UpdateExpression="set #o.order_time =:val",
                    ExpressionAttributeValues={
                        ':val': localtime
                    },
                    ReturnValues="UPDATED_NEW"
                )
                msg = 'Your order cost is '+mitem['price'][num - 1]+' . We will email you when the order is ready. Thank you!'
                data = {'message': msg}
                jdata = json.dumps(data)
                print(data)
                return respond(None, jdata)

        else:
            return respond(ValueError('Unsupported method "{}"'.format(operation)));
    else:
        return respond(ValueError('Unsupported method "{}"'.format(operation)))
