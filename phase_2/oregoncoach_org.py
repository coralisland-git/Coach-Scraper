import csv
import re
import pdb
import requests
from lxml import etree
import json
import os
from base import *
from datetime import datetime

def is_in_needed_sports(item):
    titles = ['FB', 'VB', 'BBX', 'GBX']
    for title in titles:
        if title in item:
            return True
    return False

def main():
    output_list = []
    session = requests.Session()
    file_name = 'output/' + os.path.splitext(os.path.basename(__file__))[0] + datetime.now().strftime('_%Y_%m_%d_%H_%M_%S') +'.csv'
    with open(file_name, mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["School", "Sports",  "Position", "Name", "Email"])
        url = "http://www.osaa.org/coaches-directory"
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Cookie': 'laravel_session=0ljkh2a03a3vf9frg4ie4t4as7; __cfduid=d3a616fbc653a280033d4fa115d9ad7a91582790813',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'
        }
        response = session.get(url, headers=headers).text
        schools = etree.HTML(response).xpath('.//div[@style="margin-bottom: 1.5em; font-size: 14px;"]')
        for school in schools:
            s_name = validate(school.xpath('.//h2//text()'))
            s_email = ''
            contacts = eliminate_space(school.xpath('.//div[@style="float: left;"]//text()'))
            for contact in contacts:
                if '@' in contact:
                    s_email = validate(contact)
                    break
            e_check = {
                'status' : True,
                'idx' : 0,
                'checked' : False
            }            
            events = eliminate_space(school.xpath('.//div[@style="float: left; width: 100%;"]//text()'))
            for e_idx, event in enumerate(events):
                try:
                    if ':' in event:
                        e_sport = event.replace(':', '')
                        e_name = get_name(events[e_idx+1])
                        # e_emails = generate_email(e_name, s_email) if e_check['status'] else ['']
                        # if not e_check.get('checked') and len(eliminate_space(e_name.split(' '))) < 3:
                        #     e_check = check_email_combination(session, e_emails)
                        if is_in_needed_sports(e_sport):
                            e_email = verify_email(session, generate_email(e_name, s_email))                            
                            output = [
                                s_name, e_sport, "HEAD COACH",
                                e_name, e_email
                            ]
                            writer.writerow(output)
                except Exception as e:
                    pass

if __name__ == '__main__':
    main()