import asyncio
import get_trans
import time
import sys
import sql_appbk
from concurrent.futures import ThreadPoolExecutor
"""
功能：获得一个高度的区块中的trans信息，插入数据库flow_trans_data,并更新flow_block状态，
输入：height，区块高度
返回：0
"""
def update_trans_by_height(height):
    print("height: ", height)
    #step2 获得区块内的交易信息，主要是合约代码和名称，插入flow_trans_data,
    # 调用函数为 get_trans.get_trans(height)
    ret = asyncio.run(get_trans.get_trans(height))

    # step3 更新该区块的状态 is_update =1
    sql_update_state = """
    UPDATE flow_block SET is_updated =1 WHERE height = {}
    """.format(height)
    sql_appbk.mysql_com(sql_update_state)

    return 0


"""
功能：从flow_block读取未处理的区块，获得区块内的交易信息，主要是合约代码和名称，插入flow_trans_data
输入：无
输出：无
"""
def update_trans_data():
    #step1 从 flow_block读取1个，未处理的区块，is_update =0
    concurrency_num = 10  # 线程数
    executor = ThreadPoolExecutor(max_workers=concurrency_num)

    sql_get_block = """
    select * from flow_block where is_updated = 0 limit {}
    """.format(concurrency_num)
    result = sql_appbk.mysql_com(sql_get_block)

    # 如果没有结果，表示没有数据需要处理，则sleep30秒，
    if 0==len(result):
        time.sleep(30)
        return 0
    # 获得height列表
    height_list = []
    for item in result:
        height = item["height"]
        height_list.append(height)

    print(height_list)
    # 多线程处理height list中的数据
    future_list = []  # 多线程列表
    for height in height_list:
        thread_height = height # 线程需要处理的区块高度
        # print("thread_height", thread_height)
        future = executor.submit(update_trans_by_height, thread_height)  # 处理thread height高度的区块
        future_list.append(future)

    # 等待完成
    for future in future_list:
        ret = future.result()  # 等待

    return 0



if __name__ == '__main__':
    while 1:
        update_trans_data()
    # update_trans_data()