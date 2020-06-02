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
        base_url = 'https://www.ghsa.net/'
        url = "https://www.ghsa.net/school-directory"        
        response = validate(session.get(url).text)
        data = etree.HTML(response)
        schools = data.xpath('.//select[@class="form-select"]//option')[1:]
        s_url = 'https://www.ghsa.net/school-directory'
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': 'UUID=f734419e-29e6-24a4-d95f-553a644e84c0; _ga=GA1.2.880950120.1582633299; has_js=1; _gid=GA1.2.1341098917.1582800248; _gat=1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'
        }
        for school in schools:
            try:
                s_name = validate(school.xpath('.//text()'))
                s_id = validate(school.xpath('./@value'))
                formdata = {
                    'dropdown': s_id,
                    # 'form_build_id': 'form-qpNp0l9-K7ijm2n20r6xRL60Nq_c__JQYrZ3E0xd-Yg',
                    'form_id': 'ghsa_feeds_directory_feed_form'
                }
                s_response = session.post(s_url, headers=headers, data=formdata).text
                s_data = etree.HTML(s_response)
                s_email = ''
                contacts = eliminate_space(s_data.xpath('.//table[@class="directory-table"]//text()'))
                for contact in contacts:
                    if '@' in contact:
                        s_email = contact
                        break
                e_check = {
                    'status' : True,
                    'idx' : 0,
                    'checked' : False
                }
                events = s_data.xpath('.//table[@class="directory-table"]//table//tr')
                print(s_name, s_id, len(events))
                for e_idx, event in enumerate(events):
                    tds = event.xpath('.//td[@align="left"]')
                    if len(tds) == 0:
                        tds = event.xpath('.//td')
                    for t_idx in range(0, len(tds)/2):
                        try:
                            e_name = get_name(tds[t_idx*2].xpath('.//text()'))
                            sports = eliminate_space(tds[t_idx*2+1].xpath('.//text()'))
                            # e_emails = generate_email(e_name, s_email) if e_check['status'] else ['']
                            # if not e_check.get('checked') and len(eliminate_space(e_name.split(' '))) < 3:
                            #     e_check = check_email_combination(session, e_emails)
                            for e_sport in sports:
                                if is_in_needed_sports(e_sport):
                                    e_email = verify_email(session, generate_email(e_name, s_email))
                                    e_sport = validate(e_sport.replace('Coach', ''))
                                    output = [
                                        s_name, e_sport, "HEAD COACH",
                                        e_name, e_email
                                    ]
                                    writer.writerow(output)
                        except Exception as e:
                            pass
            except Exception as se:
                print(se)
                pass

if __name__ == '__main__':
    main()