#!/bin/sh
# Step 0:
# 获得最新的区块，是0.5s请求一次
nohup python3 get_block.py > get_block.log 2>&1 &

# Step 1:
#从插入数据库flow_block获得未处理的区块处理
nohup python3 update_trans_multi.py > update_trans_multi.log 2>&1 &

# Step 2:
#从交易表flow_trans_data中获得所有的合约地址，插入flow_contract_address合约地址表
nohup python3 update_contract.py > update_contract.log 2>&1 &

# Step 3:
#从flow_contract_address未处理的合约地址表
nohup python3 get_contract.py > get_contract.log 2>&1 &


# Step 4:
#根据代码判断标签contract_type
nohup python3 parse_flow_code.py > parse_flow_code.log 2>&1 &

# Step 5:
#更新es代码，从flow_code表中获取未处理的合约代码（is_process = 1），更新es中的数据（update_fcode_es.py）
nohup python3 update_fcode_es.py > update_fcode_es.log 2>&1 &