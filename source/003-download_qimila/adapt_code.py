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
    os.system("reset_db.bat")
    
    #如果用于存放信息的数据库文件还不存在，需要用户手工自己创建
    if not os.path.isfile(BI.db_dbName):
        #CREATE TABLE 'sa_data' (id INTEGER UNSIGNED NOT NULL PRIMARY KEY, 'ios_version' TEXT NOT NULL, 'item' TEXT, 'suitable' TEXT, 'affect' TEXT, 'description' TEXT, 'CVE' TEXT, 'other' TEXT);
        print ("Please create DB firstly(%s)" % BI.db_dbName)
        sys.exit(0)    
    pass
    
def postProc(BI):
    pass
    
def soupParse(soup, BI, driver):
    
    #获取数据库中的节目记录
    db = sqlite3.connect(BI.db_dbName)
    import pandas.io.sql as sql
    allData=sql.read_sql_query('SELECT * FROM '+BI.db_tbName, db)
    saved_program_names=allData["program_name"]

    
    ul=soup.findAll("ul")[3]
    lis=ul.findAll("li")
    links=["http://qimila.vip/"+item.find("a").get("href") for item in lis]
    descriptions=[item.find("a").getText() for item in lis]
    program_names=[item.split(" ")[0]+" "+item.split(" ")[1] for item in descriptions]
    dates=[item.split(" ")[1] for item in descriptions]
    file_name=[""]*len(dates)
    file_size=[0]*len(dates)
    
    res=list(zip(dates, program_names, file_name, file_size, descriptions, links))
    
    for item in res:
        try:
            print (item)
        except:
            print ("Some un-printed Text")
            
    #与数据库中的记录进行比较，看看是否有新发布的节目
    new_program=[item for item in res if item[1] not in saved_program_names]
    
    #每次最多处理3个
    new_program = new_program[:3]
    
    downloaded_program=[]
    #开始下载文档
    for item in new_program:
        cur_url = item[5]
        driver.get(cur_url)
        
        tryTimes=5
        while tryTimes:
            tryTimes-=1
            try:
                # 将窗口最大化
                self.driver.maximize_window()        
                # 暂停5秒，目的防止页面有一些多余的弹窗占据焦点
                time.sleep(5)
            
                #已经打开界面，现在或者网页编码
                source=driver.page_source
                soup = BeautifulSoup(source,"lxml")
            
                #解析
                links=soup.findAll("a").get("href")
                links=[ii for ii in links if "share.weiyun.com" in ii]
                if len(links)==0:
                    continue
                
                print (links[0])
                break
            except:
                continue
        
        
        
        #
        downloaded_program.append(item[:-1])
        

    return downloaded_program

