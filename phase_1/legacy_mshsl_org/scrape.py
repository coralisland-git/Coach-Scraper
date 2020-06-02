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
    return item.replace(u'\u2013', '-').encode('ascii', 'ignore').encode("utf8").replace('\t', '').replace('\n', ' ').replace('\r', '').replace('  ', '').replace(':', '').strip()

def eliminate_space(items):
    rets = []
    for item in items:
        item = validate(item)
        if item != '' and item != ':':
            rets.append(item)
    return rets

def check_headers(headers):
    rets = []
    for header in headers:
        if 'TBD' !=  header:
            rets.append(header)
    return rets

def get_index(val, arr):
    for idx, item in enumerate(arr):
        if val == item:
            return idx
    return 0

def scrape():
    output_list = []
    session = requests.Session()
    file_name = os.path.dirname(os.path.realpath(__file__)).split('/')[-1] + '.csv'
    with open(file_name, mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["School", "Sports",  "Position", "Name", "Email"])
        url = "https://legacy.mshsl.org/mshsl/schoolpage2.asp?school=700"
        source = session.get(url).text
        response = etree.HTML(source)
        schools = response.xpath('.//select[@name="schoollist"]//option')[1:]
        for school in schools:
            s_url = "https://legacy.mshsl.org/mshsl/schoolpage2.asp?school="+validate(school.xpath('./@value'))
            school_name = validate(school.xpath('.//text()'))
            s_response = etree.HTML(session.get(s_url).text)
            if s_response is not None:
                tds = eliminate_space(s_response.xpath('.//td[@width="47%"]/table//text()'))
                headers = check_headers(eliminate_space(s_response.xpath('.//td[@width="47%"]//td[@class="tsmall"]//text()')))
                try:
                    for idx, header in enumerate(headers):                        
                        begin_idx = get_index(header, tds)
                        tds = tds[begin_idx+1:]
                        if idx < len(headers)-1:
                            end_idx = get_index(headers[idx+1], tds)
                        else:
                            end_idx = len(tds)
                        details = tds[:end_idx]
                        output = [school_name, header, "", details[0]]
                        for de in details:
                            if '@' in de:
                                output.append(de)
                        writer.writerow(output)
                        tds = tds[end_idx:]
                except Exception as e:
                    pass

scrape()
