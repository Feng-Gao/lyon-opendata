#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import re
import scraperwiki
import datetime

import sys  

reload(sys)  
sys.setdefaultencoding('utf8')

#NOTE that we parse dataproduct and dataapi seperately and the dirty solution is manually replace the url and set index accordingly
#to crawl both product and api, so do not forget to set file writer method to 'a' when you work on api list
base_url = 'https://data.grandlyon.com/acceder-aux-donnees/?&P='
index = 1
#manually check on the website and set the max_index accordingly
max_index = 134

#we need random ua to bypass website security check
ua = UserAgent()
headers = {'User-Agent':ua.random}

dataset_count = 1

for i in range(index,max_index+1):
    url = base_url + str(i)
    print(url)
    result = requests.get(url,headers=headers)
    soup = BeautifulSoup(result.content,features='lxml')
    #fetch all dt blocks
    package_blocks = soup.find_all("div",attrs={'class':'result_item'})

    for p in package_blocks:
        package_name  = '"'+p.find(attrs={'class':'result_item_title'}).a.text+'"'
        print(package_name)
        package_url = p.find(attrs={'class':'result_item_title'}).a['href']
        print(package_url)
        package_org = '"'+p.find(attrs={'class':'result_item_fournisseur'}).span.text+'"'
        
        package_view = p.find(attrs={'class':'result_item_consultation'}).p.span.text.strip().split(' ')[0]

        result = requests.get(package_url,headers=headers)
        soup = BeautifulSoup(result.content,features='lxml')

        package_desc = '"'+soup.find(attrs={'id':'headerSingleTexte'}).p.text+'"'
        package_topics = '|'.join([x.text for x in soup.find(attrs={'class':'categorie'}).td.find_all('span')])
        package_tags = soup.find(attrs={'class':'keyword'}).td.text.replace(',','|')
        try:
            package_format = '|'.join([x.text for x in soup.find(attrs={'class':'format'}).find_all('span')])
        except Exception as ex:
            print(ex)
            print("MISSING Format")
            package_format = 'MISSING'
        package_created = soup.find('th',string='Publication initiale').parent.td.text
        try:
            package_frequency = soup.find('th',string='Fréquence de mise à jour').parent.td.text
        except Exception as ex:
            print(ex)
            print("MISSING Frequency")
            package_frequency = 'MISSING'

        #output the result
        #note for tags, it might be splited by , or chinese , or chinese 、
        row = package_url +','+ package_name+','+package_desc+','+package_org+','+package_topics \
                +','+package_tags+','+package_created+','+package_frequency\
                +','+package_format+'\n'
        print(row)
        package_dict = {
                    'today':datetime.date.today().strftime("%m/%d/%Y"),
                    'url':package_url,
                
                    'name':package_name,
                    'desc':package_desc,
                    'org':package_org,
                    'topics':package_topics,
                    'tags':package_tags,
                    'format':package_format,
                    'created':package_created,
                    'frequency':package_frequency,
                    'view':package_view,
                    
        }
    
        scraperwiki.sqlite.save(unique_keys=['today','url'],data=package_dict)
        print('****************end---'+package_name+'---end****************')
        dataset_count = dataset_count + 1
print("everything OK now. Total daasetcount is"+str(dataset_count))
