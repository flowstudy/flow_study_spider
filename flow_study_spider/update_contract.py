import asyncio
import time

import flow_py_sdk
from flow_py_sdk import flow_client
from flow_py_sdk.cadence import Address
import re
import sql_appbk
from twisted.internet import task, reactor

def update_contract():
    print("处理合约地址更新",time.strftime("%Y-%m-%d %H:%M:%S"))
    #  flow_trans_data表中，每小时获取一次合约地址，插入到flow_contract_address
    sql = """
    INSERT ignore into flow_contract_address  (contract_address) 
    SELECT distinct(contract_address)  as dis_contract_adress  FROM flow_trans_data 
    WHERE fetch_time > DATE_SUB(now(),INTERVAL 1 HOUR) 
    """
    ret = sql_appbk.mysql_com(sql)
    return 0

"""
功能：每 秒执行一次，获得区块高度的函数
输入：无
返回：
"""
def  process():
    l = task.LoopingCall(update_contract)
    l.start(60*60)  # 每小时运行1次
    reactor.run()

if __name__ == '__main__':
    process()