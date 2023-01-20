import sql_appbk
import re
#更新合约类型，interface， NFT， TOKEN

def get_code_type(code):
    # step 1,获得定义
    # step 1,获得所有引用
    p = re.compile('pub contract.*|access\(all\) contract.*')  # 引用的正则
    import_list = p.findall(code)  # 包含回车
    #print(import_list)
    # 'pub contract RaribleFee {'
    # 'pub contract RaribleNFT : NonFungibleToken, LicensedNFT {'
    # 'pub contract interface LicensedNFT {'
    # pub contract ExampleNFT: NonFungibleToken
    # pub contract Seussibles:然后是换行

    contract_name_line = import_list[0]

    contract_type = "App"
    if -1 != contract_name_line.find("interface"):
        contract_type = "interface"
        return contract_type

    if -1 != contract_name_line.find("NonFungibleToken"):
        contract_type = "NFT"
        return contract_type

    if -1 != contract_name_line.find("FungibleToken"):
        contract_type = "Token"
        return contract_type

    return contract_type


sql = "select * from flow_code"
result = sql_appbk.mysql_com(sql)

contract_type_dict = {} #key:type, value:freq
for item in result:
    id = item["id"]
    contract_code = item["contract_code"]

    #判断类型
    contract_type = get_code_type(contract_code)
    contract_type_dict.setdefault(contract_type, 0)
    contract_type_dict[contract_type] = contract_type_dict[contract_type] + 1

    print(contract_type)

print(contract_type_dict)
