import csv
import re
import pdb
import requests
from lxml import etree
import json
import os

def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.replace(u'\u2013', '-').encode('ascii', 'ignore').encode("utf8").strip().replace('\t', '').replace('\n', ' ')

def eliminate_space(items):
    rets = []
    for item in items:
        item = validate(item)
        if item != '':
            rets.append(item)
    return rets

def get_index(val, arr):
    for idx, item in enumerate(arr):
        if val == item:
            return idx
    return 0

def get_name(arr):
    for item in arr:
        if "Name:" in item:
            return validate(item.split(':')[1])
    return ''

def get_email(arr):
    for idx, item in enumerate(arr):
        if 'Email:' in item:
            if idx+1 < len(arr):
                return arr[idx+1]
    return ''

def scrape():
    output_list = []
    session = requests.Session()
    file_name = os.path.dirname(os.path.realpath(__file__)).split('/')[-1] + '_.csv'
    with open(file_name, mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["School", "Sports",  "Position", "Name", "Email"])
        domains = [ 
            { 
                "name" : "cifnshome",
                "key" : "21" 
            }, 
            {
                "name" : "cifsshome",
                "key" : "22"
            } 
        ]
        for domain in domains:
            url = "https://www."+domain['name']+".org/public-school-directory.php"
            source = session.get(url).text
            response = etree.HTML(source)
            schools = eliminate_space(response.xpath('.//div[@id="schools_list"]//a/@onclick'))[1:]
            for s_id in schools:
                s_url = "https://www."+domain['name']+".org/process-school-detail.php?school_id=" + s_id.split('(')[1].split(')')[0]
                s_response = etree.HTML(session.get(s_url).text)
                if s_response is not None:
                    school_name = validate(validate(s_response.xpath('.//h2//text()')).split(' ')[:-1])
                    tds = eliminate_space(s_response.xpath('.//td[@rowspan="'+domain['key']+'"]//text()'))[1:]
                    headers = eliminate_space(s_response.xpath('.//td[@rowspan="'+domain['key']+'"]//p//strong//text()'))[1:]
                    try:
                        for idx, header in enumerate(headers):                        
                            begin_idx = get_index(header, tds)
                            tds = tds[begin_idx+1:]
                            if idx < len(headers)-1:
                                end_idx = get_index(headers[idx+1], tds)
                            else:
                                end_idx = len(tds)
                            details = tds[:end_idx]
                            if len(details) > 0 and details[0] != 'Does Not Field Sport':
                                name = details[0]
                                if ':' in details[0]:
                                    name = details[0].split(':')[-1]
                                output = [school_name, header, "", validate(name)]
                                for de in details:
                                    if '@' in de:
                                        email = de
                                        if ':' in de:
                                            eamil = de.split(':')[-1]
                                        output.append(validate(email))
                                writer.writerow(output)
                            tds = tds[end_idx:]
                    except Exception as e:
                        pass

scrape()

