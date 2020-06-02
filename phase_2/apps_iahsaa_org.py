import csv
import re
import pdb
import requests
from lxml import etree
import json
import os
import string
from base import *
from datetime import datetime

def main():
    output_list = []
    session = requests.Session()
    file_name = 'output/' + os.path.splitext(os.path.basename(__file__))[0] + datetime.now().strftime('_%Y_%m_%d_%H_%M_%S') +'.csv'
    with open(file_name, mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["School", "Sports",  "Position", "Name", "Email"])
        base_url = 'https://apps.iahsaa.org/secure/dirpublic.php'
        for alpha in string.ascii_lowercase:
            url = "https://apps.iahsaa.org/phpclasses/serviceConnector.php?object=DirLookupManager&method=lookupSchool&params=school;{}".format(alpha)
            headers = {
                'Accept': '*/*',
                'Cookie': '_ga=GA1.2.543232485.1582648733; _gid=GA1.2.774314913.1582648733; _gat_gtag_UA_114296197_1=1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'
            }
            response = validate(session.get(url, headers=headers).text)
            schools = eliminate_space(response.split('<result>'))
            for school in schools:
                try:
                    s_info = eliminate_space(school.split('<detail>'))
                    s_id = s_info[0]
                    s_name = s_info[1]
                    formdata = {
                        'schoolID': s_id,
                        'school': s_name,
                        'lookup': 'Go'
                    }
                    s_response = session.post(base_url, headers=headers, data=formdata).text
                    s_data = etree.HTML(s_response)
                    s_email = ''            
                    events = s_data.xpath('.//table')[-1].xpath('.//tr')
                    for contact in events:
                        c_email = validate(contact.xpath('.//a/@href')).replace('mailto:', '')
                        if '@' in c_email:
                            s_email = c_email
                            break
                    e_check = {
                        'status' : True,
                        'idx' : 0,
                        'checked' : False
                    }
                    for event in events:
                        tds = event.xpath('.//td')
                        content = eliminate_space(event.xpath('.//text()'))
                        if len(tds) < 2 and len(content) > 1 and is_not_contact(validate(content)):
                            try:
                                e_sport = content[0].replace(':', '')
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
                                print(output, e)
                except Exception as se:
                    print(school, se)
                    pass

if __name__ == '__main__':
    main()