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
        domains = [ 
            { 
                "name" : "fhsaahome",
                "key" : "22" 
            }
        ]
        for domain in domains:
            url = "https://www."+domain['name']+".org/public-school-directory.php"
            source = session.get(url).text
            response = etree.HTML(source)
            schools = eliminate_space(response.xpath('.//div[@id="schools_list"]//a/@onclick'))
            for s_id in schools:
                try:
                    s_url = "https://www."+domain['name']+".org/process-school-detail.php?school_id=" + s_id.split('(')[1].split(')')[0]
                    s_response = etree.HTML(session.get(s_url).text)                
                    s_name = validate(validate(s_response.xpath('.//h2//text()')).split(' ')[:-1])
                    tds = eliminate_space(s_response.xpath('.//td[@rowspan="'+domain['key']+'"]//text()'))[1:]
                    headers = eliminate_space(s_response.xpath('.//td[@rowspan="'+domain['key']+'"]//p//strong//text()'))[1:]
                    content = eliminate_space(s_response.xpath('.//table//text()'))
                    s_email = ''
                    for c_idx, ct in enumerate(content):
                        if ct == 'Athletic Director:' and c_idx+2 < len(content) and '@' in content[c_idx+2]:
                            s_email = validate(content[c_idx+2])
                            break                    
                    e_check = {
                        'status' : True,
                        'idx' : 0,
                        'checked' : False
                    }
                    for idx, header in enumerate(headers):
                        try:
                            begin_idx = get_index(header, tds)
                            tds = tds[begin_idx+1:]
                            if idx < len(headers)-1:
                                end_idx = get_index(headers[idx+1], tds)
                            else:
                                end_idx = len(tds)
                            details = tds[:end_idx]
                            if len(details) > 0:
                                e_name = get_name(details[1])
                                # e_emails = generate_email(e_name, s_email) if e_check['status'] else ['']
                                # if not e_check.get('checked') and len(eliminate_space(e_name.split(' '))) < 3:
                                #     e_check = check_email_combination(session, e_emails)
                                if is_in_needed_sports(header):
                                    e_email = verify_email(session, generate_email(e_name, s_email))
                                    output = [s_name, header, validate(details[0]), e_name, e_email]
                                    writer.writerow(output)
                            tds = tds[end_idx:]
                        except Exception as e:
                            pass
                except Exception as se:
                    print(se, s_id)

if __name__ == '__main__':
    main()
