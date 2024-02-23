import requests
from datetime import datetime, timedelta
from .handler import SubmitClient
from .database import fallbackdb
from .models import FallbackFlag

def truncate(string, length):
    if length < 4:
        raise AttributeError("Max length must be at least 4 characters.")

    if string and len(string) > length:
        return string[:length - 3] + "..."
    return string


def seconds_from_now(seconds):
    return datetime.now() + timedelta(seconds=seconds)

def load_config(farm_url):
    AUTH_TOKEN = None
    headers = None
    if AUTH_TOKEN is not None:
        headers = {'X-Token': AUTH_TOKEN}
    cfg = requests.get(farm_url + '/api/get_config', headers=headers).json()
    return cfg


def create_handler(farm_url, AUTH_TOKEN):
    handler = SubmitClient(farm_url, auth=AUTH_TOKEN)
    fallbackdb.connect(reuse_if_open=True)
    fallbackdb.create_tables([FallbackFlag], safe=True)
    
    return handler