import json
import re
from flow_study_spider import sql_appbk
import requests




#
def parse_declaration_end_pos(declaration_node):
    if "EndPos" in declaration_node:
        end_pos = declaration_node["EndPos"]['Line']
    return end_pos

def parse_declaration_start_pos(declaration_node):
    if "StartPos" in declaration_node:
        start_pos = declaration_node["StartPos"]['Line']
    return start_pos


"""
功能：通过代码原结构，解析Identifier/Identifiers，获得代码块的名称，struct_name
输入：declaration_node Declarations其中的一个node
返回：struct_name,list 
"""
def parse_declaration_struct_name(declaration_node):
    struct_name = ""
    if "Identifier" in declaration_node:
        struct_name = declaration_node["Identifier"]["Identifier"]
    elif "Identifiers" in declaration_node and declaration_node["Identifiers"]!=None:
        struct_name = declaration_node["Identifiers"][0]["Identifier"]
    else:
        struct_name = "other"
    return struct_name

"""
功能：通过代码原结构，解析Declarations节点，获得代码块的类型，struct_type
输入：declaration_node Declarations其中的一个node
返回：struct_type,字符串类型，可能是，resource, fun, event，空字符串（表示没有match规则的类型）
"""
def parse_declaration_struct_type(declaration_node):
    # step1 1，如果包含CompositeKind 字段，值为CompositeKindResource 则
    # struct_type为resource。值为CompositeKindEvent 则struct_type为event。

    # 2，如果包含 type 字段，且 type字段的值为FunctionDeclaration
    # 则struct_type为函数fun。

    struct_type = ""
    if "CompositeKind" in declaration_node:
        if "CompositeKindResource" == declaration_node["CompositeKind"]:
            struct_type = "resource"
        if "CompositeKindEvent" == declaration_node["CompositeKind"] :
            struct_type = "event"
    if "type" in declaration_node:
        if "FunctionDeclaration" == declaration_node["type"]:
            struct_type = "fun"
    else:
        struct_type  = "other"
    return struct_type


"""
功能:解析代码，获得所有的代码段 代码类型 struct_type
输入:代码
返回:
"""
def parse_code(code_text):
    ret_list =[]

    # 遍历code的declaration节点，逐个进行处理
    for declaration_node in code_text["program"]["Declarations"]:
        struct_type =  parse_declaration_struct_type(declaration_node)
        struct_name = parse_declaration_struct_name(declaration_node)
        start_pos = parse_declaration_start_pos(declaration_node)
        end_pos = parse_declaration_end_pos(declaration_node)
        result_dic = {}
        result_dic["struct_type"] = struct_type
        result_dic["struct_name"] = struct_name
        result_dic["start_pos"] = start_pos
        result_dic["end_pos"] = end_pos
        ret_list.append(result_dic)

        # print("stttyp"+struct_type)
        # 判断两级declaration_node
        if "Members" in declaration_node:
            declaration_node2 = declaration_node["Members"]["Declarations"]
            for declaration_node2_sub in declaration_node2:
                struct_type = parse_declaration_struct_type(declaration_node2_sub)
                struct_name = parse_declaration_struct_name(declaration_node2_sub)
                start_pos = parse_declaration_start_pos(declaration_node2_sub)
                end_pos = parse_declaration_end_pos(declaration_node2_sub)
                result_dic = {}
                result_dic["struct_type"] = struct_type
                result_dic["struct_name"] = struct_name
                result_dic["start_pos"] = start_pos
                result_dic["end_pos"] = end_pos
                ret_list.append(result_dic)
    return ret_list

"""
功能：通过contract_code 代码 调用go服务，获取包含代码结构的code_text,
"""
def get_code_text(contract_code):
    # url =  "http://127.0.0.1:8080/parse"
    url =  "http://8.218.127.18:8080/parse"
    ret = requests.post(url,data=contract_code.encode('utf-8'))
    ret_text = ret.text
    if ret_text is None or ret_text == '':
        return "null"
    code_text = json.loads(ret_text)
    return code_text

"""
功能： 更新数据库
输入： 
返回： 
"""
def code_et():
    sql = """
    SELECT id,contract_address,contract_name,contract_code FROM `flow_code` WHERE contract_type = "contract" and is_structed=0 
    """
    flow_code  = sql_appbk.mysql_com(sql)

    for item in flow_code:
        print(item['contract_code'])
        print(item["id"])
        print("next contract_code ......printing...... ")
        contract_code_single = item['contract_code']

    # step1，E extract，所有东西都是etl，获得原始解析数据，从GO的服务中获取
        code_text  = get_code_text(contract_code_single)
        print("codetext")
        print(code_text)
        if code_text!="null":
        # step2 T transform 解析原始数据代码，获得需要的数据结构信息
            result_list  = parse_code(code_text)
            for ret_dic in result_list:
                sql_insert = """
                INSERT INTO flow_code_struct (contract_address,contract_name,struct_type,struct_name,start_pos,end_pos) VALUES("{}","{}","{}","{}",{},{})
                """.format(item['contract_address'],item['contract_name'],ret_dic['struct_type'],ret_dic['struct_name'],ret_dic['start_pos'],ret_dic['end_pos'])
                insert_struct = sql_appbk.mysql_com(sql_insert)
            sql_update = """
            update  `flow_code` set is_structed=1 where id = {}
            """.format(item["id"])
            sql_appbk.mysql_com(sql_update)
        else:
            # 解析后的code_text，有值为空的情况
            print("code_text is null")
    return 1


"""
功能:解析代码，获得所有的代码段 代码类型 struct_type
输入:代码
返回:
"""

if __name__ == '__main__':
    declaration_node_text = """ 
    import FanTopToken from 0x86185fba578bc773 
      
pub contract HelloWorld {

    // Declare a public field of type String.
    //
    // All fields must be initialized in the init() function.
    pub let greeting: String

    // The init() function is required if the contract contains any fields.
    init() {
        self.greeting = "Hello, World!"
    }

    // Public function that returns our friendly greeting!
    pub fun hello(): String {
        return self.greeting
    }
}
    """
    result  = get_code_text(declaration_node_text)
    print(result)