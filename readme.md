flow爬虫代码部分

# pre intall

pip install flow-py-sdk

need  Python 3.9 or higher

# Step 0:
获得最新的区块，是0.5s请求一次，不是callback，插入数据库flow_block，通过把height当做唯一key+insert ignore做去重（ get_block.py  ）
flow区块链：https://www.flowdiver.io/

# Step 1:
从插入数据库flow_block获得未处理的区块（标记位：is_updated，0未处理，1已处理），从区块中获得交易，插入数据库flow_trans_data，（ update_trans.py,或者多线程版本update_trans_mulit.py  ）

数据回溯：爬虫获得所有高度区间内的交易，插入数据库flow_trans_data，（ get_trans.py  ）

存在可能的问题，就是区块可能在存档服务器中，不在最新的，需要专门处理下。


# Step 2:
从交易表flow_trans_data中获得所有的合约地址，插入flow_contract_address合约地址表（update_contract.py）
是通过sql查flow_trans_data中最近1小时的数据，然后insert ignore插入flow_contract_address表


# Step 3:
从flow_contract_address未处理的合约地址表，标记位（is_process），根据合约地址获取代码code，插入flow_code表。（get_contract.py）

# Step 4:
postprocess，后处理
获得代码的类型，给flow_code添加contract_category分类字段
标记为就是contract_category字段本身

# Step 5:
更新es代码，从flow_code表中获取未处理的合约代码（is_process = 1），更新es中的数据（update_fcode_es.py）

