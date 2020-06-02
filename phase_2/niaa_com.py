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
        base_url = 'https://www.niaa.com'
        url = "https://www.niaa.com/members/index"
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'cookie': '__gads=ID=d23011155225afd9:T=1582648763:S=ALNI_Mb897XOSltLGePWPDlzrMKyBFkg3w; _ga=GA1.2.1075880780.1582648763; _gid=GA1.2.183205375.1582648764; __qca=P0-1825931944-1582648766602',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKi7.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'
        }
        response = session.get(url, headers=headers).text
        data = etree.HTML(response)
        schools = data.xpath('.//div[@id="mainbody"]//b//a')
        s_headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'
        }
        for school in schools:
            try:
                s_name = validate(school.xpath('.//text()'))
                s_url = base_url + validate(school.xpath('./@href'))
                s_response = session.get(s_url, headers=s_headers).text
                s_data = etree.HTML(s_response)
                s_email = ''
                contacts = s_data.xpath('.//table[@class="roster"]//a//text()')
                for contact in contacts:
                    if '@' in contact:
                        s_email = contact
                        break
                e_url = s_url.replace('/info', '/coaches')
                e_response = session.get(e_url, headers=s_headers).text
                e_data = etree.HTML(e_response)
                e_check = {
                    'status' : True,
                    'idx' : 0,
                    'checked' : False
                }
                events = e_data.xpath('.//table//tr')
                for event in events:
                    content = eliminate_space(event.xpath('.//text()'))
                    if len(content) > 1:
                        try:
                            e_sport = content[0]
                            e_name = get_name(content[1])
                            # e_emails = generate_email(e_name, s_email) if e_check['status'] else ['']
                            # if not e_check.get('checked'):
                            #     e_check = check_email_combination(session, e_emails)
                            if is_in_needed_sports(e_sport):
                                e_email = verify_email(session, generate_email(e_name, s_email))
                                output = [
                                    s_name, e_sport, "HEAD COACH", 
                                    e_name, e_email
                                ]
                                writer.writerow(output)
                        except Exception as e:
                            print('```', e)
                            pass
            except Exception as se:
                print(se)

if __name__ == '__main__':
    main()