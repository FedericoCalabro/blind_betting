import json
from datetime import date, timedelta, datetime
from dataclasses import dataclass

CONFIG_PATH = 'config.json'


class PalinsestoSupervisor:

    def should_download(self):
        return True
        try:
            with open(CONFIG_PATH, 'r') as file:
                config = json.load(file)
                last_downloaded = datetime.fromtimestamp(config['last_downloaded'])
                return last_downloaded < datetime.now()
        except:
            return True

    def update_last_downloaded(self):
        config = {"last_downloaded" : str(datetime.now())}
        json_to_write = json.dumps(config, indent=4)
        with open(CONFIG_PATH, 'w') as file:
            file.write(json_to_write)
