# import packages
import pandas as pd
import numpy as np
import requests
import json
import math
from googletrans import Translator


def request_url_get(url):
    try:
        r = requests.get(url = url, timeout = 30)
        if r.status_code == 200:
            return r.text
        return None
    except RequestException:
        print('Error when accessing the url')
        return None

def parse_json(content_json):
    result_json = json.loads(content_json)
    return result_json

def request_api(url):
    result = request_url_get(url)
    result_json = parse_json(result)
    return result_json

def run(code):
    keywords = '美术培训'
    city = code
    key = KEY # please assgin with your own amap API key
    offset = 20

    index_url = f'https://restapi.amap.com/v3/place/text?keywords={keywords}&city={city}&offset={offset}&page=1&key={key}&extensions=base'
    index_result = request_api(index_url)
    pages = math.ceil(int(index_result['count']) / offset)  # total pages needed
    
    print('\n')
    print('{} pages in total'.format(pages))

    for page in range(1, pages+1):
        url = f'https://restapi.amap.com/v3/place/text?keywords={keywords}&city={city}&offset={offset}&page={page}&key={key}&extensions=base'
        result = request_api(url)
        if page == 1:
            big_list = result['pois']
        else:
            big_list.extend(result['pois'])
            
        print('It is now at page NO.{}'.format(page))
        
    return big_list

# translate Chinese information to English
# try to initiate the translator twice, in case of the transalation limitation for IP 
def trans(content,dest='en'):
    try:
        trans=Translator()
        translation=trans.translate(content,dest)
        return translation.text
    except:
        trans=Translator()
        try:
            translation=trans.translate(content,dest)
            return translation.text
        except:
            trans=Translator()
            try:
                translation=trans.translate(content,dest)
                return translation.text
            except:
                return ''

# adcode for Shenzhen (as an example)
# adcode corresponds to district
adcode = [440303,440304,440305,440306,440307,440308,
          440309,440310,440311] # shenzhen

def main():

    # scrape information from amap
    for i in range(len(adcode)):
        if i == 0:
            all_result = run(adcode[i])
        else:
            all_result.extend(run(adcode[i]))

    # extract the fields which I need
    art_school_name = []
    province = []
    city = []
    district = []
    address = []
    tel = []
    for i in range(len(all_result)):
        art_school_name.append(all_result[i]['name'])
        province.append(all_result[i]['pname'])
        city.append(all_result[i]['cityname'])
        district.append(all_result[i]['adname'])
        address.append(all_result[i]['address'])
        tel.append(all_result[i]['tel'])



    art_school = pd.DataFrame({'art_school_name':art_school_name,
                              'province':province,'city':city,'district':district,
                              'address':address,'tel':tel})
    art_school["tel"] = art_school["tel"].apply(lambda x: str(x).replace("[]","Not provided"))
    art_school["address"] = art_school["address"].apply(lambda x: str(x).replace("[]","Not provided"))


    # translation BEGINS
    # translate school name
    art_school_name_en = []
    for i in art_school['art_school_name']:
        art_school_name_en.append(trans(i))
    
    # translate province 
    prov_en = trans('广东省')
    province_en = [prov_en]*art_school.shape[0]

    # translate city
    cit_en = trans('深圳市')
    city_en = [cit_en]*art_school.shape[0]

    # translate district
    uni_district = list(art_school['district'].unique()) # find all district names  
    trans2 = Translator()
    dist_en = trans2.translate(uni_district)
    # store Chinese and Pinyin of district names into a dictionary
    dist_dic = {}
    for i in range(len(uni_district)):
        dist_dic[uni_district[i]] = dist_en[i].text

    district_en = []
    for i in art_school['district']:
        district_en.append(dist_dic[i])

    # translate address
    address_en = []
    for i in art_school['address']:
        address_en.append(trans(i))

    art_school['art_school_name_en'] = pd.Series(art_school_name_en)
    art_school['province_en'] = pd.Series(province_en)
    art_school['city_en'] = pd.Series(city_en)
    art_school['district_en'] = pd.Series(district_en)
    art_school['address_en'] = pd.Series(address_en)

    # write to excel
    art_school.to_excel('Shenzhen_art_school_en_cn.xlsx')

main()







