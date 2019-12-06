import csv
import pandas as pd
import sys
import numpy as np
import uuid

path = sys.path[0]
csv_path = path + "\\testcases\\csv\\"

def get_base_data(ip_name = None,name = None,ip = None):
    try:
        text_ne = pd.read_csv(csv_path + "ne180.csv")
        text_link = pd.read_csv(csv_path + "linkPort.csv")
    except:
        print("该文件为空")
        return None
    else:
        ne_dict = {}
        ne_name = text_ne.get("userLabel")
        ne_ip = text_ne.get("hostIp")
        for i in range(ne_name.shape[0]):
            ne_dict[ne_ip[i]] = ne_name[i]
        if ip_name:
            return ne_dict,text_link
        elif name:
            return ne_name
        elif ip:
            return ne_ip

def getUuid():
    UUID = uuid.uuid4()
    return str(UUID)

def create_data_by_name(name):
    title = []
    ne_dict,text_link = get_base_data(ip_name = "get")
    source_node = text_link.get("source_node")
    dest_node = text_link.get("dest_node")
    for i in range(source_node.shape[0]):
        name_a = ne_dict.get(source_node[i])
        name_b = ne_dict.get(dest_node[i])
        _title = str(name_a) + "-" + str(name_b) + "-" + str(name)
        title.append(_title)
    return title

def write_link_and_group():
    userLabel = create_data_by_name("link")
    group_name = create_data_by_name("grouop")
    _,text_link = get_base_data(ip_name = "get")
    source_port = []
    dest_port = []
    nodea_member = text_link.get("nodea_member")
    nodeb_member = text_link.get("nodeb_member")
    for i in range(nodea_member.shape[0]):
        source_port_list = nodea_member[i].split("eth")[1].split(".")
        s_port = "\s=%s\c=1\j=%s\p=1" % (source_port_list[0],source_port_list[1])
        source_port.append(s_port)
        dest_port_list = nodeb_member[i].split("eth")[1].split(".")
        d_port = "\s=%s\c=1\j=%s\p=1" % (dest_port_list[0],dest_port_list[1])
        dest_port.append(d_port)
    df = pd.DataFrame(columns=["userLabel"], data = userLabel)
    df["source_node"] = text_link.get("source_node")
    df["dest_node"] = text_link.get("dest_node")
    df["source_port"] = source_port
    df["dest_port"] = dest_port
    df["group_name"] = group_name
    df["calendar_type"] = "A"
    df["group_id"] = "1"
    df["nodea_member"] = nodea_member
    df["nodeb_member"] = nodeb_member
    df.to_csv(csv_path + "linkAndGroup.csv", sep=',', header=True, index=False)

def write_client():
    _, text_link = get_base_data(ip_name="get")
    ip_address_A = []
    ip_address_B = []
    client_name = create_data_by_name("client")
    group_name = create_data_by_name("group")
    nodeA_ip = text_link.get("source_node")
    nodeB_ip = text_link.get("dest_node")

    ne_ip_obj = get_base_data(ip = "get")
    ne_ip_list = np.array(ne_ip_obj).tolist()
    for i in range(nodeA_ip.shape[0]):
        index_a = ne_ip_list.index(nodeA_ip[i]) + 1
        index_b = ne_ip_list.index(nodeB_ip[i]) + 1
        ip_a = "11.%d.%d.1"%(int(index_a),int(index_b))
        ip_b = "11.%d.%d.2"%(int(index_a),int(index_b))
        ip_address_A.append(ip_a)
        ip_address_B.append(ip_b)

    df = pd.DataFrame(columns=["client_name"], data=client_name)
    df["group_name"] = group_name
    df["nodeA_ip"] = nodeA_ip
    df["nodeB_ip"] = nodeB_ip
    df["used_slots"] = "1"
    df["ip_type"] = "4"
    df["ip_address_A"] = ip_address_A
    df["ip_address_B"] = ip_address_B
    df["length"] = "24"
    df["bandwidth"] = "5"
    df["aviBandwidth"] = "5000"
    df.to_csv(csv_path + "client.csv", sep=',', header=True, index=False)

def write_adj():
    local_node_ip = []
    remote_node_ip = []
    name = []
    clientName = []
    adjSid = []
    ne_dict,text_link = get_base_data(ip_name="get")
    node_s = text_link.get("source_node")
    node_d = text_link.get("dest_node")
    for i in range(node_s.shape[0]):
        local_node_ip.append(node_s[i])
        local_node_ip.append(node_d[i])
        remote_node_ip.append(node_d[i])
        remote_node_ip.append(node_s[i])
    for i in range(len(local_node_ip)):
        ne_name_l = ne_dict.get(local_node_ip[i])
        ne_name_r = ne_dict.get(remote_node_ip[i])
        name_adj = "%s-%s-adj"%(str(ne_name_l),str(ne_name_r))
        name.append(name_adj)
    _clientName = create_data_by_name("client")
    for i in range(len(_clientName)):
        clientName.append(_clientName[i])
        clientName.append(_clientName[i])
    for i in range(520192,520192+len(local_node_ip)):
        adjSid.append(i)

    df = pd.DataFrame(columns=["local_node_ip"], data=local_node_ip)
    df["remote_node_ip"] = remote_node_ip
    df["name"] = name
    df["clientName"] = clientName
    df["adjSid"] = adjSid
    df.to_csv(csv_path + "adj.csv", sep=',', header=True, index=False)

def writeNodeSid():
    node_ip = get_base_data(ip="get")
    node_name = get_base_data(name="get")
    node_sid_name = []
    node_sid_uuid = []
    for name in node_name:
        sid_name = name + "-nodeSid"
        node_sid_name.append(sid_name)
        node_sid_uuid.append(getUuid())

    df = pd.DataFrame(columns=["nodeSidName"], data=node_sid_name)
    df["nodeIp"] = node_ip
    df["uuid"] = node_sid_uuid
    df.to_csv(csv_path + "nodeSid.csv", sep=',', header=True, index=False)

if __name__ == '__main__':
    write_link_and_group()
    write_client()
    write_adj()
    writeNodeSid()