import os
import sys
import pathlib

NBS_DIR= pathlib.Path(__file__).resolve().parent
BASE_DIR= NBS_DIR.parent

print(NBS_DIR)
print(BASE_DIR)




def init_django(project_name='slackbot'):
    os.chdir(BASE_DIR)
    
    sys.path.insert(0,os.getcwd())
    print('This is pwd  ',sys.path[0])
    # sys.path.insert(0, str(BASE_DIR))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', f"{project_name}.settings")
    os.environ['DJANGO_ALLOW_ASYNC_UNSAFE']="true"
    import django 
    django.setup()


init_django()
