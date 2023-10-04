# 全量向es中导入flow_code表数据
import time
from elasticsearch import Elasticsearch
import sql_appbk

#pip install elasticsearch==7.9.0

# 向es插入一条数据,data格式为dict
# 使用时修改es地址，索引名
def insert_es(data):
    # es = Elasticsearch(["http://127.0.0.1:9200"])
    es = Elasticsearch(["http://8.218.127.18:9230"])
    res = es.index(index="flow_code", body=data, request_timeout=60)
    # print(res['result'])
    return res

# 读取MySQL数据，插入es。
# 使用时修改mysql表
def process():
    print("上传es")
    # 读取MySQL数据的数据表
    sql_com = 'select * from flow_code where is_process = 0 limit 10'
    result = sql_appbk.mysql_com(sql_com)
    if 0 == len(result):
        time.sleep(60*60)  # 1小时
        return 0

    for row in result:
        print("insert contract_name", row["contract_name"])
        # print("=========")
        # 把row插入es
        insert_es(row)
        # 标记位
        sql_update = 'update flow_code set is_process = 1 where id = {} '.format(row["id"])
        ret = sql_appbk.mysql_com(sql_update)
        # print(ret)
    return ret

if __name__ == '__main__':
    while 1:
        process()
        #time.sleep(60*60)
