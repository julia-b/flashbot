import copy
import itertools
import json
import threading
from datetime import datetime


class UserConfig:
    def __init__(self, path):

        self.data_path = path
        with open(self.data_path, 'r') as fp:
            self._user_data_orig = json.loads(fp.read())

        self._user_data = {int(k): copy.deepcopy(v) for k, v in self._user_data_orig.items()}

        for exercise, day in itertools.product(['words', 'reading'], ['weekday', 'weekend']):
            for chat_id, chat_config in self._user_data.items():
                if exercise not in chat_config['schedule']:
                    self._user_data[chat_id]['schedule'][exercise] = {}
                self._user_data[chat_id]['schedule'][exercise][day] = \
                    {datetime.strptime(x, '%H:%M').time(): data for x, data in chat_config['schedule'][exercise][day].items()} \
                    if day in self._user_data[chat_id]['schedule'][exercise].keys() else {}
        self._lock = threading.Lock()

    def get_all_user_data(self):
        self._lock.acquire()
        ud_cpy = copy.deepcopy(self._user_data)
        self._lock.release()
        return ud_cpy

    def get_all_chat_ids(self):
        self._lock.acquire()
        chat_ids = list(self._user_data.keys())
        self._lock.release()
        return chat_ids

    def get_user_data(self, chat_id):
        self._lock.acquire()
        ud_cpy = copy.deepcopy(self._user_data[chat_id])
        self._lock.release()
        return ud_cpy

    def set_deck(self, chat_id: str, deck_id: int):
        self._lock.acquire()
        self._user_data_orig[chat_id]['current_deck_id'] = deck_id
        self._user_data[int(chat_id)]['current_deck_id'] = deck_id
        data_str = json.dumps(self._user_data_orig, indent='\t', ensure_ascii=False)
        with open(self.data_path, 'w') as fp:
            fp.write(data_str)
        self._lock.release()

    def release_lock(self):
        if self._lock.locked():
            self._lock.release()