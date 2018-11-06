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
import re

import adapt_code

class BaseInfo():
    def __init__(self):
        self.baseUrls=[]
        self.db_dbName=''
        self.db_tbName=''
        self.db_titleName=[]
        
        self.browser='chrome'       #iexplorer/chrome/firefox
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
        
        if BI.browser=="chrome":
            chrome_opt=webdriver.chrome.options.Options()
            #chrome_opt.add_argument("--headless")
            self.driver=webdriver.Chrome(executable_path='C:\\Program Files (x86)\\Google\\Chrome\\Application\\chromedriver.exe', options=chrome_opt)
        elif BI.browser=="iexplorer":
            ie_opt = webdriver.ie.options.Options()
            #ie_opt.add_argument("--headless")
            self.driver=webdriver.Ie(executable_path='C:\\Program Files\\Internet Explorer\\IEDriverServer.exe', options=ie_opt)
        elif BI.browser=="firefox":
            pass
        else:
            assert 0
            
        self.driver.set_page_load_timeout(30)
        self.driver.maximize_window()
        adapt_code.preProc(BI)
        
    def test_dataPickerByRightKey(self):
        #global value
        global BI
        
        weiyun_links=[]
        
        
        while True:
            try:
                cur_url = BI.baseUrls.pop(0)
            except:
                break
        

            print (">>>>Proc: %s" % cur_url)
            try:
                self.driver.get(cur_url)
            except TimeoutException:
                #self.driver.execute_script('window.stop()')
                
                try:
                    print ("time out after 30 seconds when loading page")
                    self.driver.execute_script('window.stop()') #当页面加载时间超过设定时间，通过执行Javascript来stop加载，即可执行后续动作
                except:
                    pass
                
            # 暂停n秒，目的防止页面有一些多余的弹窗占据焦点
            time.sleep(1)
            
            #已经打开界面，现在获得网页编码
            source=self.driver.page_source
            soup = BeautifulSoup(source,"lxml")
            
            #解析
            print (">>>>Soup Paser")
            res,newUrls = adapt_code.soupParse(cur_url, soup, BI)
            
            #分离出微云的链接和主站链接
            temp_weiyun_links=[item for item in newUrls if re.search(r'''share.weiyun.com''', item)]
            newUrls=[item for item in newUrls if not re.search(r'''share.weiyun.com''', item)]
            
            if temp_weiyun_links:
                assert 1==len(temp_weiyun_links)
                weiyun_links+=[temp_weiyun_links+res[0]]
            
            if True:
                BI.baseUrls+=newUrls
            else:
                BI.baseUrls+=newUrls[:3]
            
            #存入数据库
            db = sqlite3.connect(BI.db_dbName)        #连接数据库
            db_cu = db.cursor()                     #游标        
        
            for line in res:
                rows=[iitt.replace("'", "") for iitt in line]
                insertString='insert into '+BI.db_tbName+" ('"+        "', '".join(BI.db_titleName)        +"') values("
                insertString+="'"+        "', '".join(rows)        +"'"
                insertString+=')'
        
                try:
                    print (">>>>")
                    print (insertString)
                except:
                    print (">>>>Some un-printed Text")
        
                db_cu.execute(insertString)
                #insert_index+=1
                db.commit()
            db.close()
            
        #下载weiyun_links中保存的要下载的链接
        print (">>>>Doneload weiyun file:")
        for wei_link in weiyun_links:
            print ("<>URL: %s" % wei_link[0])
            print ("<>FileName: %s" % wei_link[2])
            self.driver.get(wei_link[0])
            time.sleep(3)
            
            #已经打开界面，现在获得网页编码
            source=self.driver.page_source
            soup = BeautifulSoup(source,"lxml")
            
            #找到文件下载链接
            a = self.driver.find_elements_by_xpath('//*[@id="app"]/div/div[2]/div/div/div/div[2]/div[1]/div[2]/div[1]/div/ul/li/div/div[2]/p/span')
            time.sleep(2)
            
            # 在找到的链接元素上模拟点击鼠标左键
            ActionChains(self.driver).click(a).perform()
            time.sleep(10)
        
        print (">>>>Doneload weiyun file done")
        
            
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

