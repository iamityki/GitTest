import requests
import json
import csv
import pandas as pd
import uuid
import sys

# 后台服务器ip
server = "10.240.70.180"
# 当前脚本所在目录
path = sys.path[0]
# 登录的用户名、密码
admin = "admin"
password = "admin"

# 根据ip获取网元nodeId
def getNodeId(ip):
    url = "http://"+ server +":8181/restconf/operational/utstarcom-sdn-connection-config:connections/"
    r = requests.get(url = url, auth = (admin, password))
    nodeId = ""
    try:
        nodeConnectionList = json.loads(r.text).get("connections").get("node-connections").get("node-connection")
    except AttributeError as e:
        print(e)
        print(json.loads(r.text))
        return nodeId
    else:
        for item in nodeConnectionList:
            if item["host"] == ip:
                nodeId = item["id"]
                break
        return nodeId

# def setPhysicalDcId(id):
#     filename = path + "\\testcases\\csv\\groupDict.csv"
#     with open(filename,"w+") as file_object:
#         content = file_object.read()
#         if content != "":
#             contentDict = eval(content)
#         else:
#             contentDict = {}
#         contentDict["topo_id"] = id
#         file_object.seek(0,0)
#         file_object.write(str(contentDict))

def getPhysicalDcIdBySPN():
    url = "http://" + server + ":8181/topology/topology/toplevelid/physical"
    r = requests.get(url=url, auth=(admin, password))
    physicalScId = json.loads(r.text).get("id")
    urlDc = "http://" + server + ":8181/topology/topology/group/" + physicalScId
    rDc = requests.get(url=urlDc, auth=('admin', 'admin'))
    physicalScId = json.loads(rDc.text)[0].get("id")
    return physicalScId

# def getPhysicalDcId():
#     filename = path + "\\testcases\\csv\\baseVariables.csv"
#     with open(filename,"r")as file_object:
#         content = file_object.read()
#         if content != "":
#             contentDict = eval(content)
#             id = contentDict["topo_id"]
#         else:
#             id = getPhysicalDcIdBySPN()
#         return id

# 获取group的name和id,并写入group.csv文件
def writeGroupId():
    url = "http://" + server + ":8181/restconf/config/utstarcom-sdn-flexe:flexe-groups"
    r = requests.get(url=url, auth=(admin, password))
    groups = json.loads(r.text).get("flexe-groups")
    groupId = []
    groupName = []
    groupDict = {}
    if groups != None:
        groupList = json.loads(r.text).get("flexe-groups").get("flexe-group")
        for group in groupList:
            groupId.append(group["id"])
            groupName.append(group["name"])
            groupDict[group["name"]] = group["id"]
        df = pd.DataFrame({'groupName': groupName, 'groupId': groupId})
        df.to_csv(path + "\\testcases\\csv\\groupNameAndId.csv", sep=',', header=True, index=False)
        writeGroupDict(groupDict)
    else:
        df = pd.DataFrame({'groupName': groupName, 'groupId': groupId})
        df.to_csv(path + "\\testcases\\csv\\groupNameAndId.csv", sep=',', header=True, index=False)
        writeGroupDict(groupDict)

# 将group的name和id,以key:value的形式写入groupDict.csv文件
def writeGroupDict(groupDict):
    filename = path + "\\testcases\\csv\\groupDict.csv"
    with open(filename,"w+") as file_object:
        if groupDict != "":
            file_object.seek(0, 0)
            file_object.write(str(groupDict))
        else:
            file_object.seek(0, 0)
            file_object.write()

def getGroupIdByName(name):
    filename = path + "\\testcases\\csv\\groupDict.csv"
    with open(filename,"r")as file_object:
        content = file_object.read()
        if content != "":
            contentDict = eval(content)
            id = contentDict[name]
        else:
            id = ""
        return id

def writeLinkId():
    physicalDcId = getPhysicalDcIdBySPN()
    url = "http://" + server + ":8181/topology/topology/" + physicalDcId + "/" + physicalDcId
    r = requests.get(url=url, auth=(admin, password))
    linkId = []
    linkList = json.loads(r.text).get("links")
    if linkList:
        for link in linkList:
            linkId.append(link["id"])
        df = pd.DataFrame({'linkId': linkId})
        df.to_csv(path + "\\testcases\\csv\\links.csv", sep=',', header=True, index=False)
    else:
        print("无link数据")
        df = pd.DataFrame({'linkId': linkId})
        df.to_csv(path + "\\testcases\\csv\\links.csv", sep=',', header=True, index=False)

def writeClientId():
    url = "http://" + server + ":8181/flexe/mgt-client/clients"
    r = requests.get(url= url, auth=(admin,password))
    clientId = []
    clientName = []
    clientList = json.loads(r.text)
    if len(clientList):
        for client in clientList:
            clientId.append(client.get("id"))
            clientName.append(client.get("name"))
        df = pd.DataFrame({'clientId': clientId, 'clientName': clientName})
        df.to_csv(path + "\\testcases\\csv\\clientNameAndId.csv", sep=',', header=True, index=False)
    else:
        print("无client数据")
        df = pd.DataFrame({'clientId': clientId, 'clientName': clientName})
        df.to_csv(path + "\\testcases\\csv\\clientNameAndId.csv", sep=',', header=True, index=False)

def getUuid():
    UUID = uuid.uuid4()
    return str(UUID)

def getClientIdByGrouop(groupName):
    groupId = getGroupIdByName(groupName)
    url = "http://" + server + ":8181/flexe/mgt-client/clientId/groupId/"+ str(groupId)
    r = requests.get(url=url, auth=(admin, password))
    clientId = int(r.text)
    return clientId

def getDomainId():
    url = "http://" + server + ":8181/restconf/config/utstarcom-sdn-spn-sid:SR-Domain-SID"
    r = requests.get(url=url, auth=(admin, password))
    domainId = json.loads(r.text).get("SR-Domain-SID").get("SR-Domains")[0].get("domain-id")
    return domainId

# 添加adj时，获取对应网元端clientIndex值和ip
def getPrefix(nodeIp,clientName,active = "no"):
    prefix = ""
    nodeId = getNodeId(nodeIp)
    url = "http://" + server + ":8181/flexe/mgt-client/ne/"+ nodeId +"/clients"
    r = requests.get(url=url, auth=(admin, password))
    if r.status_code != "404":
        clientList = json.loads(r.text)
        for client in clientList:
            if client.get("name") == clientName:
                index = client.get("flexEClientIndex")
                ipAddr = client.get("ip-addresses")[0].get("ip-address")
                length = client.get("ip-addresses")[0].get("length")
                if active == "no":
                    prefix = index
                elif active == "yes":
                    prefix = ipAddr + "/" + str(length)
    else:
        prefix = ""
    return prefix

def writeClientId():
    url = "http://" + server + ":8181/flexe/mgt-client/clients"
    r = requests.get(url=url, auth=(admin, password))
    clientId = []
    clientName = []
    clientList = json.loads(r.text)
    if clientList:
        for client in clientList:
            clientId.append(client.get("id"))
            clientName.append(client.get("name"))
            df = pd.DataFrame({'clientName': clientName, 'clientId': clientId})
            df.to_csv(path + "\\testcases\\csv\\clientNameAndId.csv", sep=',', header=True, index=False)
    else:
        df = pd.DataFrame({'clientName': clientName, 'clientId': clientId})
        df.to_csv(path + "\\testcases\\csv\\clientNameAndId.csv", sep=',', header=True, index=False)

'''
adj部分
'''
def writeAdjId():
    domainId = getDomainId()
    url = "http://" + server + ":8181/sid/sid-mgt/domains/" + domainId + "/adj-sids"
    r = requests.get(url=url,auth=(admin,password))
    adjSid = []
    adjSidId = []
    adjDict = {}
    adjList = json.loads(r.text)
    if adjList:
        for adj in adjList:
            adjSid.append(adj.get("Adj-SID"))
            adjSidId.append(adj.get("adj-sid-id"))
            adjDict[adj.get("Adj-SID")] = adj.get("adj-sid-id")
            df = pd.DataFrame({'adjSid': adjSid, 'adjSidId': adjSidId})
            df.to_csv(path + "\\testcases\\csv\\adjSidAndId.csv", sep=',', header=True, index=False)
            writeAdjDict(adjDict)
    else:
        df = pd.DataFrame({'adjSid': adjSid, 'adjSidId': adjSidId})
        df.to_csv(path + "\\testcases\\csv\\adjSidAndId.csv", sep=',', header=True, index=False)
        writeAdjDict(adjDict)

# 将sdj的name和id,以key:value的形式写入adjDict.csv文件
def writeAdjDict(adjDict):
    filename = path + "\\testcases\\csv\\adjDict.csv"
    with open(filename,"w+") as file_object:
        if adjDict != "":
            file_object.seek(0, 0)
            file_object.write(str(adjDict))
        else:
            file_object.seek(0, 0)
            file_object.write()

def getAdjIdBySid(name):
    filename = path + "\\testcases\\csv\\adjDict.csv"
    with open(filename,"r")as file_object:
        content = file_object.read()
        if content != "":
            contentDict = eval(content)
            id = contentDict[name]
        else:
            id = ""
        return id

'''
nodeSid 部分
'''
def getPrefixIpByNodeId(ip):
    nodeId = getNodeId(ip)
    url = "http://" + server + ":8181/sid/sid-mgt/ne/"+ nodeId +"/ipaddrs/1?isNodeSID=true"
    r = requests.get(url= url,auth=(admin,password))
    prefixIpList = json.loads(r.text)
    if prefixIpList:
        for ip in prefixIpList:
            if ip == "192.168.0.254/24":
                return ip
    else:
        return "127.0.0.1/8"
        # return ""

def getNodeSid(uuid):
    domainId = getDomainId()
    url = "http://" + server + ":8181/sid/sid-mgt/domains/"+ domainId +"/labels/prefix-sids/"+ uuid
    r = requests.get(url=url,auth=(admin,password))
    nodeSid = json.loads(r.text)
    return nodeSid