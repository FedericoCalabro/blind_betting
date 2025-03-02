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
                response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
                with open(DOWNLOAD_PATH, 'wb') as file:
                  for chunk in response.iter_content(chunk_size=8192): # Download chunk by chunk
                      file.write(chunk)
                supervisor.update_last_downloaded()
            except requests.exceptions.Timeout as err:
                print(f"Download timed out: {err}")
                raise
            except requests.exceptions.RequestException as err:
                print(f"An error occurred during the download: {err}")
                raise
            except Exception as err:
                print(f"An unexpected error occurred: {err}")
                raise
    
    
    def __get_fake_headers(self, generate_random = False):
        if not generate_random:
            return {
                "sec-ch-ua": "\"Not(A:Brand\";v=\"99\", \"Google Chrome\";v=\"133\", \"Chromium\";v=\"133\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"macOS\"",
                "upgrade-insecure-requests": "1",
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
                "accept-encoding": "gzip, deflate, br, zstd",
                "accept-language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7",
                "cache-control": "max-age=0",
            }
        else:
            mocker = Headers(browser="chrome", os="win", headers=True)
            mocked = mocker.generate()
            return mocked
    