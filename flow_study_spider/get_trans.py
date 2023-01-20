import asyncio
import datetime
import time

import flow_py_sdk
from flow_py_sdk import flow_client
import re
import sql_appbk
from concurrent.futures import ThreadPoolExecutor



# pip3 install  flow-py-sdk
# need py 3.9
# 异步

"""
功能：解析trans脚本，获得引用的合约地址
输入：script，trans脚本
返回：合约地址
"""
def get_contract_address(trans_script):
    #step 1,获得所有引用
    p = re.compile('import.{3,30}from 0x\w{10,25}') #引用的正则
    import_list = p.findall(trans_script)

    #step 2，解析所有引用
    import_data_list = []
    for item in import_list:
        item_list = item.split()
        contract_name = item_list[1]
        contract_address = item_list[3]
        #print(contract_name, contract_address)
        import_data = {
            "contract_name":contract_name,
            "contract_address":contract_address,
        }
        import_data_list.append(import_data)
    return import_data_list


'''
功能：获得交易，解析交易中的调用合约。
输入：height区块高度。
返回：0成功 其他失败。

 插入数据库flow_trans_data
'''
async def get_trans(height):
    async with flow_client(
            host="access.mainnet.nodes.onflow.org", port=9000
    ) as client:
        # latest_block = await client.get_latest_block()
        # 通过height获取区块信息。
        block = await client.get_block_by_height(height=height)
        #collection是transaction的集合
        trans_list = []
        # 获得区块中的collection列表
        for i in range(len(block.collection_guarantees)):
            collection_id = block.collection_guarantees[i].collection_id  # 获得第i个 collection id
            collection = await client.get_collection_by_i_d(id=collection_id)  # 获得 collection 详情
            for trans_id in collection.transaction_ids: # 获得 collection 中所有transaction 列表，并遍历
                trans_id_hex = trans_id.hex() # 获得交易id，16进制形式
                transaction = await client.get_transaction(id=trans_id) # 根据交易id 获得交易详情

                user_address= transaction.proposal_key.address.hex() # 获得交易中的用户地址
                trans_script = transaction.script.decode("utf-8") # 获得交易的脚本代码
                #print(trans_script)
                import_data_list = get_contract_address(trans_script) # 从交易代码中解析合约地址
                # 遍历合约地址，构造需要插入数据库的数据
                for import_data in import_data_list:
                    trans_data = {
                        "trans_id":trans_id_hex,
                        "user_address":"0x" + user_address,
                        "contract_name":import_data["contract_name"],
                        "contract_address":import_data["contract_address"],
                        "fetch_time":time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                        "height":height,
                    } #注意使用的时候，基础的nft等类，可以不用
                    #print(trans_data)
                    trans_list.append(trans_data)
        try:
            sql_appbk.insert_data_list(trans_list, "flow_trans_data")
            return 0
        except Exception as e:
            print("ERROR", e)

        return -1



def thread_run(height):
    asyncio.run(get_trans(height))
    #time.sleep(5)

# 多线程跑历史数据
def get_all():
    concurrency_num = 30  #线程数
    executor = ThreadPoolExecutor(max_workers=concurrency_num)
    for height in range(38395746, 37795746, -1*concurrency_num):
    # for height in range(31893338, 31293338, -1*concurrency_num):
        print(height, "time", time.time())

        future_list = []  # 多线程列表
        for i in range(0, concurrency_num):
            thread_height = height - i
            print("thread_height", thread_height)
            future = executor.submit(thread_run, thread_height)
            future_list.append(future)

        #等待完成
        for future in future_list:
            ret = future.result()  # 等待

if __name__ == "__main__":
    asyncio.run(get_trans())
    get_all()
