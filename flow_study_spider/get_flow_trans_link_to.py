import asyncio
import json
import time
import flow_py_sdk
from flow_py_sdk import flow_client
from flow_py_sdk.cadence import Address
import sql_appbk
# pip3 install  flow-py-sdk
# need py 3.9
# 获得flow转账的events记录

async def get_event_list(start_height, end_height):
    async with flow_client(
            #host="access-001.mainnet14.nodes.onflow.org", port=9000,
            host="access.mainnet.nodes.onflow.org", port=9000
    ) as client:
        #必须知道所有的合约，和event的名称
        #type: A.{contract address}.{contract name}.{event name}
        events = await client.get_events_for_height_range(
            type="A.1654653399040a61.FlowToken.TokensDeposited",
            #type="flow.AccountCreated", #账号创建 event
            #type="flow.AccountContractAdded", #合约创建event
            start_height=start_height,
            end_height=end_height,
        )
        #print("event num: {}".format(events))
        transfer_data_list = []
        for item in events:
            for sub_item in item.events:
                #print(sub_item.payload.decode())
                event_data = json.loads(sub_item.payload.decode())
                trans_id = sub_item.transaction_id.hex()
                try:
                    if "Event" == event_data["type"]:
                        to_address = event_data["value"]["fields"][1]["value"]["value"]["value"]
                        amount = event_data["value"]["fields"][0]["value"]["value"]
                        #print(from_address,amount,trans_id)
                        if  "0xf919ee77447b7497" != to_address: #系统的不要
                            transfer = {
                                "to_address":to_address,
                                "amount": amount,
                                "trans_id": trans_id,
                            }
                            transfer_data_list.append(transfer)
                except Exception as e:
                    print("ERROR", e)
                    continue

        #load
        sql_appbk.insert_data_list(transfer_data_list, "flow_token_to")

def get_all():
    for height in range(31893338, 31293338,  -250):
        start_height = height - 250 + 1
        end_height = height
        print(start_height, end_height)
        #time.sleep(1)
        asyncio.run(get_event_list(start_height, end_height))

if __name__ == "__main__":
    get_all()
