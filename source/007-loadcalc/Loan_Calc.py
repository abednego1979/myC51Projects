# -*- coding: utf-8 -*-

#Python 3.5.x

import os

def LoanCalc(curRate, remainLoan, Monthly, year, month, prePayMonth, prePayLoan):

    spendMonthes=0
    allInterest=0.0
        
    print ('year'+'\t'+'month'+'\t'+'interest'+'\t'+'principal'+'\t'+'remain Loan')
    while True:
        #计算year/month的所还利息
        interest=remainLoan*curRate/12      #所还利息
        principal_Monthly=Monthly-interest  #所还本金
        
        if month==prePayMonth:
            principal_Monthly+=prePayLoan
        
        remainLoan-=principal_Monthly
        
        #最后一个月的情况，不要得到负数
        if remainLoan<=0:
            principal_Monthly=remainLoan+principal_Monthly
            remainLoan=0
        
        print (str(year)+'\t'+str(month)+'\t'+str(interest)+'\t'+str(principal_Monthly)+'\t'+str(remainLoan))
        spendMonthes+=1
        allInterest+=interest
        
        if remainLoan<=0:
            return [year,month,spendMonthes,allInterest]
    
        month+=1
        if month>12:
            month=1
            year+=1
        

if False:
    curRate=float(raw_input(u'当前利率：'))
    remainLoan=float(raw_input(u'剩余贷款：'))
    Monthly=float(raw_input(u'基本月供：'))
    nextMonth=raw_input(u'下个还款月份(YYYYMM)：')
    year=int(nextMonth[0:4])
    month=int(nextMonth[4:]) 
else:
    curRate=0.04165
    remainLoan=2223519.44
    Monthly=12199.38
    year=2019
    month=3
        
print ('当前利率：', end="")
print (curRate)
print ('剩余贷款：', end="")
print (remainLoan)
print ('基本月供：', end="")
print (Monthly)

temp=[]

prePayMonth=int(input('每年的几月提前还款（1-12）：'))
prePayLoan=float(input('每次提前还款还多少钱：'))   

res_list=LoanCalc(curRate, remainLoan, Monthly, year, month, prePayMonth, prePayLoan)
print ('********************************')

print ("最后还款年月：%d%02d" % (res_list[0], res_list[1]))
print ("总还款月数：%d" % res_list[2])
print ("总支付利息：%f" % res_list[3])




