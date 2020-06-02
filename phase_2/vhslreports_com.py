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
        url = "https://vhslreports.com/school_directory/"
        response = session.get(url).text
        schools = etree.HTML(response).xpath('.//table//a/@data-school-info')
        for school in schools:
            try:
                s_url = 'https://vhslreports.com/school_directory/view?schoolInfo={}'.format(school)
                s_response = session.get(s_url).text
                s_data = etree.HTML(s_response)
                s_name = validate(s_data.xpath('.//div[@class="print-section"]//h3//text()'))
                s_email = ''
                contacts = eliminate_space(s_data.xpath('.//div[@class="print-section"]/div[@class="row"]//text()'))
                for contact in contacts:
                    if '@' in contact:
                        s_email = validate(contact)
                        break
                e_check = {
                    'status' : True,
                    'idx' : 0,
                    'checked' : False
                }            
                events = eliminate_space(s_data.xpath('.//table[@class="table-coach"]//text()'))
                for e_idx, event in enumerate(events):
                    try:
                        if ':' in event and e_idx+1 < len(events) and ':' not in events[e_idx+1]:
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
            except Exception as se:
                print(school, se)

if __name__ == '__main__':
    main()