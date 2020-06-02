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

def get_value(item):
    if item == None :
        item = '<MISSING>'
    item = validate(item)
    if item == '':
        item = '<MISSING>'    
    return item

def eliminate_space(items):
    rets = []
    for item in items:
        item = validate(item)
        if item != '':
            rets.append(item)
    return rets

def scrape():
    output_list = []
    session = requests.Session()
    file_name = os.path.dirname(os.path.realpath(__file__)).split('/')[-1] + '.csv'
    with open(file_name, mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["School", "Sports",  "Position", "Name", "Email"])
        url = "http://aiaonline.org/schools"
        source = session.get(url).text    
        response = etree.HTML(source)
        schools = eliminate_space(response.xpath('.//select[@name="id"]')[0].xpath('.//option/@value'))
        for s_id in schools:
            s_url = url + '/' + s_id
            s_response = etree.HTML(session.get(s_url).text)
            headers = s_response.xpath('.//h2')
            school_name = validate(headers[0].xpath('.//text()'))
            sections = s_response.xpath('.//div[@class="col-main"]//table')
            count = len(headers)
            for idx, header in enumerate(headers):
                try:
                    title = validate(header.xpath('.//text()'))
                    if 'Sports' in title:
                        tds = eliminate_space(sections[idx-count].xpath('.//td//text()'))                
                        t_idx = 0
                        output = [school_name]
                        while t_idx != len(tds):
                            if tds[t_idx] == 'Sport' and output != [school_name]:
                                writer.writerow(output)
                                output = [school_name]
                            else:
                                if t_idx % 2 == 1:
                                    output.append(tds[t_idx])
                                if t_idx == len(tds)-1:
                                    writer.writerow(output)
                            t_idx += 1
                except Exception as e:
                    pass

scrape()
