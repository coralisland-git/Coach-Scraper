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
    return item.replace(u'\u2013', '-').encode('ascii', 'ignore').encode("utf8").replace('\t', '').replace('\n', ' ').strip()

def eliminate_space(items):
    rets = []
    for item in items:
        item = validate(item)
        if item != '' and item != ':':
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
        url = "https://www.uhsaa.org/directory"
        source = session.get(url).text
        response = etree.HTML(source)
        schools = response.xpath('.//div[@class="portfolio-item"]')
        for school in schools:
            s_url = validate(school.xpath('.//a[@class="thumb-info"]/@href'))
            s_response = etree.HTML(session.get(s_url).text)
            if s_response is not None:
                school_name = validate(school.xpath('.//h4//text()'))
                tables = s_response.xpath('.//div[@class="main"]//div[@class="container"]/div/div[@class="col-md-8"]/div')
                if len(tables) > 0:
                    events = tables[0].xpath('.//tbody//tr')
                    for event in events:
                        tds = event.xpath('.//td')
                        output = [
                            school_name,
                            validate(tds[0].xpath('.//text()')).replace(':', ''),
                            "",
                            validate(tds[1].xpath('.//text()')),
                            validate(tds[1].xpath('.//a/@href')).replace('mailto:', ''),
                        ]                    
                        writer.writerow(output)
scrape()
