import pathlib 
from functools import lru_cache

from decouple import Config, RepositoryEnv 

THIS_DIR= pathlib.Path(__file__).resolve().parent

# print('this is the directory', THIS_DIR)
BASE_DIR= THIS_DIR.parent
print('This is base directory', BASE_DIR)
BASE_DIR_ENV=  BASE_DIR / ".env"
REPO_DIR= BASE_DIR.parent
REPO_DIR_ENV= REPO_DIR / ".env"



@lru_cache 
def get_config():

    if BASE_DIR_ENV:
        return Config(RepositoryEnv(str(BASE_DIR_ENV)))
    if  REPO_DIR_ENV.exists():
        return Config(RepositoryEnv(str(REPO_DIR_ENV)))
    
    from decouple import config
    return config

config= get_config()
