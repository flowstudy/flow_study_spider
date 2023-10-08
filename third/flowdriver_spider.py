import time

import requests
import sql_appbk

def get_contract(page=1):
    offset = (page-1) * 25 #page从1开始
    headers = {
        'authority': 'api.findlabs.io',
        'accept': 'application/graphql-response+json, application/graphql+json, application/json, text/event-stream, multipart/mixed',
        'accept-language': 'zh-CN,zh;q=0.9',
        'authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwczovL2hhc3VyYS5pby9qd3QvY2xhaW1zIjp7IngtaGFzdXJhLWFsbG93ZWQtcm9sZXMiOlsidXNlciJdLCJ4LWhhc3VyYS1kZWZhdWx0LXJvbGUiOiJ1c2VyIiwiWC1IYXN1cmEtVXNlci1JZCI6IjE2YzE5ZDIzLTJkY2ItNDVlMy1iODI1LTM1NTQ1YmQ4MjhjNSJ9LCJpYXQiOjE2OTIxODEwOTEsImV4cCI6MTcyMzcxNzA5MX0.M4XDDYiYaa6ymEfiUkyuQEePxDe0VSD8VyRIvlI7Jns',
        'content-type': 'application/json',
        'origin': 'https://www.flowdiver.io',
        'referer': 'https://www.flowdiver.io/',
        'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    }

    json_data = {
        'operationName': 'RecentContracts',
        'query': 'query RecentContracts($limit: Int, $offset: Int, $addressFilter: String_comparison_exp, $parentFilter: String_comparison_exp) @cached(ttl: 60) {\n  contracts(\n    limit: $limit\n    offset: $offset\n    where: {parent_contract_id: $parentFilter, address: $addressFilter}\n    order_by: {valid_from: desc_nulls_first}\n  ) {\n    name\n    address\n    parent_contract_id\n    id\n    transaction_hash\n    status\n    diff\n    valid_from\n    __typename\n  }\n}',
        'variables': {
            'addressFilter': {},
            'limit': 25,
            'offset': offset,
            'parentFilter': {},
        },
    }

    response = requests.post('https://api.findlabs.io/hasura/v1/graphql', headers=headers, json=json_data)
    print(response.text[0:100])
    return response.json()

#解析一个合约
def parse_contract(contract):
    contract_name = contract["name"]
    contract_address = contract["address"]
    data = {
        "contract_name": contract_name,
        "contract_address": contract_address,
    }
    return data

def contrat_tl(contract_list):
    data_list = []
    for contract in contract_list:
        data = parse_contract(contract)
        data_list.append(data)

    #插入数据库
    sql_appbk.insert_data_list(data_list, "flow_contract_address")



def get_all_page():
    for page in range(1, 2000):
        print("process page-----", page)
        ret = get_contract(page)
        data_list = ret["data"]["contracts"]
        if len(data_list) > 0:
            contrat_tl(contract_list=data_list)
            time.sleep(1)
        else:
            break


if __name__=="__main__":
    # page = 1
    # ret = get_contract(page) #{"data":{"contracts":[]}}
    get_all_page()