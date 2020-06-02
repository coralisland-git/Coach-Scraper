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

def scrape():
    output_list = []
    session = requests.Session()
    file_name = os.path.dirname(os.path.realpath(__file__)).split('/')[-1] + '.csv'
    with open(file_name, mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["School", "Sports",  "Position", "Name", "Email"])
        url = "https://secure.sdhsaa.com/SchoolZone/Directory/BySchool.aspx"
        source = session.get(url).text
        response = etree.HTML(source)
        schools = eliminate_space(response.xpath('.//table[@id="ContentPlaceHolder1_dlSchools"]//a/@href'))
        for s_url in schools:
            s_response = etree.HTML(session.get(s_url).text)
            if s_response is not None:
                school_name = validate(s_response.xpath('.//span[@id="ContentPlaceHolder1_lblSchool"]//text()'))
                tables = s_response.xpath('.//table[@width="680px"]')
                for table in tables:
                    table_name = validate(table.xpath('.//h3//text()'))
                    if 'ATHLETICS' == table_name:
                        for fieldset in table.xpath('.//fieldset'):
                            field_name = validate(fieldset.xpath('.//legend//text()')).split(' ')[0]
                            events = fieldset.xpath('.//tr')
                            for event in events:
                                tds = eliminate_space(event.xpath('.//td[@valign="top"]//text()'))
                                if len(tds) > 1:
                                    output = [
                                        school_name,
                                        field_name + ' ' + tds[0],
                                        "",
                                        tds[1]
                                    ]
                                    for td in tds:
                                        if '@' in td:
                                            output.append(td)
                                    writer.writerow(output)

scrape()