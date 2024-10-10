from celery import shared_task
from SlackClient import send_message



@shared_task
def slack_message_task(message, channel_id= None,user_id= None, thread_ts= None ):
    r= send_message(message, channel_id= channel_id, user_id= user_id, thread_ts= thread_ts)

    return r.status_code
    