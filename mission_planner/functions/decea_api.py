import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

SECRET_KEY = os.environ.get("DECEA_API_KEY")
PASSWORD = os.environ.get("DECEA_API_PASSWORD")

import requests
from xml.etree import ElementTree

from datetime import datetime


class DeceaApiConnection:
    def __init__(self):
        self.SECRET_KEY = SECRET_KEY
        self.PASSWORD   = PASSWORD

        self.data_output = [] # A LIST OF DICTIONARIES

    def get_notam_from_icao(self, ICAO: str):
        api_key         = self.SECRET_KEY
        api_pass        = self.PASSWORD
        notam_icao_code = ICAO
        
        API_URL         = f"http://aisweb.decea.gov.br/api/"
        PAYLOAD         = f"?apiKey={api_key}&apiPass={api_pass}&area=notam&icaocode={notam_icao_code}"
        headers         = {
            'apiKey': api_key,
            'apiPass': api_pass,
            'area': 'notam',
            'icao_code': notam_icao_code
        }
        response        = requests.get(API_URL + PAYLOAD)

        if response.status_code != 200:
            return None

        # XML PARSING
        root            = ElementTree.fromstring(response.content)

        for unit in root[0]:
            status     = unit.find('status').text
            cat        = unit.find('cat').text
            creation   = unit.find('dt').text
            number     = unit.find('n').text

            valid_from = unit.find('b').text
            valid_til  = unit.find('c').text

            try:
                valid_from = datetime.strptime(valid_from, "%y%m%d%H%M")
                valid_til = datetime.strptime(valid_til, "%y%m%d%H%M")
            except:
                pass

            message    = unit.find('e').text

            package_dict = {
                'status': status,
                'cat': cat,
                'creation': creation,
                'number': number,
                'valid_from': valid_from,
                'valid_til': valid_til,
                'message': message
            }

            self.data_output.append(package_dict)

    def get_meteoro_data_from_icao(self, ICAO: str):
        api_key = self.SECRET_KEY
        api_pass = self.PASSWORD
        notam_icao_code = ICAO

        API_URL = f"http://aisweb.decea.gov.br/api/"
        PAYLOAD = f"?apiKey={api_key}&apiPass={api_pass}&area=met&icaocode={notam_icao_code}"
        headers = {
            'apiKey': api_key,
            'apiPass': api_pass,
            'area': 'met',
            'icao_code': notam_icao_code
        }
        response = requests.get(API_URL + PAYLOAD)

        if response.status_code != 200:
            return None

        root = ElementTree.fromstring(response.content)

        # print(response.text)
        for unit in root:
            metar = unit.find('metar').text
            taf   = unit.find('taf').text

            if metar is None:
                metar = 'Indisponível'
            if taf is None:
                taf = 'Indisponível'

            package_dict = {
                'metar': metar,
                'taf': taf
            }

            self.data_output.append(package_dict)

    def get_working_hours_from_icao(self, ICAO:str):
        api_key = self.SECRET_KEY
        api_pass = self.PASSWORD
        notam_icao_code = ICAO

        API_URL = f"http://aisweb.decea.gov.br/api/"
        PAYLOAD = f"?apiKey={api_key}&apiPass={api_pass}&area=rotaer&icaocode={notam_icao_code}"
        headers = {
            'apiKey': api_key,
            'apiPass': api_pass,
            'area': 'rotaer',
            'icao_code': notam_icao_code
        }
        response = requests.get(API_URL + PAYLOAD)

        if response.status_code != 200:
            return None

        root = ElementTree.fromstring(response.content)

        print(response.text)

        for unit in root:
            timesheets = unit.findall('timesheet')

            for sheet in timesheets:
                print(sheet.attrib)

            package_dict = {
            }

            self.data_output.append(package_dict)
