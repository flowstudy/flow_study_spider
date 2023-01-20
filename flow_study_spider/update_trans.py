import asyncio
import get_trans
import time
import sys
import sql_appbk

"""
功能：从 flow_block读取未处理的区块，获得区块内的交易信息，主要是合约代码和名称，插入flow_trans_data
输入：无
输出：无
"""
def update_trans_data():
    #step1 从 flow_block读取1个，未处理的区块，is_update =0
    sql_get_block = """
    select * from flow_block where is_updated = 0 limit 1 
    """
    result = sql_appbk.mysql_com(sql_get_block)

    # 如果没有结果，表示没有数据需要处理，则sleep30秒，
    if 0==len(result):
        time.sleep(30)
        return 0

    height = result[0]["height"]
    print("height ", height)


    #step2 获得区块内的交易信息，主要是合约代码和名称，插入flow_trans_data,
    # 调用函数为 get_trans.get_trans(height)
    ret = asyncio.run(get_trans.get_trans(height))

    # step3 更新该区块的状态 is_update =1
    sql_update_state = """
    UPDATE flow_block SET is_updated =1 WHERE height = {}
    """.format(height)
    sql_appbk.mysql_com(sql_update_state)

    return 0

if __name__ == '__main__':
    while 1:
        update_trans_data()