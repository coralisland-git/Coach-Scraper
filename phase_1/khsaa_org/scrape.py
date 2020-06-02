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
        if item != '' and item != '(no team)':
            rets.append(item)
    return rets

def scrape():
    output_list = []
    session = requests.Session()
    file_name = os.path.dirname(os.path.realpath(__file__)).split('/')[-1] + '.csv'
    with open(file_name, mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["School", "Sports",  "Position", "Name", "Email"])
        url = "https://khsaa.org/general/resources/member-school-directory"
        source = session.get(url).text
        response = etree.HTML(source)
        schools = eliminate_space(response.xpath('.//div[@id="post-662"]//li//a/@href'))
        for s_id in schools:            
            s_url = url + s_id
            s_response = etree.HTML(session.get(s_url).text)
            if s_response is not None:
                tables = s_response.xpath('.//div[@style="float:left; width: 75%;"]/table')
                school_name = eliminate_space(tables[0].xpath('.//b//text()'))[0]
                for table in tables[2:]:
                    try:
                        events = table.xpath('.//tr')[3:-1]
                        for event in events:
                            tds = eliminate_space(event.xpath('.//text()'))
                            output = [school_name, tds[0], ""]
                            if len(tds) > 1:
                                output.append(tds[1])
                            if len(tds) > 2:
                                output.append(tds[2])
                            writer.writerow(output)
                    except Exception as e:
                        pass

scrape()
