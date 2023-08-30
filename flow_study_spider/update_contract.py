import time
from twisted.internet import task, reactor
import sql_appbk
"""
功能：每小时运行1次，flow_trans_data表中的contract_address去重，插入flow_contract_address表
输入：无。
返回：
"""

def update_contract():
    print("处理合约地址更新",time.strftime("%Y-%m-%d %H:%M:%S"))
    #  flow_trans_data表中，每小时获取一次合约地址，插入到flow_contract_address
    sql = """
    INSERT ignore into flow_contract_address  (contract_address) 
    SELECT distinct(contract_address)  as dis_contract_adress FROM flow_trans_data 
    WHERE fetch_time > DATE_SUB(now(),INTERVAL 1 HOUR)
    """
    ret = sql_appbk.mysql_com(sql)
    return 0

"""
功能：每小时运行1次，获得区块高度的函数
输入：无
返回：
"""
def  process():
    l = task.LoopingCall(update_contract)
    l.start(60*60)  # 每小时运行1次
    reactor.run()

if __name__ == '__main__':
    process()