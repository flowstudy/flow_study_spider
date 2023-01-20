import json
import re
from flow_study_spider import sql_appbk






"""
功能；根据代码判断标签contract_type
输入：contract_code 
返回：标签 contract_type (interface,contract,transaction)
"""
def get_code_type(contract_code):
    p = re.compile('pub contract.*|access\(all\) contract.*')  # 引用的正则
    i = re.compile('pub contract interface.*')
    if i.findall(contract_code):
        contract_type = "interface"
    elif p.findall(contract_code):  # 包含回车
        contract_type = "contract"
    else:
        contract_type = "transaction"
    return contract_type



"""
功能；根据代码判断标签
输入：contract_code
返回：标签 contract_category(nft,token,other)
"""
def get_code_category():
    sql = """
    select contract_name,id from flow_code where contract_type = "contract" and contract_category is null 
    """
    ret = sql_appbk.mysql_com(sql)
    # print(contract_name)
    for item in ret:
        contract_name = item["contract_name"]
        id = item["id"]
        tgt_nft = "nft"
        tgt_token = "token"
        name_formate = contract_name.lower()
        code_category = ""
        if name_formate.find(tgt_nft):
            code_category = "nft"
        elif name_formate.find(tgt_token):
            code_category = "token"
        else:
            code_category = "other"
        sql_update = """
        update flow_code set contract_category = '{}' where id={}
        """.format(code_category,id)
        result = sql_appbk.mysql_com(sql_update)


"""
功能；读取sql中 contract_code，调用方法，打标签
输入： 
输出： 
"""
def process():
    sql_select = "select * from flow_code where contract_type is null "
    # sql_select = "select * from flow_code where id =2"
    ret = sql_appbk.mysql_com(sql_select)
    for item in ret:
        id = item["id"]
        code = item["contract_code"]
        contract_type = get_code_type(code)
        sql = """
        UPDATE flow_code SET contract_type = '{}' where id = {}
        """.format(contract_type,id)
        result = sql_appbk.mysql_com(sql)


if __name__ == '__main__':
    contract_code = """
// Version         : 0.0.8

// Blockchain      : Flow www.onFlow.org

import NonFungibleToken from 0x1d7e57aa55817448

import MetadataViews from 0x1d7e57aa55817448

import FungibleToken from 0xf233dcee88fe0abe

pub contract DisruptArt: NonFungibleToken {
    """
    # process()

    # cate_type= get_code_type(contract_code)
    # print(cate_type)
    # get_code_category()
    # get_code_related(contract_code)