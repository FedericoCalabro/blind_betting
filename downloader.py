from fake_headers import Headers
from supervisor import PalinsestoSupervisor
import requests

DOWNLOAD_URL = "https://landing.sisal.it/volantini/Scommesse_Sport/Quote/calcio%20base%20per%20manifestazione.pdf"
DOWNLOAD_PATH = "palinsesto.pdf"

class PalisenstoDownloader:
    def __init__(self, supervisor : PalinsestoSupervisor):
        if supervisor.should_download():
            try:
                response = requests.get(DOWNLOAD_URL, headers=self.__get_fake_headers(), timeout=120, stream=True)
                file = open(DOWNLOAD_PATH, 'wb')
                file.write(response.content)
                supervisor.update_last_downloaded()
            except Exception as err:
                raise Exception(err)
    
    
    def __get_fake_headers(self):
        return {
            'Accept': '*/*', 
            'Connection': 'keep-alive', 
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.91 Safari/537.36', 
            'Accept-Language': 'en-US;q=0.5,en;q=0.3', 
            'Cache-Control': 'max-age=0', 
            'DNT': '1', 
            'Upgrade-Insecure-Requests': '1'
        }
        mocker = Headers(browser="chrome", os="win", headers=True)
        mocked = mocker.generate()
        print(mocked)
        return mocked
    