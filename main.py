import re
import time
import requests
from bs4 import BeautifulSoup
from ast import literal_eval as le
import pandas as pd


header = {
  'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
  'accept-encoding':'gzip, deflate, br',
  'accept-language':'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
  'cache-control':'no-cache',
  'dnt': '1',
  'pragma': 'no-cache',
  'sec-fetch-mode': 'navigate',
  'sec-fetch-site': 'none',
  'sec-fetch-user': '?1',
  'upgrade-insecure-requests': '1',
  'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
}

datas = {
    'logonInfo.logUserName' : 'vovager2003@gmail.com',
    'logonInfo.logPassword' : 'Airbus2003'
}

def parse_comp():
    f = open('Tags.txt', 'r', encoding="utf-8");
    lines = f.readlines()
    links = []
    for line in lines:
        links.append(re.sub('[\t\r\n]', '', line[line.find('https')::]))
    f.close()
    for j in range(0, len(links)):
        r = requests.get(links[j], headers=header)
        soup = BeautifulSoup(r.text, 'lxml')
        page = soup.find('div', class_='page-num').find('a', class_='page-dis').text.strip()
        end_page = int(page)
        print(end_page)
        for i in range(1, 4+1):
            data = []
            link = links[j].replace(links[j][links[j].rfind('/')::], f'/{i}.html')
            url_r = requests.get(link, headers=header)
            doc = BeautifulSoup(url_r.text, 'lxml')
            names = doc.find_all('h2', class_='company-name')
            products = doc.find_all('table', class_='company-intro')
            print(i)
            with open('Companies.txt', 'a', encoding='utf-8') as f:
                pos = 0
                for name in names:
                    comp = dict()
                    tmp_str = name.find('a').text.strip()
                    comp[tmp_str] = []
                    comp[tmp_str].append('https:'+name.find('a').get('href'))
                    prod = products[pos].find_all('tr')[1].find_all('td')[1].text.strip()
                    prod = prod.replace('\t', '').replace('\r', '').replace('\n', '').replace('\n', '').replace(' ', '')
                    comp[tmp_str].append(prod)
                    data.append(comp)
                    pos += 1
                for item in data:
                    f.write(str(item))
                    f.write('\n')
            time.sleep(3)
        time.sleep(5)

def parse_data():
    f = open('Companies.txt', 'r', encoding='utf-8')
    lines = f.readlines()
    tmp_data = []
    for line in lines:
        tmp_data.append(re.sub('[\t\r\n]', '', line))
    f.close()

    s = requests.Session()
    s.post('https://login.made-in-china.com/sign-in/?baseNextPage=https%3A%2F%2Fwww.made-in-china.com%2F', data=datas,
           headers=header)

    for i in range(18511, len(tmp_data)):
        print(i+1)
        tmp_dict = le(tmp_data[i])
        key = list(tmp_dict.keys())[0]
        url = list(tmp_dict.values())[0][0]
        r = s.get(url, headers=header)
        doc = BeautifulSoup(r.text, 'lxml')
        if doc.find('div', class_='info-cont-wp'):
            ad = doc.find('div', class_='info-cont-wp').find_all('div', class_='info')[0].text.strip()
            ph = doc.find('div', class_='info-cont-wp').find_all('div', class_='info')[1].text.strip()
            ph = re.sub('[\t\r\n\ue021]', '', ph)
            ph = ph.replace(' ', '')
            ph = ph.replace(ph[ph.find('LocalTime')::], '')
            tmp_dict[key].append(ad)
            tmp_dict[key].append(ph)
            file = open('new_comp.txt', 'a', encoding='utf-8')
            file.write(str(tmp_dict))
            file.write('\n')
            file.close()
            time.sleep(3)
        else:
            if doc.find('ul', class_='sr-nav-main'):
                new_link = doc.find('ul', class_='sr-nav-main').find_all('li', class_='sr-nav-item')
                new_href = new_link[len(new_link)-1].find('a').get('href')
            elif doc.find('ul', class_='sr-virtual-nav-main'):
                new_link = doc.find('ul', class_='sr-virtual-nav-main').find_all('li', class_='sr-virtual-nav-item')
                new_href = new_link[len(new_link)-1].find('a').get('href')

            time.sleep(0.5)

            r2 = s.get(new_href, headers=header)
            doc2 = BeautifulSoup(r2.text, 'lxml')

            address = doc2.find('span', class_='contact-address').text.strip()
            tmp = address[address.find('China')+5::].strip()
            address = address[0:address.find('China')] + 'China ' + tmp
            arr = doc2.find_all('div', class_='info-item')
            ph = ''
            for elem in arr:
                if elem.find('div', class_='info-label'):
                    if elem.find('div', class_='info-label').text.strip() == 'Telephone:':
                        ph = elem.find('div', class_='info-fields').text.strip()

            tmp_dict[key].append(address)
            tmp_dict[key].append(ph)
            time.sleep(3)

            file = open('new_comp.txt', 'a', encoding='utf-8')
            file.write(str(tmp_dict))
            file.write('\n')
            file.close()

def collect_data():
    dict_ans = {'Страна': [], 'Название': [], 'Сайт' : [], 'Деятельность' : [], 'Адрес':[], 'Телефон':[]}
    f = open('new_comp.txt', 'r', encoding='utf-8')
    lines = f.readlines()
    tmp_data = []
    for line in lines:
        tmp_data.append(re.sub('[\t\r\n]', '', line))
    f.close()
    kol = 0
    for item in tmp_data:
        tmp_dict = le(item)
        country = tmp_dict.keys()
        dict_ans['Страна'].append('Ch')
        dict_ans['Название'].append(list(country)[0])
        dict_ans['Сайт'].append(tmp_dict[list(country)[0]][0])
        dict_ans['Деятельность'].append(tmp_dict[list(country)[0]][1])
        tmp_dict[list(country)[0]][2] = tmp_dict[list(country)[0]][2].replace('\t', '')
        tmp_dict[list(country)[0]][2] = tmp_dict[list(country)[0]][2].replace('\n', '')
        addr = tmp_dict[list(country)[0]][2].split(' ')
        addr = list(filter(lambda x: x!='', addr))
        addr = ' '.join(addr)
        dict_ans['Адрес'].append(addr)
        dict_ans['Телефон'].append(tmp_dict[list(country)[0]][3])

        ##print(dict_ans)
    df = pd.DataFrame(dict_ans)
    df.to_excel('./Data_China.xlsx')

if __name__ == '__main__':
    ##parse_comp()
    ##parse_data()
    collect_data()