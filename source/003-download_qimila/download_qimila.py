# -*- coding: utf-8 -*-

#py 3.5.x

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
import unittest, time, os
import win32api
import win32con
from bs4 import BeautifulSoup
import sqlite3
import xlwt
import configparser


import adapt_code

class BaseInfo():
    def __init(self):
        self.baseUrls=[]
        self.db_dbName=''
        self.db_tbName=''
        self.db_titleName=[]
        pass

BI=BaseInfo()


VK_CODE ={'enter':0x0D, 'down_arrow':0x28}

#键盘键按下
def keyDown(keyName):
    win32api.keybd_event(VK_CODE[keyName], 0, 0, 0)
#键盘键抬起
def keyUp(keyName):
    win32api.keybd_event(VK_CODE[keyName], 0, win32con.KEYEVENTF_KEYUP, 0)
    

class TestDemo(unittest.TestCase):
    def setUp(self):
        global BI
        
        self.driver=webdriver.Ie(executable_path='C:\\Program Files\\Internet Explorer\\IEDriverServer.exe')
        adapt_code.preProc(BI)
        
    def test_dataPickerByRightKey(self):
        #global value
        global BI
        
        
        while True:
            try:
                cur_url = BI.baseUrls.pop(0)
            except:
                return
        

            print ("Proc: %s" % cur_url)
            self.driver.get(cur_url)
            # 将窗口最大化
            self.driver.maximize_window()
            # 暂停5秒，目的防止页面有一些多余的弹窗占据焦点
            time.sleep(3)
            
            #已经打开界面，现在或者网页编码
            source=self.driver.page_source
            soup = BeautifulSoup(source,"lxml")
            
            #解析
            res,newUrls = adapt_code.soupParse(cur_url, soup, BI)
            BI.baseUrls+=newUrls
            
            #存入数据库
            db = sqlite3.connect(BI.db_dbName)        #连接数据库
            db_cu = db.cursor()                     #游标        
        
            for line in res:
                rows=[iitt.replace("'", "") for iitt in line]
                insertString='insert into '+BI.db_tbName+" ('"+        "', '".join(BI.db_titleName)        +"') values("
                insertString+="'"+        "', '".join(rows)        +"'"
                insertString+=')'
        
                try:
                    print (insertString)
                except:
                    print ("Some un-printed Text")
        
                db_cu.execute(insertString)
                #insert_index+=1
                db.commit()
            db.close()
            
        #导出数据到excel文件
        db = sqlite3.connect(BI.db_dbName)
        import pandas.io.sql as sql
        allData=sql.read_sql_query('SELECT * FROM '+BI.db_tbName, db)
        
        titles=allData.columns
        #allData.irow(row_index)[col_index]
        #allData.shape
        
        w = xlwt.Workbook(encoding = 'utf-8')
        w_s = w.add_sheet('My Worksheet')
        
        rows,cols=allData.shape
        
        for col_index in range(cols):
            w_s.write(0, col_index, titles[col_index])
            
        for row_index in range(rows):
            for col_index in range(cols):
                w_s.write(row_index+1, col_index, allData.iloc[row_index][col_index])
                
        w.save('outInfo.xls')        
        

            
    def tearDown(self):
        global BI
        self.driver.quit()
        adapt_code.postProc(BI)
        
if __name__ == '__main__':
    #从配置文件获取环境信息    
    myConfig = configparser.ConfigParser()
    myConfig.read("config.conf")
    BI.baseUrls=myConfig.get('website', 'baseUrls').split(",")
    BI.db_dbName=myConfig.get('local', 'dbName')
    BI.db_tbName=myConfig.get('local', 'dbTbName')
    BI.db_titleName=myConfig.get('local', 'dbTitleName').split(",")

    #开始处理
    print ("Start...")
    unittest.main()
    print ("Proc Over.")

