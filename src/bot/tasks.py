from celery import shared_task
from SlackClient import send_message
from bot.utils import response_model
from bot.retrival_Engine import DocumentRetriever



@shared_task
def slack_message_task(message, channel_id= None,user_id= None, thread_ts= None ):
    # print('This is the message received in the slack message task__', type(message))
    
    model_message =response_model(message)
    # print('this is model response in the slack_message_task', model_message)
    
    r= send_message(model_message, channel_id= channel_id, user_id= user_id, thread_ts= thread_ts)
    return r.status_code


    







    