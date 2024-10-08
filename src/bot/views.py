from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import requests

import helper

SLACK_BOT_OAUTH= helper.config('SLACK_BOT_OAUTH',  cast=str)


def send_message(message, channel_id= None):

    url = "https://slack.com/api/chat.postMessage"

    headers={
        'Content-Type' : "application/json; charset=utf-8",
        'Authorization': f'Bearer {SLACK_BOT_OAUTH}',
        "Accept": 'application/json'
    }

    data= {
        "channel": f"{channel_id}",
        "text": message
    } 

    print('Function here is triggering', data )  

    return requests.post(url, json=data, headers= headers)


    


    
 


# Create your views here.

@csrf_exempt
@require_POST
def bot_events(request):
    json_data= {}
    try:
        json_data=json.loads(request.body.decode('utf-8'))
    except:
        pass 
    data_types= json_data.get('type')

    print('These are data types',data_types)

    


    print('These are the json keys', json_data.keys())

    print(data_types, json_data)
    allowed_data_types=[
        'event_callback',
        'url_verification'
    ]
    if data_types not in  allowed_data_types:
        return HttpResponse('Not Allowed', status= 400)   
    if data_types =='url_verification':
        challenge= json_data.get('challenge')
        if challenge is None:
            return HttpResponse('Not Allowed', status= 400)
        print('Here is the challenge', challenge)
    elif data_types==  'event_callback':
        event= json_data.get('event')
        text= event.get('text')
        print('this is text data', text)
        channel_id= event.get('channel')

        print('this is channel id ', channel_id)


        r=send_message(text, channel_id=channel_id)
       
        return  HttpResponse("Success", status= 200 )
    return HttpResponse('Success', status= 200)