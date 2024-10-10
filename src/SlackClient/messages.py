import requests
import helper


SLACK_BOT_OAUTH= helper.config('SLACK_BOT_OAUTH',  cast=str)


def send_message(message, channel_id= None, user_id= None, thread_ts= None):

    url = "https://slack.com/api/chat.postMessage"

    headers={
        'Content-Type' : "application/json; charset=utf-8",
        'Authorization': f'Bearer {SLACK_BOT_OAUTH}',
        "Accept": 'application/json'
    }

    message= f'<@{user_id}> {message}'

    data= {
        "channel": f"{channel_id}",
        "text": f'{message}'.strip()
    } 

    data['thread_ts']= thread_ts

    print('Function here is triggering', data )  

    return requests.post(url, json=data, headers= headers)