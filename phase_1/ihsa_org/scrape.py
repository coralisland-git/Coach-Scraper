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
        url = "https://www.ihsa.org/Schools/School-Directory"
        source = session.get(url).text
        response = etree.HTML(source)
        pages = eliminate_space(response.xpath('.//div[@id="dnn_ctr1610_HtmlModule_lblContent"]//a/@href'))
        for page_url in pages:
            page_url = 'https://www.ihsa.org' + page_url.split('=')[1]
            p_response = etree.HTML(session.get(page_url).text)
            schools = eliminate_space(p_response.xpath('.//p[@class="nospace"]//a/@href'))
            for s_id in schools:
                s_url = "https://www.ihsa.org/data/school/" + s_id
                s_response = etree.HTML(session.get(s_url).text)
                if s_response is not None:
                    school_name = validate(s_response.xpath('.//h1//text()'))
                    headers = eliminate_space(s_response.xpath('.//h3//text()'))
                    tds = eliminate_space(s_response.xpath('.//text()'))                    
                    sports_arr = []
                    for idx, header in enumerate(headers):
                        if 'Boys Athletics' in header or 'Girls Athletics' in header:
                            sports_arr = tds[get_index(header, tds)+1 : get_index(headers[idx+1], tds)]
                            s_idx = 0
                            while s_idx < len(sports_arr):
                                try:
                                    output = [
                                        school_name,
                                        sports_arr[s_idx],
                                        "",
                                        sports_arr[s_idx+1].replace(':', '')
                                    ]                    
                                    if s_idx+2 < len(sports_arr):
                                        if '@' in sports_arr[s_idx+2]:
                                            output.append(sports_arr[s_idx+2])
                                            s_idx += 3
                                        else:
                                            s_idx += 2
                                    else:
                                        writer.writerow(output)
                                        break
                                    writer.writerow(output)
                                except Exception as e:
                                    pass
scrape()
