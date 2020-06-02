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
        start_url = 'https://schsl.org/index.php/directory'
        start_response = etree.HTML(session.get(start_url).text)
        page_count = int(start_response.xpath('.//div[@class="sabai-pagination sabai-btn-group"]//a//text()')[-2])        
        for page_idx in range(0, page_count):
            url = "https://schsl.org/index.php/directory?p={}".format(page_idx+1)
            source = session.get(url).text
            response = etree.HTML(source)
            schools = eliminate_space(response.xpath('.//div[@class="sabai-directory-title"]//a/@href'))
            for s_link in schools:
                s_response = etree.HTML(session.get(s_link).text)
                if s_response is not None:
                    school_name = validate(s_response.xpath('.//h1//text()'))
                    events = s_response.xpath('.//div[@id="sabai-body"]//div[@class="sabai-directory-body"]//table')[-1].xpath('.//tr')                    
                    for event in events:
                        tds = eliminate_space(event.xpath('.//text()'))
                        if len(tds) > 1 and ':' not in tds[0] and 'N/A' != tds[1]:
                            output = [
                                school_name,
                                tds[0],
                                "",
                                tds[1],
                            ]
                            if len(tds) > 2 and '@' in tds[2]:
                                output.append(tds[2])
                            writer.writerow(output)

scrape()
