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
import code_relation
import time


"""
功能；抽取flowcode代码的相关代码，插入数据库contract_related
输入：
返回：0成功，-1失败
"""
def update_relate_code():
    # step 1 从数据库flow_code获得一批需要处理的代码，标记为is_relate，
    sql = """
    select * from flow_code where  is_relate = 0 limit 100
    """
    result = sql_appbk.mysql_com(sql)   # 原始代码列表

    if 0==len(result):# 没有查询到结果返回
        return

    # step 2 处理flow_code每一段代码，抽取相关代码，

    for item in result: # 处理每一个原始的code数据，
        contract_id = item["id"]  # 代码id
        print(contract_id)
        contract_code = item["contract_code"]   #原始代码的contracct_code
        contract_name =  item["contract_name"]  # 原始代码的名称
        contract_address = item["contract_address"] # 原始代码地址

        relate_code_list = code_relation.get_code_related(contract_code)    #抽取相关代码


        data_list = []  # 一条代码的，需要插入数据库的orm数据列表
        for relate_code in relate_code_list:    # 处理每一行代码相关信息
            ralated_contract_name = relate_code["contract_name"]    # 相关代码名称
            related_contract_address = relate_code["contract_address"]# 相关代码地址
            # 构建orm数据
            data = {}
            data["contract_name"] = contract_name# 原始代码名称
            data["contract_address"] = contract_address# 原始代码地址
            data["related_contract_name"] = ralated_contract_name #相关代码名称
            data["related_contract_address"] = related_contract_address #相关代码地址
            data["fetch_time"] = time.strftime("%Y-%m-%d %H:%M:%S")#更新时间
            data_list.append(data)


        # step 3 一条代码的结果,统一插入数据库，contract_related
        ret = sql_appbk.insert_data_list(data_list,"contract_relation") #插入 一条代码的相关信息

        #step 4 更新flow_code中的处理标记位，
        sql_update = """
        update flow_code set is_relate = 1 where id = {}
        """.format(contract_id)
        ret_code = sql_appbk.mysql_com(sql_update)

    return 0



def proceess():
    while 1:
        update_relate_code()
        time.sleep(60*10)

        # 1
        # 2
# def cc():
#     sql = """
#     select * from flow_code where is_relate = 0 limit 1
#     """
#     result = sql_appbk.mysql_com(sql)
#
#     for item in result:
#         c_name = item["contract_name"]
#         c_address = item["contract_address"]
#         c_code  = item["contract_code"]
#         c_id  = item["id"]
#         code_relation_l = code_relation.get_code_related(c_code)
#         data_list  = []
#         for i in code_relation_l:
#             i_name = i["contract_name"]
#             i_ad = i["contract_address"]
#
#             contract_related = {}
#             contract_related["contract_name"] = c_name
#             contract_related["contract_address"] = c_address
#             contract_related["related_contract_name"] =  i_name
#             contract_related["related_contract_address"] = i_ad
#             contract_related["fetch_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
#             data_list.append(contract_related)
#         print(data_list)
#
#         sql_appbk.insert_data_list(data_list,"contract_relation")
#
#         update_sql = """
#         update flow_code set is_relate = 1 where id = {}
#         """.format(c_id)
#         sql_appbk.mysql_com(update_sql)
#     return 0

if __name__ == '__main__':
    update_relate_code()
    # cc()