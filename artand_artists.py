#!/usr/bin/env python
# coding: utf-8

# import packages
import requests
from bs4 import BeautifulSoup
import os
import re
import pandas as pd
from selenium import webdriver
import time

headers = {'User-Agent':'Mozilla/5.0 3578.98 Safari/537.36'}
def getHTMLText(url,headers):
    try:
        r = requests.get(url,headers=headers,timeout=30)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return ""

def log_in_get_html_text():
    '''
    1. log in with account
    2. scroll down the page
    3. click "load more" button
    4. get HTML test
    '''
    # open with Chrome
    driver=webdriver.Chrome('/Users/xxx/opt/anaconda3/chromedriver')
    # open artand and we need to log in
    driver.get("https://artand.cn/")
    # slow down the operation
    time.sleep(2) 

    # log in window automatically pops up
    # find the place where we enter username and password  
    # enter username                           
    driver.find_element_by_css_selector('body > div:nth-child(8) > div > div > div.flipper > form > div.msg_content.login_code > div:nth-child(4) > div:nth-child(1) > input').send_keys('my_username') 
    time.sleep(2)
    # enter passward
    driver.find_element_by_css_selector('body > div:nth-child(8) > div > div > div.flipper > form > div.msg_content.login_code > div:nth-child(4) > div:nth-child(2) > input').send_keys('my_password')
    time.sleep(2)
    # click the log in button
    driver.find_element_by_css_selector('body > div:nth-child(8) > div > div > div.flipper > form > div.msg_content.login_code > div:nth-child(4) > div:nth-child(3) > a').click()

    time_start=time.time()
    # scroll down the page for 7 times
    time.sleep(3)
    for i in range(7):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight); var lenOfPage=document.body.scrollHeight; return lenOfPage;")
        time.sleep(3)
    
    # click "load more" for 1000 times
    for i in range(1000):
        driver.find_element_by_css_selector('#feed_list > div.left_feed > div.ajax_load_more').click()
        time.sleep(3)
        print(i)
    time_end=time.time()
    print('time cost',time_end-time_start,'s')

    html=driver.page_source
    soup=BeautifulSoup(html,"html.parser")
    return soup


def get_general_info(soup):
    '''
    get uid, url, name of each artist
    '''
    artist_urls = []
    artist_names = []
    artist_uids = []

    mainurl = 'https://artand.cn'
    for item in soup.find_all('a','btn t_links_blue padding_r3'):
        uid = item.get('href')[5:]
        if uid not in artist_uids:
            artist_uids.append(item.get('href')[5:])
            artist_urls.append(mainurl+item.get('href'))
            artist_names.append(item.get_text())

    df_general = pd.DataFrame({'uid':artist_uids,'name':artist_names,'link':artist_urls})
    return df_general


def get_detail_info(df_general):
    '''
    enter the url for each artist
    get location, follower, number of artwork, introduction
    '''

    time_start=time.time()
    detail_dic = {}
    pat1 = re.compile(r'[0-9]+件作品')
    pat2 = re.compile(r'[0-9]+位圈内人关注')

    pat_style = re.compile(r'<style')
    pat_br  = re.compile(r'<br>|</br>|<br/>')

    for i in range(df_general.shape[0]):  
        uid = df_general['uid'].loc[i]
        name = df_general['name'].loc[i]
    
        html = getHTMLText('https://artand.cn/uid/'+uid+'/about',headers=headers)
        soup = BeautifulSoup(html,"html.parser")

        detail_dic[uid] = {}
        detail_dic[uid]['name'] = name
    
        # get artist's location
        if soup.find('h4') is not None:
            detail_dic[uid]['location'] = soup.find('h4').get_text() 
        if soup.find('h4') is None:
            detail_dic[uid]['location'] = ''
    
        # verification
        if soup.find('h2').a is not None:
            detail_dic[uid]['verification'] = soup.find('h2').a.get('title') 
        if soup.find('h2').a is None:
            detail_dic[uid]['verification'] = ''
    
        # number of artwork, follower
        detail_dic[uid]['num_of_work'] = ''
        detail_dic[uid]['follower'] = ''
    
        for item in soup.find_all('p'):
            if item.span is not None:
                for j in item.find_all('span'):
                    if len(j.get_text()) != 0:
                        match = pat1.search(j.get_text())
                        if match:
                            detail_dic[uid]['num_of_work'] = int(match.group(0).split('件')[0])
                        match2 = pat2.search(j.get_text())
                        if match2:
                            detail_dic[uid]['follower']= int(match2.group(0).split('位')[0]) 
    
        # introduction
        intro = []
        for item in soup.find_all('div','resume'):
            if item.p is not None: # if introduction is in between <p><p/>
                for j in item.find_all('p'):
                    info = j.get_text().replace(u'\xa0', u'')
                    if len(info)!=0:
                        intro.append(info)
            else:
                for i in item.children:
                    i = str(i).strip()
                    i = i.replace(u'\xa0', u' ') # delete \xa0
                    match = pat_style.search(i) 
                    if not match:  # we don't care about style, delete information about style
                        match2 = pat_br.search(i) 
                        if not match2:  # delete <br/>
                            if len(i) != 0: # delete blank
                                intro.append(i)
        txt = ', '.join(intro)
        detail_dic[uid]['intro'] = txt

    time_end=time.time()
    print('time cost',time_end-time_start,'s')

    result = pd.DataFrame(dict([(k,pd.Series(v)) for k,v in detail_dic.items()])).T
    result = result.reset_index()
    result.rename(columns={'index':'uid'},inplace=True)

    return result

def main():
    soup = log_in_get_html_text()
    df_general = get_general_info(soup)
    df_detail = get_detail_info(df_general)

main()