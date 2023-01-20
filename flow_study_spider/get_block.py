import asyncio
import datetime
import time
from twisted.internet import task, reactor
import flow_py_sdk
from flow_py_sdk import flow_client
import re
import sql_appbk
#
# client = flow_client(host="access.mainnet.nodes.onflow.org", port=9000)

'''
功能：获得最新区块的高度,插入flow_block
输入：无
返回：height 高度 
'''
async def get_block_height():
    async with flow_client(
            host="access.mainnet.nodes.onflow.org", port=9000
    ) as client:
        latest_block = await client.get_latest_block()
        height = latest_block.height
        print(height)
        # block信息插入数据库
        parent_id_hex = latest_block.parent_id.hex()
        data = {
            "block_id" : latest_block.id.hex(),
            "signatures" : latest_block.signatures[0].hex(),
            "parent_id" : parent_id_hex,
            "height" : latest_block.height,
            "fetch_time" : time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()),
            "timestamp" : latest_block.timestamp,
        }
        # block_list.append(data)
        # sql_appbk.insert_update_data(data,"flow_block")
        ret = sql_appbk.insert_data(data,"flow_block")

        return height



def process_sub():
    height = asyncio.run(get_block_height())
    return height
"""
功能：每0.5秒执行一次，获得区块高度的函数
输入：无
返回：
"""
def  process():
    # while True:
    #     height = asyncio.run(get_block_height())
        # print(height)
        # time.sleep(0.5)
    l = task.LoopingCall(process_sub)
    l.start(0.5)  # call every STEP_S seconds
    reactor.run()


if __name__ == '__main__':
    process()



