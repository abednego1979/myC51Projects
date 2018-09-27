# -*- coding: utf-8 -*-

#Python 3.5.x

#V0.01

#read readme.txt to get help
#SQLite
#+----------+----------+----------+
#|   MD5    |   Len    |   Path   |
#+----------+----------+----------+

import os
import sys

import re
import copy
import sqlite3
import hashlib

DB_NAME="MD5_Len_Path"

class MyDB_Sqlite():
    def __init__(self, dbName):
        self.db_conn=None
        self.db_curs=None
        self.db_name=dbName
        self.tb_name=dbName
        return
    
    def Connect(self):
        #如果数据库不存在，就先创建数据库和表
        if not os.path.isfile(self.db_name+".sqlite"):
            self.db_conn=sqlite3.connect(self.db_name+'.sqlite')
            self.db_curs=self.db_conn.cursor()
            #指定数据库内部是utf-8编码的
            self.db_conn.text_factory=str
            
            self.__CreateTable__({'column': ['md5', 'len', 'path'], 'dataType': ['CHAR(32)', 'UNSIGNED INT', 'TEXT']})
            self.db_conn.commit()
            self.db_curs.close()
            self.db_conn.close()
            self.db_curs=None
            self.db_conn=None
            pass
        
        self.db_conn=sqlite3.connect(self.db_name+'.sqlite')
        self.db_curs=self.db_conn.cursor()
        #指定数据库内部是utf-8编码的
        self.db_conn.text_factory=str
        pass
    
    def __CreateTable__(self, tableConstruct):
        # create tables
        execString="create table "+self.tb_name+" ("
        
        for index,title_type in enumerate(zip(tableConstruct['column'], tableConstruct['dataType'])):
            execString+=title_type[0]+' '+title_type[1]
            execString+=','
        execString=execString.rstrip(',')
        execString+=')'
        try:
            self.db_curs.execute(execString)
        except Exception as err:
            print(('The table '+self.tb_name+' exists!'))
            print (err)
            print(traceback.format_exc())
        return
    
    def Commit(self):
        self.db_conn.commit()
        
    def Close(self):
        self.db_curs.close()
        self.db_conn.close()
        self.db_curs=None
        self.db_conn=None
    
    def Drop(self):
        #删除相应的数据库文件即可
        try:
            os.remove(self.db_name+'.sqlite')
        except:
            pass            
        return    
    
    def SqlCmd_SELECT(self, sql_select, sql_where, *para):
        if len(sql_where):
            str_select='SELECT '+sql_select+' FROM '+self.tb_name+' WHERE '+sql_where
        else:
            str_select='SELECT '+sql_select+' FROM '+self.tb_name
            
        for i in range(len(para)):
            s=re.search(r"(?<=')"+'##'+str(i)+r"(?=')", str_select)
            str_select=str_select.replace('##'+str(i), str(para[i]))
        return str_select    
    
    def SqlCmd_INSERT(self, titleNameList, data):
        insert='INSERT INTO '+self.tb_name+' ('+','.join(titleNameList)+') VALUES ('
        for value in data:
            para1=value
            if type(para1)==str:
                para1='"'+para1+'"'
            insert+=str(para1)+','
        insert=insert.rstrip(',')
        insert+=')'

        return insert
    
    def Query(self, query):
        #执行查询操作
        self.db_curs.execute(query)

        #取出列名称
        names=[f[0] for f in self.db_curs.description]
        
        l_temp=[]
        for row in self.db_curs.fetchall():
            l_temp.append(list(copy.deepcopy(row)))
        return l_temp
    
    def Insert(self, insert):
        try:
            #执行插入操作        
            self.db_curs.execute(insert)
        except Exception as err:
            print ('Insert Fail: ')
            print((str(insert, 'utf-8')))
            print (err)
            print(traceback.format_exc())
            return -1
        return 0   

##MD5####################################################
def hash_bytestr_iter(bytesiter, hasher, ashexstr=False):
    for block in bytesiter:
        hasher.update(block)
    return (hasher.hexdigest() if ashexstr else hasher.digest())

def file_as_blockiter(filename, blocksize=65536):
    with filename:
        block = filename.read(blocksize)
        while len(block) > 0:
            yield block
            block = filename.read(blocksize)

def md5(filename):
    md5 = hash_bytestr_iter(file_as_blockiter(open(filename, 'rb')), hashlib.md5(), True)
    return md5,os.path.getsize(filename),filename
######################################################


def main():
    global DB_NAME
    
    files2Del=[]
    
    #连接数据库
    db=MyDB_Sqlite(DB_NAME)
    db.Drop()
    db.Connect()
    
            
    root="."
    for dirpath, dirnames, filenames in os.walk(root):
        for filepath in filenames:
            tempFileName=os.path.join(dirpath, filepath)
            
            #有些文件可能不需要参与hash去重复的过程，所以这里有机会写代码continue
            if tempFileName.endswith(".py") or tempFileName.endswith(".pyc"):
                continue
            if tempFileName.endswith(".sqlite"):
                continue
            if os.path.getsize(tempFileName)==0:
                continue

            #求md5值
            md5_len_path=md5(tempFileName)
            print (md5_len_path)
            
            #检查这个文件的md5值是否已经在数据库中存在
            sel=db.SqlCmd_SELECT("len,path", 'md5="%s"' % md5_len_path[0])
            res=db.Query(sel)
            if len(res)==0:
                #如果这个文件不与数据库中的已有文件的md5冲突，认为是一个不重复的文件，把这个文件的数据写入数据库
                ins=db.SqlCmd_INSERT(['md5', 'len', 'path'], list(md5_len_path))
                try:
                    print (ins)
                except:
                    print (md5_len_path)
                    input("Insirt STRING ERROR")
                    pass
                res=db.Insert(ins)
                db.Commit()
            else:
                #发现冲突
                if res[0][1] != tempFileName:
                    #应该删除这个文件
                    print (res[0][1]+"<<<<>>>>"+tempFileName)
                    #print ("Delete: "+tempFileName)
                    files2Del.append(tempFileName)
            pass
        pass
    db.Close()
    
    print (">>>>>>>>>>>>>>>>>>>>>>>>")
    print ("Files should be deleted:")
    for item in files2Del:
        print (item)

if __name__ == "__main__":
    print ("Start ...")
    main()
    print ("End ...")