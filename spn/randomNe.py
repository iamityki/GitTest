import pandas as pd
import sys
import random

hostIp = []
userLabel = []
def get_data(number='10', start='1.1.1.1'):
    num_random = random.randint(97,122)
    letter_ramdom = chr(num_random)
    for i in range(number):
        label = str(i) + letter_ramdom
        userLabel.append(label)
    starts = start.split('.')
    A = int(starts[0])
    B = int(starts[1])
    C = int(starts[2])
    D = int(starts[3])
    for A in range(A, 256):
        for B in range(B, 256):
            for C in range(C, 256):
                for D in range(D, 256):
                    ip = "%d.%d.%d.%d" % (A, B, C, D)
                    if number >= 1:
                        hostIp.append(ip)
                        number -= 1
                    else:
                        return hostIp
                D = 0
            C = 0
        B = 0

def write_data(ne_type = "SPN805"):
    path = sys.path[0]
    csv_path = path + "\\testcases\\csv\\"
    df = pd.DataFrame(columns=["userLabel"],data=userLabel)
    df["hostIp"] = pd.DataFrame(hostIp)
    df["neType"] = ne_type
    df.to_csv(csv_path + "neRandom.csv", sep=',', header=True, index=False)

def write_data_hf(ne_type = "SPN805"):
    port = []
    path = sys.path[0]
    csv_path = path + "\\testcases\\csv\\"
    for i in range(17830,18829):
        userLabel.append("NE" + str(i))
        port.append(i)
    df = pd.DataFrame(columns=["userLabel"], data=userLabel)
    df["port"] = pd.DataFrame(port)
    df["neType"] = ne_type
    df.to_csv(csv_path + "neRandom.csv", sep=',', header=True, index=False)

if __name__ == '__main__':
    # 网元类型
    ne_type = "SPN805"
    # 网元数量
    ne_number = 200
    # 网元起始ip
    start_ip = "1.1.1.1"

    get_data(ne_number, start_ip)
    write_data(ne_type)
    # write_data_hf()