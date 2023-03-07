import json
import time

import requests
from flow_study_spider import sql_appbk


"""
功能：通过代码原结构，解析Identifier/Identifiers，获得代码块的EndPos
输入：declaration_node Declarations其中的一个node
返回：end_pos
"""
def parse_declaration_end_pos(declaration_node):
    if "EndPos" in declaration_node:
        end_pos = declaration_node["EndPos"]['Line']
    return end_pos

"""
功能：通过代码原结构，解析Identifier/Identifiers，获得代码块的StartPos
输入：declaration_node Declarations其中的一个node
返回：start_pos
"""
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
    if "Identifier" in declaration_node:
        struct_name = declaration_node["Identifier"]["Identifier"]
    # elif "Identifiers" in declaration_node and declaration_node["Identifiers"]!=None:
    #     struct_name = declaration_node["Identifiers"][0]["Identifier"]
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
        if "CompositeKindContract" == declaration_node["CompositeKind"]:
            struct_type = "contract"
        elif "CompositeKindResource" == declaration_node["CompositeKind"]:
            struct_type = "resource"
        elif "CompositeKindEvent" == declaration_node["CompositeKind"]:
            struct_type = "event"
        # elif "CompositeKindStructure" == declaration_node["CompositeKind"]:
        # struct_type = "structure"
        #
        # elif "FunctionDeclaration" == declaration_node["type"]:
        #     struct_type = "fun"
        else:
            struct_type = "other"
    elif "Type" in declaration_node:
        if "FunctionDeclaration" == declaration_node["Type"]:
            struct_type = "fun"
        else:
            struct_type = "other"
        # elif
        # "FieldDeclaration" = declaration_node["Type"]
        #   struct_type = "Field"
    else:
        struct_type = "other"
    return struct_type


"""
功能:解析代码，获得所有的代码段 代码类型 struct_type, 第二步 
输入:代码
返回:
"""
def process_declaration_node(declaration_node):

    # 分别调用函数，获取此节点的类型，名称，位置行号
    struct_type = parse_declaration_struct_type(declaration_node)
    struct_name = parse_declaration_struct_name(declaration_node)
    start_pos = parse_declaration_start_pos(declaration_node)
    end_pos = parse_declaration_end_pos(declaration_node)
    result_dic = {}
    result_dic["struct_type"] = struct_type
    result_dic["struct_name"] = struct_name
    result_dic["start_pos"] = start_pos
    result_dic["end_pos"] = end_pos
    return result_dic





"""
功能:解析代码，获得所有的代码段 代码类型 struct_type  ,第一步 调用  找节点
输入:代码
返回:
"""
def parse_code(declaration_nodes):
    ret_list = []
    # 遍历code的declaration节点，逐个进行处理
    for declaration_node in declaration_nodes:
        # 非import类型才继续处理分析
        if declaration_node['Type'] != 'ImportDeclaration':
            # 调用函数解析一个节点内的数据
            # 最外层，第一层函数 一般只有一个
            result_dic = process_declaration_node(declaration_node)
            ret_list.append(result_dic)
            if "Members" in declaration_node and declaration_node["Members"]["Declarations"]:
                for declaration_node2 in declaration_node["Members"]["Declarations"]:
                    # 第二层
                    result_dic = process_declaration_node(declaration_node2)
                    ret_list.append(result_dic)
                    # 第三层
                    if "Members" in declaration_node2 and declaration_node2["Members"]["Declarations"]:
                        for declaration_node3 in declaration_node2["Members"]["Declarations"]:
                            # 第二层
                            result_dic = process_declaration_node(declaration_node3)
                            ret_list.append(result_dic)
    print(ret_list)
    return ret_list


        # print("stttyp"+struct_type)
        # 判断两级declaration_node
    #     if "Members" in declaration_node:
    #         declaration_node2 = declaration_node["Members"]["Declarations"]
    #         for declaration_node2_sub in declaration_node2:
    #             struct_type = parse_declaration_struct_type(declaration_node2_sub)
    #             struct_name = parse_declaration_struct_name(declaration_node2_sub)
    #             start_pos = parse_declaration_start_pos(declaration_node2_sub)
    #             end_pos = parse_declaration_end_pos(declaration_node2_sub)
    #             result_dic = {}
    #             result_dic["struct_type"] = struct_type
    #             result_dic["struct_name"] = struct_name
    #             result_dic["start_pos"] = start_pos
    #             result_dic["end_pos"] = end_pos
    #             ret_list.append(result_dic)
    # return ret_list

"""
功能：通过contract_code 代码 调用go服务，获取包含代码结构的code_text,
"""
def get_code_text(contract_code):
    url =  "http://127.0.0.1:8080/parse"
    # url =  "http://8.218.127.18:8080/parse"
    ret = requests.post(url, data=contract_code.encode('utf-8'))
    ret_text = ret.text
    if ret_text is None or ret_text == '':
        return "null"
    code_text = json.loads(ret_text)
    return code_text
    # return ret_text
"""
功能： 更新数据库
输入： 
返回： 
"""
def code_et():
    sql = """
    SELECT id,contract_address,contract_name,contract_code FROM `flow_code` WHERE contract_type = "contract" and is_structed = 0 limit 20
    """
    flow_code = sql_appbk.mysql_com(sql)
    if 0 == len(flow_code):
        time.sleep(60*60)
        print("sleep")
        return 0

    for item in flow_code:
        # print(item['contract_code'])
        print(item["id"])
        print("next contract_code ......printing...... ")
        contract_code_single = item['contract_code']

    # step1，E extract，所有东西都是etl，获得原始解析数据，从GO的服务中获取
        code_text = get_code_text(contract_code_single)

        if code_text != "null":
        # step2 T transform 解析原始数据代码，获得需要的数据结构信息
            declaration_nodes = code_text["program"]["Declarations"]
            result_list = parse_code(declaration_nodes)
            for ret_dic in result_list:
                sql_insert = """
                INSERT INTO flow_code_struct (contract_address,contract_name,struct_type,struct_name,start_pos,end_pos) VALUES ("{}", "{}", "{}", "{}", "{}", "{}")
                """.format(item['contract_address'], item['contract_name'], ret_dic['struct_type'], ret_dic["struct_name"], ret_dic['start_pos'], ret_dic['end_pos'])
                insert_struct = sql_appbk.mysql_com(sql_insert)
            sql_update = """
            update  `flow_code` set is_structed=1 where id = {}
            """.format(item["id"])
            sql_appbk.mysql_com(sql_update)
        else:
            # 解析后的code_text，有值为空的情况
            print("code_text is null")
    return 0


"""
功能:解析代码，获得所有的代码段 代码类型 struct_type
输入:代码
返回:
"""

if __name__ == '__main__':
    declaration_node_text1 = """
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



#     declaration_node_text = """
#     import FungibleToken from 0xf233dcee88fe0abe
#     import NyatheesOVO from 0x75e0b6de94eb05d0
#     import NonFungibleToken from 0x1d7e57aa55817448
#
#     pub contract OVOMarketPlace{
#
#         pub enum orderStatues: UInt8{
#             pub case onSell
#             pub case sold
#             pub case canceled
#         }
#         pub struct orderData{
#             // order Id
#             pub let orderId: UInt64;
#             // order statue
#             pub var orderStatue: orderStatues;
#             // tokenId of in this order
#             pub let tokenId: UInt64;
#             // seller address
#             pub let sellerAddr: Address;
#             // buyer address
#             pub var buyerAddr: Address?;
#             // token name
#             pub let tokenName: String;
#             // total price
#             pub let totalPrice: UFix64;
#             // create time of this order
#             pub let createTime: UFix64;
#             // sold time of this order
#             pub let soldTime: UFix64;
#
#             init(orderId: UInt64, orderStatue: orderStatues, tokenId: UInt64, sellerAddr: Address,
#                 buyerAddr: Address?, tokenName: String, totalPrice: UFix64, createTime: UFix64
#                 soldTime: UFix64){
#                     self.orderId = orderId;
#                     self.orderStatue = orderStatue;
#                     self.tokenId = tokenId;
#                     self.sellerAddr = sellerAddr;
#                     self.buyerAddr = buyerAddr;
#                     self.tokenName = tokenName;
#                     self.totalPrice = totalPrice;
#                     self.createTime = createTime;
#                     self.soldTime = soldTime;
#             }
#         }
#
#         pub event SellNFT(sellerAddr: Address, orderId: UInt64, tokenId: UInt64, totalPrice: UFix64,
#                          buyerFee: UFix64, sellerFee: UFix64, tokenName: String, createTime: UFix64)
#         pub event BuyNFT(buyerAddr: Address, orderId: UInt64, tokenId: UInt64, totalPrice: UFix64,
#                         buyerFee: UFix64, sellerFee: UFix64, createTime: UFix64,
#                         soldTime: UFix64)
#         pub event CancelOrder(orderId: UInt64, sellerAddr: Address, cancelTime: UFix64)
#         pub event MarketControllerCreated()
#
#
#         //path
#         pub let MarketPublicPath: PublicPath
#         pub let MarketControllerPrivatePath: PrivatePath
#         pub let MarketControllerStoragePath: StoragePath
#
#         // public functions to all users to buy and sell NFTs in this market
#         pub resource interface MarketPublic {
#             // @dev
#             // orderId: get it from orderList
#             // buyerAddr: the one who want to buy NFT
#             // buyerTokenVault: the vault from the buyer to buy NFTs
#             // this function will transfer NFT from onSellNFTList to the buyer
#             // transfer fees to admin, deposit price to seller and set order statue to sold
#             pub fun buyNFT(orderId: UInt64, buyerAddr: Address, tokenName: String, buyerTokenVault: @FungibleToken.Vault);
#
#             // @dev
#             // sellerAddr: as it means
#             // tokenName: to support other tokens, you shuould pass tokenName like "FUSD"
#             // totalPrice: total price of this NFT, which contains buyer fee
#             // sellerNFT: the NFT seller want to sell
#             // this function will create an order, move NFT resource to onSellNFTList
#             // and set order statue to onSell
#             pub fun sellNFT(sellerAddr: Address, tokenName: String, totalPrice: UFix64, tokenId: UInt64,
#                                         sellerNFTProvider: &NyatheesOVO.Collection{NonFungibleToken.Provider, NyatheesOVO.NFTCollectionPublic});
#
#             // @dev
#             // orderId: the order to cancel
#             // sellerAddr: only the seller can cancel it`s own order
#             // this will set order statue to canceled and return the NFT to the seller
#             pub fun cancelOrder(orderId: UInt64, sellerAddr: Address);
#
#             // @dev
#             // this function will return order list
#             pub fun getMarketOrderList(): [orderData];
#
#             // @dev
#             // this function will return an order data
#             pub fun getMarketOrder(orderId: UInt64): orderData?
#
#             // @dev
#             // this function will return transaction fee
#             pub fun getTransactionFee(tokenName: String): UFix64?
#         }
#
#         // private functions for admin to set some args
#         pub resource interface MarketController {
#             pub fun setTransactionFee(tokenName: String, fee_percentage: UFix64);
#             pub fun setTransactionFeeReceiver(receiverAddr: Address);
#             pub fun getTransactionFeeReceiver(): Address?;
#         }
#
#         pub resource Market: MarketController, MarketPublic {
#
#             // save on sell NFTs
#             access(self) var onSellNFTList:@{UInt64: NonFungibleToken.NFT};
#             // order list
#             access(self) var orderList: {UInt64: orderData};
#             // fee list, like "FUSD":0.05
#             // 0.05 means 5%
#             access(self) var transactionFeeList: {String: UFix64}
#             // record current orderId
#             // it will increase 1 when a new order is created
#             access(self) var orderId: UInt64;
#             // fees receiver
#             access(self) var transactionFeeReceiverAddr: Address?;
#
#             destroy() {
#                 destroy self.onSellNFTList;
#              }
#             // public functions
#             pub fun buyNFT(orderId: UInt64, buyerAddr: Address, tokenName: String, buyerTokenVault: @FungibleToken.Vault) {
#                 pre {
#                     buyerAddr != nil : "Buyer Address Can not be nil"
#                     orderId >= 0 : "Wrong Token Id"
#                     self.orderList[orderId] != nil : "Order not exist"
#                     self.onSellNFTList[orderId] != nil : "Order was canceled or sold"
#                     self.transactionFeeList["FUSD_SellerFee"] != nil : "Seller Fee not set"
#                     self.transactionFeeList["FUSD_BuyerFee"] != nil : "buyer Fee not set"
#                 }
#
#                 // get order data
#                 // and it should exist
#                 var orderData = self.orderList[orderId]
#                 if (orderData!.orderStatue != orderStatues.onSell){
#                     panic("Unable to buy the order which was sold or canceled")
#                 }
#
#                 // get transaction fee for seller and buyer
#                 var sellerFeePersentage = self.transactionFeeList[tokenName.concat("_SellerFee")]!
#                 var buyerFeePersentage = self.transactionFeeList[tokenName.concat("_BuyerFee")]!
#                 if (sellerFeePersentage == nil || buyerFeePersentage == nil){
#                     panic("Fees not found")
#                 }
#
#                 var sellerFUSDReceiver = getAccount(orderData!.sellerAddr)
#                             .getCapability(/public/fusdReceiver)
#                             .borrow<&{FungibleToken.Receiver}>()
#                             ?? panic("Unable to borrow seller receiver reference")
#
#                 var feeReceiverFUSDReceiver = getAccount(self.transactionFeeReceiverAddr!)
#                             .getCapability(/public/fusdReceiver)
#                             .borrow<&{FungibleToken.Receiver}>()
#                             ?? panic("Unable to borrow fee receiver reference")
#
#                 var totalPrice = orderData!.totalPrice
#                 if (totalPrice == nil || totalPrice <= 0.0){
#                     panic("Wrong total price")
#                 }
#
#                 // balance of buyer token vault should > total price
#                 // if we have buyer fee
#                 var buyerFee = totalPrice * (buyerFeePersentage * 100000000.0) / 100000000.0
#                 var sellerFee = totalPrice * (sellerFeePersentage * 100000000.0) / 100000000.0
#
#                 // deposit buyer fee if exist
#                 if (buyerFeePersentage > 0.0){
#                     feeReceiverFUSDReceiver.deposit(from: <-buyerTokenVault.withdraw(amount: buyerFee))
#                 }
#
#                 // total price should >= buyer vault balance
#                 // after deposit fees
#                 if (totalPrice > buyerTokenVault.balance){
#                     panic("Please provide enough money")
#                 }
#
#                 // deposit seller fee
#                 feeReceiverFUSDReceiver.deposit(from: <-buyerTokenVault.withdraw(amount: sellerFee))
#                 // deposit valut to seller
#                 sellerFUSDReceiver.deposit(from: <-buyerTokenVault)
#
#                 var buyerNFTCap = getAccount(buyerAddr).getCapability(NyatheesOVO.CollectionPublicPath).borrow<&{NyatheesOVO.NFTCollectionPublic}>()
#                                                             ?? panic("Unable to borrow NyatheesOVO Collection of the seller")
#                 // deposit NFT to buyer
#                 buyerNFTCap.deposit(token: <-self.onSellNFTList.remove(key: orderId)!)
#                 // update order info
#                 self.orderList[orderId] = OVOMarketPlace.orderData(orderId: orderData!.orderId, orderStatue: orderStatues.sold,
#                                                                     tokenId: orderData!.tokenId, sellerAddr: orderData!.sellerAddr, buyerAddr: buyerAddr,
#                                                                     tokenName: orderData!.tokenName, totalPrice: totalPrice,
#                                                                     createTime: orderData!.createTime, soldTime: getCurrentBlock().timestamp)
#
#                 emit BuyNFT(buyerAddr: buyerAddr, orderId: orderId, tokenId: orderData!.tokenId,
#                             totalPrice: totalPrice, buyerFee: buyerFee, sellerFee: sellerFee,
#                             createTime: orderData!.createTime, soldTime: getCurrentBlock().timestamp)
#
#             }
#
#             pub fun sellNFT(sellerAddr: Address, tokenName: String, totalPrice: UFix64, tokenId: UInt64,
#                         sellerNFTProvider: &NyatheesOVO.Collection{NonFungibleToken.Provider, NyatheesOVO.NFTCollectionPublic}) {
#                 pre {
#                     tokenName != "" : "Token Name Can Not Be \"\" "
#                     totalPrice > 0.0 : "Total Price should > 0.0"
#                     sellerNFTProvider != nil : "NFT Provider can not be nil"
#                     tokenId >= 0 : "Wrong Token Id"
#                     self.transactionFeeList["FUSD_SellerFee"] != nil : "Seller Fee not set"
#                     self.transactionFeeList["FUSD_BuyerFee"] != nil : "buyer Fee not set"
#                 }
#
#                 self.orderList.insert(key: self.orderId, orderData(orderId: self.orderId, orderStatue: orderStatues.onSell,
#                                                                     tokenId: tokenId, sellerAddr: sellerAddr, buyerAddr: nil,
#                                                                     tokenName: tokenName, totalPrice: totalPrice,
#                                                                     createTime: getCurrentBlock().timestamp, soldTime: 0.0))
#                 if (!sellerNFTProvider.idExists(id: tokenId)){
#                     panic("The NFT not belongs to you")
#                 }
#
#                 // check metadata
#                 // user can not sell NFT which has sign = 1
#                 var metadata = sellerNFTProvider.borrowNFTItem(id: tokenId)!.getMetadata()
#                 if (metadata != nil && metadata["sign"] != nil && metadata["sign"] == "1"){
#                     panic("You can not sell this NFT")
#                 }
#
#                 // get transaction fee for seller and buyer
#                 var sellerFeePersentage = self.transactionFeeList[tokenName.concat("_SellerFee")]!
#                 var buyerFeePersentage = self.transactionFeeList[tokenName.concat("_BuyerFee")]!
#                 if (sellerFeePersentage == nil || buyerFeePersentage == nil){
#                     panic("Fees not found")
#                 }
#
#                 self.onSellNFTList[self.orderId] <-!sellerNFTProvider.withdraw(withdrawID: tokenId)
#
#
#                 emit SellNFT(sellerAddr: sellerAddr, orderId: self.orderId, tokenId: tokenId,
#                              totalPrice: totalPrice, buyerFee: buyerFeePersentage, sellerFee: sellerFeePersentage,
#                               tokenName: tokenName, createTime: getCurrentBlock().timestamp)
#
#                 self.orderId = self.orderId + 1
#
#             }
#
#             pub fun cancelOrder(orderId: UInt64, sellerAddr: Address) {
#                 pre {
#                     sellerAddr != nil : "Seller Address Can not be nil"
#                     orderId >= 0 : "Wrong Token Id"
#                     self.orderList[orderId] != nil : "Order not exist"
#                     self.onSellNFTList[orderId] != nil : "Order was canceled or sold"
#                 }
#
#                 var orderData = self.orderList[orderId]
#                 if (orderData!.orderStatue != orderStatues.onSell){
#                     panic("Unable to cancel the order which was sold or canceled!")
#                 }
#
#                 if (orderData!.sellerAddr != sellerAddr){
#                     panic("Unable to cancel the order which not belongs to you!")
#                 }
#
#                 var tokenId = orderData!.tokenId
#
#                 var sellerNFTCap = getAccount(sellerAddr).getCapability(NyatheesOVO.CollectionPublicPath).borrow<&{NyatheesOVO.NFTCollectionPublic}>()
#                                                             ?? panic("Unable to borrow NyatheesOVO Collection of the seller!")
#                 sellerNFTCap.deposit(token: <-self.onSellNFTList.remove(key: orderId)!)
#
#                 self.orderList[orderId] = OVOMarketPlace.orderData(orderId: orderData!.orderId, orderStatue: orderStatues.canceled,
#                                                                     tokenId: tokenId, sellerAddr: sellerAddr, buyerAddr: nil,
#                                                                     tokenName: orderData!.tokenName, totalPrice: orderData!.totalPrice,
#                                                                     createTime: orderData!.createTime, soldTime: getCurrentBlock().timestamp)
#                 emit CancelOrder(orderId: orderId, sellerAddr: sellerAddr, cancelTime: getCurrentBlock().timestamp)
#             }
#
#             pub fun getMarketOrderList(): [orderData] {
#                 return self.orderList.values;
#             }
#
#             pub fun getMarketOrder(orderId: UInt64): orderData?{
#                 return self.orderList[orderId]
#             }
#
#             pub fun getTransactionFee(tokenName: String): UFix64?{
#                 return self.transactionFeeList[tokenName]
#             }
#
#             // private functions
#             pub fun setTransactionFee(tokenName: String, fee_percentage: UFix64) {
#                 self.transactionFeeList[tokenName] = fee_percentage;
#             }
#
#             pub fun setTransactionFeeReceiver(receiverAddr: Address) {
#                 self.transactionFeeReceiverAddr = receiverAddr;
#             }
#
#             pub fun getTransactionFeeReceiver(): Address? {
#                 return self.transactionFeeReceiverAddr
#             }
#
#             init(){
#                 self.onSellNFTList <- {};
#                 self.orderList = {};
#                 self.transactionFeeList = {};
#                 self.orderId = 0;
#                 self.transactionFeeReceiverAddr = nil;
#             }
#         }
#
#         init(){
#             self.MarketPublicPath = /public/MarketPublic;
#             self.MarketControllerPrivatePath = /private/MarketControllerPrivate;
#             self.MarketControllerStoragePath = /storage/MarketControllerStorage;
#             let market <- create Market();
#             self.account.save(<-market, to: self.MarketControllerStoragePath)
#             self.account.link<&OVOMarketPlace.Market{MarketPublic}>(self.MarketPublicPath, target: self.MarketControllerStoragePath)
#             emit MarketControllerCreated()
#         }
#     }
#     """


    declaration_node_text = """
    import FungibleToken from 0xf233dcee88fe0abe
    import NonFungibleToken from 0x1d7e57aa55817448
    import DapperUtilityCoin from 0xead892083b3e2c6c

    // Offers
    //
    // Contract holds the Offer resource and a public method to create them.
    //
    // Each Offer can have one or more royalties of the sale price that
    // goes to one or more addresses.
    //
    // Owners of NFT can watch for OfferAvailable events and check
    // the Offer amount to see if they wish to accept the offer.
    //
    // Marketplaces and other aggregators can watch for OfferAvailable events
    // and list offers of interest to logged in users.
    //
    pub contract Offers {
        // OfferAvailable
        // An Offer has been created and added to the users DapperOffer resource.
        //
        pub event OfferAvailable(
            offerAddress: Address,
            offerId: UInt64,
            nftType: Type,
            nftId: UInt64,
            offerAmount: UFix64,
            royalties: {Address:UFix64},
        )

        // OfferCompleted
        // The Offer has been resolved. The offer has either been accepted
        //  by the NFT owner, or the offer has been removed and destroyed.
        //
        pub event OfferCompleted(
            offerId: UInt64,
            nftType: Type,
            nftId: UInt64,
            purchased: Bool,
            acceptingAddress: Address?,
        )

        // Royalty
        // A struct representing a recipient that must be sent a certain amount
        // of the payment when a NFT is sold.
        //
        pub struct Royalty {
            pub let receiver: Capability<&{FungibleToken.Receiver}>
            pub let amount: UFix64

            init(receiver: Capability<&{FungibleToken.Receiver}>, amount: UFix64) {
                self.receiver = receiver
                self.amount = amount
            }
        }
pub resource SomeResource {
    pub var value: Int

    init(value: Int) {
        self.value = value
    }
}
        // OfferDetails
        // A struct containing Offers' data.
        //
        pub struct OfferDetails {
            // The ID of the offer
            pub let offerId: UInt64
            // The Type of the NFT
            pub let nftType: Type
            // The ID of the NFT
            pub let nftId: UInt64
            // The Offer amount for the NFT
            pub let offerAmount: UFix64
            // Flag to tracked the purchase state
            pub var purchased: Bool
            // This specifies the division of payment between recipients.
            pub let royalties: [Royalty]

            // setToPurchased
            // Irreversibly set this offer as purchased.
            //
            access(contract) fun setToPurchased() {
                self.purchased = true
            }

            // initializer
            //
            init(
                offerId: UInt64,
                nftType: Type,
                nftId: UInt64,
                offerAmount: UFix64,
                royalties: [Royalty]
            ) {
                self.offerId = offerId
                self.nftType = nftType
                self.nftId = nftId
                self.offerAmount = offerAmount
                self.purchased = false
                self.royalties = royalties
            }
        }

        // OfferPublic
        // An interface providing a useful public interface to an Offer resource.
        //
        pub resource interface OfferPublic {
            // accept
            // This will accept the offer if provided with the NFT id that matches the Offer
            //
            pub fun accept(
                item: @NonFungibleToken.NFT,
                receiverCapability: Capability<&{FungibleToken.Receiver}>
            ): Void
            // getDetails
            // Return Offer details
            //
            pub fun getDetails(): OfferDetails
        }

        pub resource Offer: OfferPublic {
            // The OfferDetails struct of the Offer
            access(self) let details: OfferDetails
            // The vault which will handle the payment if the Offer is accepted.
            access(contract) let vaultRefCapability: Capability<&{FungibleToken.Provider, FungibleToken.Balance}>
            // Receiver address for the NFT when/if the Offer is accepted.
            access(contract) let nftReceiverCapability: Capability<&{NonFungibleToken.CollectionPublic}>

            init(
                vaultRefCapability: Capability<&{FungibleToken.Provider, FungibleToken.Balance}>,
                nftReceiverCapability: Capability<&{NonFungibleToken.CollectionPublic}>,
                nftType: Type,
                nftId: UInt64,
                amount: UFix64,
                royalties: [Royalty],
            ) {
                pre {
                    nftReceiverCapability.check(): "reward capability not valid"
                }
                self.vaultRefCapability = vaultRefCapability
                self.nftReceiverCapability = nftReceiverCapability

                var price: UFix64 = amount
                let royaltyInfo: {Address:UFix64} = {}

                for royalty in royalties {
                    assert(royalty.receiver.check(), message: "invalid royalty receiver")
                    price = price - royalty.amount
                    royaltyInfo[royalty.receiver.address] = royalty.amount
                }

                assert(price > 0.0, message: "price must be > 0")

                self.details = OfferDetails(
                    offerId: self.uuid,
                    nftType: nftType,
                    nftId: nftId,
                    offerAmount: amount,
                    royalties: royalties
                )

                emit OfferAvailable(
                    offerAddress: nftReceiverCapability.address,
                    offerId: self.details.offerId,
                    nftType: self.details.nftType,
                    nftId: self.details.nftId,
                    offerAmount: self.details.offerAmount,
                    royalties: royaltyInfo,
                )
            }

            // accept
            // Accept the offer if...
            // - Calling from an Offer that hasn't been purchased/desetoryed.
            // - Provided with a NFT matching the NFT id within the Offer details.
            // - Provided with a NFT matching the NFT Type within the Offer details.
            //
            pub fun accept(
                    item: @NonFungibleToken.NFT,
                    receiverCapability: Capability<&{FungibleToken.Receiver}>
                ): Void {

                pre {
                    !self.details.purchased: "Offer has already been purchased"
                    item.id == self.details.nftId: "item NFT does not have specified ID"
                    item.isInstance(self.details.nftType): "item NFT is not of specified type"
                }

                self.details.setToPurchased()
                self.nftReceiverCapability.borrow()!.deposit(token: <- item)

                let initalDucSupply = self.vaultRefCapability.borrow()!.balance
                let payment <- self.vaultRefCapability.borrow()!.withdraw(amount: self.details.offerAmount)

                // Payout royalties
                for royalty in self.details.royalties {
                    if let receiver = royalty.receiver.borrow() {
                        let amount = royalty.amount
                        let part <- payment.withdraw(amount: amount)
                        receiver.deposit(from: <- part)
                    }
                }

                receiverCapability.borrow()!.deposit(from: <- payment)

                // If a DUC vault is being used for payment we must assert that no DUC is leaking from the transactions.
                let isDucVault = self.vaultRefCapability.isInstance(
                    Type<Capability<&DapperUtilityCoin.Vault{FungibleToken.Provider, FungibleToken.Balance}>>()
                )

                if isDucVault {
                    assert(self.vaultRefCapability.borrow()!.balance == initalDucSupply, message: "DUC is leaking")
                }

                emit OfferCompleted(
                    offerId: self.details.offerId,
                    nftType: self.details.nftType,
                    nftId: self.details.nftId,
                    purchased: self.details.purchased,
                    acceptingAddress: receiverCapability.address,
                )
            }

            // getDetails
            // Return Offer details
            //
            pub fun getDetails(): OfferDetails {
                return self.details
            }

            destroy() {
                if !self.details.purchased {
                    emit OfferCompleted(
                        offerId: self.details.offerId,
                        nftType: self.details.nftType,
                        nftId: self.details.nftId,
                        purchased: self.details.purchased,
                        acceptingAddress: nil,
                    )
                }
            }
        }

        // makeOffer
        pub fun makeOffer(
            vaultRefCapability: Capability<&{FungibleToken.Provider, FungibleToken.Balance}>,
            nftReceiverCapability: Capability<&{NonFungibleToken.CollectionPublic}>,
            nftType: Type,
            nftId: UInt64,
            amount: UFix64,
            royalties: [Royalty],
        ): @Offer {
            let newOfferResource <- create Offer(
                vaultRefCapability: vaultRefCapability,
                nftReceiverCapability: nftReceiverCapability,
                nftType: nftType,
                nftId: nftId,
                amount: amount,
                royalties: royalties,
            )
            return <-newOfferResource
        }
    }

        """



    while 1:
        code_et()


    # result = get_code_text(declaration_node_text)
    # print(result)

    # result  = parse_declaration_struct_type(declaration_node_text)
    # print(result)