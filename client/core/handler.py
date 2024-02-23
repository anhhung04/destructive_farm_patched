from .log import logger
import requests
import json
from .database import fallbackdb
from .models import FallbackFlag

class SubmitClient(object):
    def __init__(self, server_url, auth=None):
        self._auth = auth
        self._server_url = server_url
        self._game_config = requests.get(f'{self._server_url}/api/get_config').json()
        if not self._game_config:
            raise Exception("Can't get game config from server")
        self._connect_to_fallbackdb()        

    def _connect_to_fallbackdb(self):
        fallbackdb.connect(reuse_if_open=True)

    def enqueue(self, flags, exploit, target):
        if target not in self._game_config['TEAMS']:
            try:
                logger.warning(f"Sploit {exploit} returned flag from your team. Patch the service ASAP !!!")
            except Exception:
                pass
            return {'own': len(flags)}
        
        try:
            response = requests.post(
                f'{self._server_url}/api/post_flags', json=[{'flag': f, 'sploit': exploit, 'team': target} for f in flags], headers={
                    'X-Token': self._auth
                })
        except Exception:
            for flag_value in flags:
                with fallbackdb.atomic():
                    FallbackFlag.create(value=flag_value, exploit=exploit, target=target, 
                                        status='pending')
            return {'pending': len(flags)}
        else:
            return response.json()

    def enqueue_from_fallback(self, flags):
        try:
            response = requests.post(
                f'{self._server_url}/api/post_flags', json=[
                    {
                        'flag': flag.value,
                        'sploit': flag.exploit,
                        'team': flag.target,
                    } for flag in flags], headers={
                        'X-Token': self._auth
                })
            response.raise_for_status()
        except Exception:
            logger.error("Server is unavailable. Skipping...")
        else:
            with fallbackdb.atomic():
                FallbackFlag.update(status='forwarded').where(FallbackFlag.value.in_([flag.value for flag in flags])).execute()