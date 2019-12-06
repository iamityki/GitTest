import requests
import json
import csv
import pandas as pd
import uuid
import sys

# 后台服务器ip
server = "10.240.70.180"
# 登录的用户名、密码
admin = "admin"
password = "admin "
# 当前脚本所在目录
path = "E:\\hrunProject\\spn"

# 根据ip获取网元nodeId
def getNodeId(ip):
    url = "http://"+ server +":8181/restconf/operational/utstarcom-sdn-connection-config:connections/"
    r = requests.get(url = url, auth = (admin, password))
    nodeConnectionList = json.loads(r.text).get("connections").get("node-connections").get("node-connection")
    nodeId = ""
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
        df.to_csv(path + "\\testcases\\csv\\group.csv", sep=',', header=True, index=False)
        writeGroupDict(groupDict)
    else:
        df = pd.DataFrame({'groupName': groupName, 'groupId': groupId})
        df.to_csv(path + "\\testcases\\csv\\group.csv", sep=',', header=True, index=False)
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
        df.to_csv(path + "\\testcases\\csv\\link.csv", sep=',', header=True, index=False)
    else:
        df = pd.DataFrame({'linkId': linkId})
        df.to_csv(path + "\\testcases\\csv\\link.csv", sep=',', header=True, index=False)

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
def getPrefix(nodeIp,clientName,status="deactive"):
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
                if status == "deactive":
                    prefix = index + ";" + ipAddr + "/"+ str(length)
                elif status == "active":
                    prefix = ipAddr + "/" + str(length)
    else:
        prefix = ""
    return prefix

def writeClientId():
    url = "http://" + server + ":8181/restconf/config/utstarcom-sdn-flexe:flexe-clients"
    r = requests.get(url=url, auth=(admin, password))
    clientId = []
    clientName = []
    if r.status_code != 404:
        clientList = json.loads(r.text).get("flexe-clients").get("flexe-client")
        for client in clientList:
            clientId.append(client.get("id"))
            clientName.append(client.get("name"))
            df = pd.DataFrame({'clientName': clientName, 'clientId': clientId})
            df.to_csv(path + "\\testcases\\csv\\clientNameAndId.csv", sep=',', header=True, index=False)
    else:
        df = pd.DataFrame({'clientName': clientName, 'clientId': clientId})
        df.to_csv(path + "\\testcases\\csv\\clientNameAndId.csv", sep=',', header=True, index=False)

def writeAdjId():
    url = "http://" + server + ":8181/restconf/config/utstarcom-sdn-spn-sid:SR-Domain-SID"
    r = requests.get(url=url, auth=(admin, password))
    adjSidList = json.loads(r.text).get("SR-Domain-SID").get("SR-Domains")[0].get("Adj-SID")
    adjDict = {}
    for adj in adjSidList:
        adjSid = adj.get("adj-sid-id")
        adjName = adj.get("name")
        adjDict[adjName] = adjSid
    filename = path + "\\testcases\\csv\\adjDict.csv"
    with open(filename, "w+") as file_object:
        if adjDict != "":
            file_object.seek(0, 0)
            file_object.write(str(adjDict))
        else:
            file_object.seek(0, 0)
            file_object.write()

def getAdjIdByName(name):
    filename = path + "\\testcases\\csv\\adjDict.csv"
    with open(filename,"r")as file_object:
        content = file_object.read()
        if content != "":
            contentDict = eval(content)
            id = contentDict[name]
        else:
            id = ""
        return id
