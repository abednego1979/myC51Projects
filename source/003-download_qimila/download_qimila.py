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

config_resMail=False

if config_resMail:
    import sendMail
import adapt_code


class BaseInfo():
    def __init__(self):
        self.baseUrls=[]
        self.db_dbName=''
        self.db_tbName=''
        self.db_titleName=[]
        
        self.browser='iexplorer'       #iexplorer/chrome/firefox
        self.browser_mode=""
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
            if BI.browser_mode=="headless":
                chrome_opt.add_argument("--headless")
            self.driver=webdriver.Chrome(executable_path='C:\\Program Files (x86)\\Google\\Chrome\\Application\\chromedriver.exe', options=chrome_opt)
        elif BI.browser=="iexplorer":
            ie_opt = webdriver.ie.options.Options()
            if BI.browser_mode=="headless":
                ie_opt.add_argument("--headless")
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
        global config_resMail
        
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
            res,Urls = adapt_code.soupParse(cur_url, soup, BI)
            
            #分离出微云的链接和主站链接
            newUrls=[item for item in Urls if not re.search(r'''share.weiyun.com''', item)]
            if newUrls:
                if False:
                    BI.baseUrls+=newUrls
                else:
                    BI.baseUrls+=newUrls[:2]
                
                continue
            
            temp_weiyun_links=[item for item in Urls if re.search(r'''share.weiyun.com''', item)]
            assert 1==len(temp_weiyun_links)
            
            row = res[0]+temp_weiyun_links
            rows=[iitt.replace("'", "") for iitt in row]

            #存入数据库
            db = sqlite3.connect(BI.db_dbName)        #连接数据库
            db_cu = db.cursor()                     #游标        
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
        print (">>>>Save file to my weiyun:")
        
        #从数据库中取出file_name列为空的数据，这代表文件还没有转存到我的微云
        db = sqlite3.connect(BI.db_dbName)
        import pandas.io.sql as sql
        import numpy as np
        weiyun_links=sql.read_sql_query('SELECT * FROM '+BI.db_tbName, db)
        weiyun_links=np.array(weiyun_links)
        weiyun_links=weiyun_links.tolist()
        
        for wei_link in weiyun_links:
            print ("<>URL: %s" % wei_link[4])
            print ("<>FileName: %s" % wei_link[1])
            self.driver.get(wei_link[4])
            time.sleep(3)
            
            #在打开的界面中，检查是否需要登录
            login_button=self.driver.find_element_by_class_name("layout-header").find_element_by_class_name("name")
            if login_button.text=="登录":
                login_button.click()
                time.sleep(1)
            
                #这时弹出了iframe，所以要切换到新的iframe
                self.driver.switch_to.frame(self.driver.find_elements_by_tag_name("iframe")[0])
            
                #默认是qq 二维码登录，找到账户密码登录的链接
                self.driver.find_element_by_id("switcher_plogin").click()
                
                #找到输入账户的位置，先清除内容，再输入用户名
                uin_del = self.driver.find_element_by_id("loginform").find_element_by_id("uin_del")
                if uin_del.is_displayed():#判断元素可见
                    uin_del.click()
                self.driver.find_element_by_id("loginform").find_element_by_id("u").send_keys("108253836")
                self.driver.find_element_by_id("loginform").find_element_by_id("p").send_keys("12@Achlbs")
                self.driver.find_element_by_id("loginform").find_element_by_id("login_button").click()
                
                #回到原frame
                self.driver.switch_to.default_content()

                #关闭弹出框。由于关闭按钮是利用CSS做出来的，不是输入类的元素，所以这里需要用JS执行的方式来关闭
                self.driver.execute_script("arguments[0].click();", self.driver.find_element_by_class_name("close-btn").find_element_by_tag_name("i"))

                
                
            time.sleep(1)
            
            #这时已经登录了微云
            #先找到视频的选择按钮
            self.driver.execute_script("arguments[0].click();", self.driver.find_element_by_class_name("list-group-hd").find_element_by_tag_name("i"))
            
            #得到文件名
            saveFileName=self.driver.find_element_by_class_name("list-group-bd").find_element_by_class_name("figure-list-item-txt").find_element_by_tag_name("span").text
            
            
            #找到"保存微云"按钮，并点击
            self.driver.execute_script("arguments[0].click();", self.driver.find_element_by_class_name("layout-body").find_element_by_class_name("action-item").find_element_by_tag_name("i"))
            
            #保存的时候会弹框确认存储位置，确认到默认路径既可
            temp_buttons=self.driver.find_element_by_class_name("modal-show").find_elements_by_tag_name("button")
            for temp_button in temp_buttons:
                if temp_buttons.text=="确定":
                    temp_buttons.click()
                    pass
                pass
            print ("Save %s to weiyun OK" % saveFileName)
            time.sleep(1)
            
            #将saveFileName信息放入数据库中
            
        
        print (">>>>Save file to my weiyun done")
        
        
        if config_resMail:
            '''
            mailinfo=json.loads(sendMail.decryptInfo(sendMail.mail_info_cipherText, key=""))     
            sendMail.MySendMail(server_host=mailinfo['mail_host'], \
                                server_port=mailinfo['mail_port'], \
                                user=['mail_user'], \
                                password=['mail_pass'], \
                                sender=['sender'], \
                                receivers=['receivers']).sendRes_ByMail(plain_msg="lines", plain_msg=[])
            '''
            pass


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

