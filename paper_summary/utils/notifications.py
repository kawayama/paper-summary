import configparser
import datetime
import json
import os
import requests
from typing import Union


def notify_to_slack(content: Union[str, dict], channel: str):
    try:
        if type(content) is str:
            pass
        elif type(content) is dict:
            content = '\n'.join([f"{key}: {value}" for key, value in content.items()])
        else:
            raise AttributeError(f"引数contentの型はstrかdictです (content: {content}, type: {type(content)})")

        webhook_url = _get_webhook_url()
        r = requests.post(webhook_url, data=json.dumps({
            'channel': channel,
            'text': content,
        }))
        r.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        _gen_error_log(notify_to_slack.__name__, e, content=content, channel=channel)
        return False


def _get_webhook_url():
    inifile = configparser.ConfigParser()
    inifile.read('./config.ini', 'utf-8')
    return inifile.get('slack', 'webhook_url')


def _gen_error_log(func_name, error, **kwargs):
    now_str = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    file_path = os.path.join('logs', f"notification-error-{now_str}.log")

    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(f"{now_str} {func_name} {error} {kwargs}")
