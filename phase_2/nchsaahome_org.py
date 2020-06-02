import csv
import re
import pdb
import requests
from lxml import etree
import json
import os
from base import *
from datetime import datetime

def main():
    output_list = []
    session = requests.Session()
    file_name = 'output/' + os.path.splitext(os.path.basename(__file__))[0] + datetime.now().strftime('_%Y_%m_%d_%H_%M_%S') +'.csv'
    with open(file_name, mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["School", "Sports",  "Position", "Name", "Email"])
        url = "https://nchsaahome.org/widget/nchsaa-member-schools-widget"
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'cookie': 'XSRF-TOKEN=eyJpdiI6IjdVS3dJK1wvVXZYUjREUDgwcFpwd3pBPT0iLCJ2YWx1ZSI6InZxOHRMSmloOExhTkloSStpQmlGNUg3N2FxXC9CaVM1MGR1ZGwxWFVIT1p2Z294TmwwXC9LODMyYUpoeVM0ZG1jciIsIm1hYyI6IjA2YjhjYzY4YjEyM2Y3N2M0OTEyNGNjNzQwMDAyOTExOGE5ZGE0OTA5ODhmOWFlOWVmZDg0YTIyNjA5ZWQxODgifQ%3D%3D; nchsaahome_session=eyJpdiI6InJ3bGxXTTB3aVg2QnFlSWlhbEJIN2c9PSIsInZhbHVlIjoieUZNRUdvMlhhTko3XC85ZlJxRGdIM1E4amZBMm9rWmRZcFRaNmZrWDJ5cVJyZUVMYTFqVjhxek5XcStDS0k2cTIiLCJtYWMiOiIwZmI1MmRlZGI4ZjBiODVhZWUzYjNlZWQzMmE0NDI4ZTE0NGVmNzcwZDcwYzg0ZmE0YTVlNDBlMWRlNjE3YTA2In0%3D',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'
        }
        response = session.get(url, headers=headers).text
        schools = etree.HTML(response).xpath('.//select[@name="school_id"]//option/@value')
        s_url = 'https://nchsaahome.org/widget/nchsaa-member-schools-widget/coaches-sports'            
        for school in schools:
            try:
                formdata = {
                    'school_id': school,
                    'level_id': '1',
                    '_token': 'aZTNAIIJRwRgaQ6hKYJKwPKPmjQk5EQeFJYphAyS'
                }
                s_response = session.post(s_url, headers=headers, data=formdata).text
                s_data = json.loads(s_response)[school]
                s_name = validate(s_data.get('name'))
                sports = s_data.get('sports')
                for s_key, sport in sports.items():
                    e_sport = validate(sport.get('name'))
                    if is_in_needed_sports(e_sport):
                        events = sport.get('levels').get('Varsity').get('Head')
                        for event in events:
                            try:
                                e_name = validate(event.get('firstname')) + ' ' +  validate(event.get('lastname'))
                                e_email =validate(event.get('email'))
                                output = [
                                    s_name, e_sport, "HEAD COACH",
                                    e_name, e_email
                                ]
                                writer.writerow(output)
                            except Exception as e:
                                pass
            except Exception as se:
                print(school, se)

if __name__ == '__main__':
    main()