import csv
import re
import pdb
import requests
from lxml import etree
import json
import os
from base import *
from ast import literal_eval
from datetime import datetime

def main():
    output_list = []
    session = requests.Session()
    file_name = 'output/' + os.path.splitext(os.path.basename(__file__))[0] + datetime.now().strftime('_%Y_%m_%d_%H_%M_%S') +'.csv'
    with open(file_name, mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["School", "Sports",  "Position", "Name", "Email"])
        base_url = 'https://www.mshsaa.org'
        url = "https://www.mshsaa.org/Schools/"
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Cookie': '__utmc=92616065; ASP.NET_SessionId=http1frnpa3dpon5vcxs1yly; __utma=92616065.1821169365.1582752291.1582883982.1582884087.7; __utmz=92616065.1582884087.7.5.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=https://www.mshsaa.org/MySchool/Coaches.aspx?s%3D3%26alg%3D5; __utmt=1; __utmb=92616065.50.10.1582884087',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'
        }
        response = session.get(url, headers=headers).text        
        schools = literal_eval(validate(response.split("schoolSelect_txtSchoolName1'),")[1].split(")})")[0]))
        s_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',                
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': '__utmc=92616065; ASP.NET_SessionId=http1frnpa3dpon5vcxs1yly; __utma=92616065.1821169365.1582752291.1582883982.1582884087.7; __utmz=92616065.1582884087.7.5.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=https://www.mshsaa.org/MySchool/Coaches.aspx?s%3D3%26alg%3D5; __utmt=1; __utmb=92616065.51.10.1582884087',                
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'
        }
        for school in schools:
            try:
                formdata = {
                    '__EVENTTARGET': 'ctl00$contentMain$lbtnSchoolSearch',
                    '__EVENTARGUMENT': '',
                    '__VIEWSTATE': 'qB8UDFeGMZGjTNO7KCTR8pLWzo2a3HhNR+EbGZEGvkb4/uzVqrQo9RuTwzL6bQLVTB6rNUnJrQ+Q74HM/s/utEx4Y0gwB8U0WXOvOAVE587w9v10VIwLhV4RWQFtlmid8CG0+7EQ6fI9HJZ95J/YRnnlJ8bvIL94DjotKB+IyeIJGHOVc4JVT+HePLpRAWA9OChDBILWF8Drxe+voSZ5JQ6/5ig=',
                    '__VIEWSTATEGENERATOR': '933FF48B',
                    '__VIEWSTATEENCRYPTED': '',
                    '__EVENTVALIDATION': 'RQnfnGI1hkE+jNOVsogJm+svQyoUoAcn9UlT3NIOHlMhf+pL6eJ2H1Tj+wI/QK7l+7AwxfKb8GQamATNT3m0uCeeTIXI/JSKbhoWFz3HnRRpXXXF9MW+yzPPI1CSxdek8xHJN+82z+mobF2OIfFDQmMNMnVT7suoBwl0mSVkkW8Oly3M/rPo8jPTcaTqy5QDTGvvGDW+O9hMTNNjCZ0Xit138bIWMVijTEmPnxNe9oEDY2e5QvKx3Q1qvd7df3bYhPgYVehDJZZ6bOpPVqRN28k1GAwe/HC0NeqR0FggMmD5o3qM',
                    'ctl00$contentMain$schoolSelect$txtSchoolName1': school,
                    'ctl00$contentMain$LoginView1$ucLogin$Login$UserName': '',
                    'ctl00$contentMain$LoginView1$ucLogin$Login$Password': ''
                }
                s_name = validate(school)
                s_response = session.post(url, headers=s_headers, data=formdata).text
                s_data = etree.HTML(s_response)
                s_website = validate(s_data.xpath('.//a[@id="ctl00_SchoolHeader_aMySchoolWebsite"]/@href'))
                s_email = validate(s_website.split('://')[-1].split('/')[0].replace('www.', ''))
                sports = s_data.xpath('.//div[@class="footerContent"]//div[contains(@class, "footerLinks")]//ul//a')                
                for sport in sports:
                    e_sport = validate(sport.xpath('.//text()'))
                    if is_in_needed_sports(e_sport):
                        e_url = base_url + validate(sport.xpath('./@href')).replace('Schedule', 'Coaches')
                        e_response = session.get(e_url).text
                        e_data = etree.HTML(e_response)
                        e_check = {
                            'status' : True,
                            'idx' : 0,
                            'checked' : False
                        }
                        sections = e_data.xpath('.//div[@class="formsharp"]//div[@class="fs_item"]')                    
                        for section in sections:
                            position = validate(section.xpath('.//h1//text()')).replace('(es)', '')
                            events = section.xpath('.//table//tr')
                            for event in events:
                                try:
                                    content = eliminate_space(event.xpath('.//text()'))
                                    e_name = get_name(content[0])
                                    if len(content) > 1:
                                        position = content[1]
                                    # e_emails = generate_email(e_name, s_email) if e_check['status'] else ['']
                                    # if not e_check.get('checked'):
                                    #     e_check = check_email_combination(session, e_emails)
                                    if s_email != '':
                                        s_email = '@' + s_email
                                    e_email = verify_email(session, generate_email(e_name, s_email))
                                    output = [
                                        s_name, e_sport, "HEAD COACH", 
                                        e_name, e_email
                                    ]
                                    writer.writerow(output)
                                except Exception as e:
                                    print(output, e)
                                    pass
            except Exception as se:
                print(school, se)
                pass

if __name__ == '__main__':
    main()