import sql_appbk
sql = "select * from flow_code"
result = sql_appbk.mysql_com(sql)

for item in result:
    contract_address = item["contract_address"]
    contract_name = item["contract_name"]
    filename = contract_address + "_" + contract_name
    contract_code = item["contract_code"]

    #写入文件
    codefile = open("code/" + filename, "w")
    codefile.write(contract_code)
    codefile.close()

