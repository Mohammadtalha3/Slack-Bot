from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

import helper

SLACK_BOT_OAUTH= helper.config('SLACK_BOT_OAUTH', Default= None, cast=str)

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
        return  HttpResponse(challenge, status= 200 )
    return HttpResponse('Success', status= 200)