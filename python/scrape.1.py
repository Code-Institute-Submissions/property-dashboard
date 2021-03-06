from bs4 import BeautifulSoup
# from urllib.request import urlopen
import re
import pprint
import json
import urllib3
http = urllib3.PoolManager()
txt_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3)',
    'Accept-Language': 'en-US',
    'Accept-Encoding': 'text/html'
}


def location(county, locality):
    return 'http://www.daft.ie/'+county+'/houses-for-sale/'+locality

def format_html_to_xml_soup(url):
    f = http.request(url, '', txt_headers)
    response = http.request.urlopen(f)
    return BeautifulSoup(response, 'lxml')

def get_number_of_pagination_pages(soup):
    number_properties = soup.find(id="sr-sort").next_sibling.next_sibling.next_sibling.next_sibling.string
    x = list(number_properties)
    y=""
    for char in x:
        if char.isdigit():
            y+=char
    number_of_pages = (int(y)//20)*20
    return number_of_pages

def get_urls_for_each_page(url, number_of_pages):
    urls=[]
    while number_of_pages>=0:
        paginated_page = url+'/?offset='+str(number_of_pages)
        soup = format_html_to_xml_soup(paginated_page)
        divs = soup.find_all('div', class_="search_result_title_box")
        
        for div in divs:
            a=div.find('a')
            urls.append("http://www.daft.ie" + a['href'])
        
        print(urls)
        number_of_pages -= 20
    return urls

def get_data_from_each_page(urls):
    parsed_list = []
    full_dict_of_data = []
    
    for page in urls:
        parsed_single_page = format_html_to_xml_soup(page)
        
        # Ber Number
        # ber_number = parsed_single_page.find("div", attrs={"id": "smi-ber-details"}).next_sibling
        # number_from_text = [int(s) for s in ber_number.split() if s.isdigit()]
        
        json_string = re.findall(r"{\W\w.*\W}", parsed_single_page.text)[1].split(',"')
        for i in json_string:
            parsed_list.append(i.replace('"', '').replace('{', '').replace('}', ''))
        
        # split list into 2 lists
        dictionary_keys = [i.split(':', 1)[0] for i in parsed_list]
        dictionary_values = [i.split(':', 1)[1] for i in parsed_list]
        # combine 2 lists into dictionary
        dictionary = dict(zip(dictionary_keys, dictionary_values))
        dictionary['url'] = page
        full_dict_of_data.append(dictionary)
    
    return full_dict_of_data

def parse_the_data(data):
    for v in data:
        del v['environment']
        del v['platform']
        del v['currency']
        del v['ad_ids']
        if 'price' in v:
            v['price'] = int(v['price'])
        else:
            v['price'] = "Not Given"
        v['longitude'] = float(v['longitude'])
        v['latitude'] = float(v['latitude'])
        if 'surface' in v:
            v['surface'] = float(v['surface'])
        else:
            v['surface'] = "Not Given"
        v['beds'] = int(v['beds'])
        v['seller_id'] = int(v['seller_id'])
        v['bathrooms'] = int(v['bathrooms'])
        v['no_of_photos'] = int(v['no_of_photos'])
        v['facility'] = (v['facility']).split(",")
    return data

def filter_data(list_of_dict_data):
  updated_list = []
  for v in list_of_dict_data:
    if v['surface'] != "Not Given" and v['price'] != "Not Given":
      updated_list.append(v)
      
  return updated_list

# ===================================================================

# URL = location('dublin', 'ranelagh')

# soup = format_html_to_xml_soup(URL)

# number_of_pages = get_number_of_pagination_pages(soup) 

# urls = get_urls_for_each_page(URL, number_of_pages)  

# raw_data = get_data_from_each_page(urls)

# data = parse_the_data(raw_data)

# ====================================================================

        
# data = get_data_from_each_page(sample_data)    
   
# ==================GET 20 PAGES FROM DUBLIN==================================================

print("=========================================")
print("===================URL======================")
URL = location('dublin', 'ranalagh')
print(URL)

print("=========================================")
print("===================SOUP======================")
soup = format_html_to_xml_soup(URL)
print(soup)

print("=========================================")
print("===================SOUP======================")
number_of_pages = get_number_of_pagination_pages(soup)
print(number_of_pages)

print("=========================================")
print("===================03======================")
urls = get_urls_for_each_page(URL, number_of_pages)
print(urls)



print("=========================================")
print("===================04======================")
raw_data = get_data_from_each_page(urls)
print(raw_data)
with open('data/testdata.json', 'w') as tout:
    json.dump(raw_data, tout, sort_keys=True,indent=4, separators=(',', ': '))

print("=========================================")
print("===================05======================")
unfiltered_data = parse_the_data(raw_data)
data = filter_data(unfiltered_data)
print(data)

with open('data/sampledata.json', 'w') as fout:
    json.dump(data, fout, sort_keys=True,indent=4, separators=(',', ': '))

