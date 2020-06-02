import csv
import re
import pdb
import requests
from lxml import etree
import json
import string
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
    file_name = os.path.dirname(os.path.realpath(__file__)).split('/')[-1] + '.csv'
    history = []
    with open(file_name, mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["School", "Sports",  "Position", "Name", "Email"])        
        for alpha in string.ascii_lowercase:
            page_idx = 1
            while True:
                url = "http://officials.myohsaa.org/Outside/SearchSchool?OhsaaId=&Name={}&page={}".format(alpha, page_idx)
                source = session.get(url).text
                response = etree.HTML(source)
                schools = eliminate_space(response.xpath('.//table[@class="table table-striped"]//a[@class="btn btn-warning"]/@href'))
                if len(schools) == 0:
                    break
                else:
                    for s_id in schools:
                        s_url = "http://officials.myohsaa.org/Outside/Schedule/SportsInformation?" + s_id.split('?')[1]
                        if s_url not in history:
                            history.append(s_url)
                            try:
                                s_response = etree.HTML(session.get(s_url).text)
                                if s_response is not None:                
                                    school_name = validate(validate(s_response.xpath('.//div[@class="schoolHeader"]//h2//text()')).split('(')[0])
                                    events = s_response.xpath('.//table[@class="displayTable"]//tr')[1:]
                                    for event in events:
                                        tds = event.xpath('.//td')
                                        sport_name = validate(tds[0].xpath('.//text()'))
                                        gender = ['Boys', 'Girls']
                                        for t_idx, td in enumerate(tds[1:]):
                                            name = validate(td.xpath('.//text()'))
                                            if name != 'N/A':
                                                output = [
                                                    school_name,
                                                    gender[t_idx] + ' ' +sport_name,
                                                    "",
                                                    name,
                                                    validate(td.xpath('.//a/@href')).replace('mailto:', '')
                                                ]
                                                writer.writerow(output)
                            except Exception as e:
                                pass
                page_idx += 1

scrape()
