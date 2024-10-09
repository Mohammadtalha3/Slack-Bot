from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from SlackClient import send_message
from bot.tasks import slack_message_task
from pprint import pprint
import json





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

    allowed_data_types=[
        'event_callback',
        'url_verification'
    ]
    if data_types not in  allowed_data_types:
        return HttpResponse('Not Allowed', status= 400)   
    if data_types =='url_verification':
        challenge= json_data.get('challenge')
        if challenge:
            return HttpResponse(challenge, status= 200)
        else:
            return HttpResponse('Not Allowed Challenge missing', status= 400)
    elif data_types==  'event_callback':
        event= json_data.get('event') or {}
        try:
            text= event['blocks'][0]['elements'][0]['elements'][1]['text']
        except:
            text= event.get('text')
        user_id= event.get('user')     
        channel_id= event.get('channel')
        msg_ts= event.get('ts')
        thread_ts= event.get('thread_ts') or msg_ts
        # send_message(text, channel_id=channel_id, user_id=user_id, thread_ts=thread_ts)
        slack_message_task.delay(text, channel_id=channel_id, user_id=user_id, thread_ts=thread_ts)
       
        return  HttpResponse("Success", status= 200 )
    return HttpResponse('Success', status= 200)