#!/usr/bin/env python3
#coding=utf-8
#########################################################################
# Author: @appbk.com
# Created Time: Sun 01 Mar 2020 09:08:42 PM CST
# File Name: index.py
# Description:
######################################################################
import re
import json
import sql_appbk


"""
功能；通过go服务解析代码，得到代码结构，获取代码相关合约,抽取import 并存入数据库。
输入：contract_code,合约代码。
输入：contract_address,合约地址。
返回：list 格式如下 [{"contract_name":"name1","contract_address":"address1"},
                    {"contract_name":"name2","contract_address":"address2"}]。
"""
def get_code_related(contract_code):
    relate_contract_list = []
    #step 1 ，获得所有的import行
    #step 1,获得所有引用
    p = re.compile('import.{3,30}from 0x\w{10,25}') #引用的正则
    import_list = p.findall(contract_code)

    # step 2 ,解析每一行，获得相关的合约地址和合约名称


    for item in import_list:
        item_list = item.split()
        contract_name = item_list[1]
        contract_address = item_list[3]
        #print(contract_name, contract_address)
        import_data = {
            "contract_name":contract_name,
            "contract_address":contract_address,
        }
        relate_contract_list.append(import_data)

    return relate_contract_list


"""
功能；获取代码相关合约transaction，存入数据库flow_code_relate_transaction表
输入： 
输入： 
返回：
"""
def get_code_relate_transaction():
    # jia 状态为
    sql ="""
    select * from flow_code where is_trans = 0 
    """
#     sql ="""
# select * from flow_code where is_trans = 0 and  contract_address = '0x097bafa4e0b48eef'
# """

    reslut = sql_appbk.mysql_com(sql)  #待处理 contract_code
    for item in reslut:     # 需要处理目标合约代码，合约地址
        c_name = item["contract_name"]
        c_address = item["contract_address"]

        sql_re_transaction = """
        select * from contract_relation where related_contract_address = '{}' and  related_contract_name = '{}'  
        """.format(c_address,c_name)
        result_data = sql_appbk.mysql_com(sql_re_transaction)
        data_list = []
        for result_item in result_data:
            # 相关合约
            data_dict = {}
            relate_transaction_name = result_item["contract_name"]      #  相关合约的合约名
            relate_transaction_address = result_item["contract_address"]   # 相关合约的合约地址
            data_dict["relate_transaction_name"] = relate_transaction_name
            data_dict["relate_transaction_address"] = relate_transaction_address
            data_dict["contract_name"] = c_name
            data_dict["contract_address"] = c_address
            # 判断相关合约，属于trans类型（flow_code表 contract_type字段，值为transaction） 则插入表flow_code_relate_transaction、

            sql_istrans = """
            select contract_type from flow_code where contract_address = '{}' and contract_name = '{}'
            """.format(relate_transaction_address,relate_transaction_name)
            istrans = sql_appbk.mysql_com(sql_istrans)
            if istrans and "transaction"== istrans[0]["contract_type"]:
                data_list.append(data_dict)

        if None != data_list:
            sql_appbk.insert_data_list(data_list,"flow_code_relate_transaction")

        sql_update = """
        update flow_code set is_trans =1 where contract_address = '{}' and contract_name = '{}'
        """.format(c_address,c_name)
        sql_appbk.mysql_com(sql_update)

    return 0




if __name__ == '__main__':
#     contract_code = """
#     import NonFungibleToken from 0x1d7e57aa55817448
#     import MetadataViews from 0x1d7e57aa55817448
#
#
# pub contract HelloWorld {
#     //import LicensedNFT from 0x01ab36aaf654a13e
#     // Declare a public field of type String.
#     //
#     // All fields must be initialized in the init() function.
#     pub let greeting: String
#
#     // The init() function is required if the contract contains any fields.
#     init() {
#         self.greeting = "Hello, World!"
#     }
#
#     // Public function that returns our friendly greeting!
#     pub fun hello(): String {
#         return self.greeting
#     }
# }
#     """
#     result = get_code_related(contract_code)
#     print(result)
    get_code_relate_transaction()

