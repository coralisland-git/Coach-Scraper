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
    return item.replace(u'\xa0', ' ').replace(u'\u2013', '-').encode('ascii', 'ignore').encode("utf8").strip()

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
        writer.writerow(["School", "Sports",  "Position", "Name", "Email", "Year"])
        base_url = 'https://schools.wiaawi.org'
        url = 'https://schools.wiaawi.org/Directory/School/DirectoryLetter?searchOpt=new'
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': 'ASP.NET_SessionId=dgerrn2q0c3uows11cvh3ilh; _ga=GA1.2.1427195903.1582537912; _gid=GA1.2.473663136.1582537912',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        for alpha in string.ascii_lowercase:
            formdata = {
                'LetterBtn': alpha.upper(),
                'X-Requested-With': 'XMLHttpRequest'
            }
            source = session.get(url, headers=headers, data=formdata).text
            response = etree.HTML(source)
            schools = response.xpath('.//div[@id="ReportData"]//tbody//tr//form')
            for school in schools:
                s_id = validate(school.xpath('./@action')).split('?orgID=')[1].split('&')[0]
                if s_id not in history:
                    history.append(s_id)
                    try:
                        school_name = validate(school.xpath('.//text()'))
                        s_url = 'https://schools.wiaawi.org/Directory/School/CoachList?orgID={}&CoachRole=29&AllCoaches=False'.format(s_id)
                        year = 2016
                        for y_idx in range(0, 4):
                            s_formdata = {
                                'CoachYear': str(year+y_idx),
                                'X-Requested-With': 'XMLHttpRequest'
                            }
                            s_response = etree.HTML(session.get(s_url, headers=headers, data=s_formdata).text)
                            events = s_response.xpath('.//div[@id="coachListItems"]/div')
                            for event in events:
                                tds = event.xpath('./div')
                                output = [
                                    school_name,
                                    validate(eliminate_space(validate(tds[0].xpath('.//text()')).split(' '))),
                                    "",
                                    validate(eliminate_space(validate(tds[1].xpath('.//text()')).split(' '))),
                                    validate(eliminate_space(validate(tds[3].xpath('.//text()')).split(' '))),
                                    str(year+y_idx)+'-'+str(year+y_idx+1)
                                ]
                                writer.writerow(output)
                    except Exception as e:
                        pass

scrape()