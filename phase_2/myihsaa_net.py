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
        writer.writerow(["School", "Sports",  "Position", "Name", "Email", "Year"])
        url = "https://myihsaa-prod-ams.azurewebsites.net/api/school-directory/search"
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36'
        }
        payload = {
            'limit': -1,
            'page': 1,
            'ihsaaDistrict': ''
        }        
        response = session.post(url, headers=headers, data=json.dumps(payload)).text
        schools = json.loads(response).get('items')
        for school in schools:
            try:
                s_url = 'https://myihsaa-prod-ams.azurewebsites.net/api/schools/{}/profile'.format(validate(school.get('id')))
                s_response = session.get(s_url, headers=headers).text
                s_data = json.loads(s_response)
                s_name = validate(school.get('name'))
                s_email = ''
                contacts = s_data.get('contacts')
                for contact in contacts:
                    c_email = validate(contact.get('email'))
                    if c_email != '':
                        s_email = c_email
                        break
                e_check = {
                    'status' : True,
                    'idx' : 0,
                    'checked' : False
                }            
                events = s_data.get('sportYears')
                for event in events:
                    try:
                        e_sport = validate(event.get('gender')) + ' ' + validate(event.get('sportName'))
                        e_name = get_name(event.get('headCoach'))
                        # e_emails = generate_email(e_name, s_email) if e_check['status'] else ['']
                        # if not e_check.get('checked') and len(eliminate_space(e_name.split(' '))) < 3:
                        #     e_check = check_email_combination(session, e_emails)
                        if is_in_needed_sports(e_sport):
                            e_email = verify_email(session, generate_email(e_name, s_email))
                            output = [
                                s_name, e_sport, "HEAD COACH",
                                e_name, e_email, validate(event.get('year'))
                            ]
                            writer.writerow(output)
                    except Exception as e:
                        pass
            except Exception as se:
                print(school, se)

if __name__ == '__main__':
    main()