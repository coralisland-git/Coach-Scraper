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
    return item.replace(u'\u2013', '-').encode('ascii', 'ignore').encode("utf8").strip().replace('\t', '').replace('\n', ' ').replace('\r', '')

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
        base_url = 'https://portal.tssaa.org/common/directory/'
        urls = [ "", '?type=middle']
        for url in urls:
            url = base_url + url
            source = session.get(url).text
            data = re.sub("(\w+):", r'"\1":', validate(source.split('source: ')[1].split('autoSelect:')[0])[:-1])
            schools = json.loads(data)
            for school in schools:
                s_url = base_url + "?id=" + school.get('id')
                s_response = etree.HTML(session.get(s_url).text)
                school_name = validate(school.get('name'))
                tables = s_response.xpath('.//div[@class="card mb-3"]')[1:]
                for table in tables:
                    sport_name = validate(table.xpath('.//div[contains(@class, "card-header")]//text()'))
                    events = table.xpath('.//tr[@class="staffPerson"]')
                    for event in events:
                        tds = event.xpath('.//td')
                        e_tmp = eliminate_space(validate(tds[2].xpath('.//text()')).replace('"', '').replace(')', '').split(','))
                        email = ''
                        try:
                            email = e_tmp[1]  + '@' + e_tmp[3][::-1]
                        except:
                            pass
                        output = [
                            school_name,
                            sport_name,
                            validate(tds[1].xpath('.//text()')),
                            validate(tds[0].xpath('.//text()')),
                            email
                        ]
                        writer.writerow(output)

scrape()
