import requests
from bs4 import BeautifulSoup
from time import time
from typing import List


class GrametScraper:
    def __init__(self, icao_route: List[str]):
        self.route = ''

        for icao in icao_route:
            self.route += icao + '_'

        self.route = self.route.rstrip('_')

        self.epoch = int(time())

        self.url = "https://www.ogimet.com/display_gramet.php?"
        self.payload = f"icao={self.route}&hini=0&tref={self.epoch}&hfin=0&fl=100&enviar=Enviar"

        self.gramet_url = self.scraping()

    def scraping(self):
        html_page = requests.get(self.url + self.payload)
        soup = BeautifulSoup(html_page.content, 'html.parser')
        center = soup.find('center')

        error_message = 'Error, no se han encontrado datos'

        if error_message in center.parent.text:
            return None

        base_url = "https://www.ogimet.com"
        image_source = center.findChild('img').attrs['src']

        return base_url + image_source


if __name__ == '__main__':
    icao_route = ['SBCO', 'SBFL', 'SBGL']
    gramet = GrametScraper(icao_route)
    image_url = gramet.scraping()

    print(image_url)

