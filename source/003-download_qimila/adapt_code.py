# -*- coding: utf-8 -*-

#py 3.5.x

#import your packet
import sqlite3
import xlwt
import re
import os
import time
from bs4 import BeautifulSoup

def preProc(BI):
    #os.system("reset_db.bat")
    
    #如果用于存放信息的数据库文件还不存在，需要用户手工自己创建
    if not os.path.isfile(BI.db_dbName):
        #CREATE TABLE 'sa_data' (id INTEGER UNSIGNED NOT NULL PRIMARY KEY, 'ios_version' TEXT NOT NULL, 'item' TEXT, 'suitable' TEXT, 'affect' TEXT, 'description' TEXT, 'CVE' TEXT, 'other' TEXT);
        print ("Please create DB firstly(%s)" % BI.db_dbName)
        sys.exit(0)    
    pass
    
def postProc(BI):
    pass
    
def soupParse(cur_url, soup, BI):
    
    newUrls=[]
    
    #获取数据库中的节目记录
    db = sqlite3.connect(BI.db_dbName)
    import pandas.io.sql as sql
    allData=sql.read_sql_query('SELECT * FROM '+BI.db_tbName, db)
    saved_program_names=list(allData["program_name"])
    
    
    #qimila的入口页没有微云链接，具体某个节目的页面有微云链接。所以以是否有微云链接作为判断是否是具体节目页的标准
    links=soup.findAll("a")
    links=[item.get("href") for item in links]
    links=[item for item in links if (item is not None) and ("share.weiyun.com" in item)]
    
    if len(links)==0:       #这是旗米拉的入口页
        for ul in soup.findAll("ul"):
            lis=ul.findAll("li")
            if len(lis)<10:
                continue
            links=["http://qimila.vip/"+item.find("a").get("href") for item in lis]
            descriptions=[item.find("a").getText() for item in lis]
            program_names=[item.split(" ")[0]+" "+item.split(" ")[1] for item in descriptions]
            dates=[item.split(" ")[1] for item in descriptions]
            file_name=[""]*len(dates)
            break
    
        res=list(zip(dates, program_names, file_name, descriptions, links))
    
        for item in res:
            try:
                print (">>>>")
                print (item)
            except:
                print (">>>>Some un-printed Text")
            
        #与数据库中的记录进行比较，看看是否有新发布的节目
        new_program=[item for item in res if item[1] not in saved_program_names]

    
        downloaded_program=[]
        newUrls = [item[4] for item in new_program]
    else:               #处理具体的下载页
        newUrls=[]
        #解析
        links=soup.findAll("a")
        links=[item.get("href") for item in links]
        links=[item for item in links if item is not None]
        links=[item for item in links if (item is not None) and ("share.weiyun.com" in item)]
        if len(links)==0:
            downloaded_program=[]
        else:
            print (">>>>")
            #print (links[0])
            
            link=links[0]
            #datetime,program_name,file_name,description
            description=soup.find("title").getText()
            temp=description.split(" ")
            datetime=temp[1]
            program_name=temp[0]+" "+temp[1]
            file_name=''

            #下载
            print (">>>>%s : %s" % (program_name, link))
            file_name='waiting to define.mkv'
            
            downloaded_program=[[datetime, program_name, file_name, description]]
            newUrls.append(link)
    
    return downloaded_program,newUrls
        
