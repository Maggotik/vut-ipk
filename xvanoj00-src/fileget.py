#!/usr/bin/python3
import socket
import sys
import re

#kontrola a ulozenie argumentov
#====================================================
if(len(sys.argv) != 5):
    sys.stderr.write ("Wrong number of arguments\n")
    exit()


if(re.match('-n',sys.argv[1])):
    NAMESERVER = sys.argv[2]
    if(re.match('-f',sys.argv[3])):
        SURL = sys.argv[4]
    else:
        sys.stderr.write ("Wrong arguments\n")
        exit()
elif(re.match('-f',sys.argv[1])):
    SURL = sys.argv[2]   
    if(re.match('-n',sys.argv[3])):
        NAMESERVER = sys.argv[4]
    else:
        sys.stderr.write ("Wrong arguments\n")
        exit()
else:
    sys.stderr.write ("Wrong arguments\n")
    exit()

split = SURL.split("/", 3)
if(split[0] != 'fsp:'):
    sys.stderr.write("Wrong protocol\n")
    exit()
if(re.match('^[\w\.\-_]*$',split[2])):
    SERVER_NAME = split[2]
else:
    sys.stderr.write("Wrong server name\n")
    exit()
FILE = split[3]

if(re.match('^[\d\.]*:[\d]*$', NAMESERVER)):
    ip = NAMESERVER.split(":", 2)
else:
    sys.stderr.write("Wrong argument\n")
    exit()
HOST = ip[0]
if(re.match('^\d{1,5}$', ip[1])):
    PORT = int(ip[1])
else:
    sys.stderr.write("Wrong port\n")
    exit()
if(PORT < 0 or PORT > 65535):
    sys.stderr.write("Wrong port\n")
    exit()
#====================================================

#funkcia na preberanie spravy po jednom riadku
#====================================================
def recv_header():
    x = ""
    ret = ""
    while x != "\n":
        x = header = tcp.recv(1).decode('utf-8')
        ret += x
    return ret
#====================================================

#UDP komunikacia
#====================================================
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp.sendto(("WHEREIS " + SERVER_NAME + "\r\n").encode('utf-8'), (HOST, PORT))
breceivedMsg = udp.recv(2048)
receivedMsg = (breceivedMsg).decode('utf-8')
#kontrola prebranej spravy
if(receivedMsg == 'ERR Not Found'):
    sys.stderr.write("ERR Not Found\n")
    exit()
if(receivedMsg == 'ERR Syntax'):
    sys.stderr.write("ERR Syntax\n")
    exit()
udp.close()
port = (receivedMsg.split(":",2))
FILEPORT = int(port[1])
#====================================================

#TCP komunikacia
#====================================================
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp.connect((HOST, FILEPORT))
SAVEFILE = FILE.split("/")
#zistenie vsetkych suborov v adresary ak je v argumente *
if(SAVEFILE[-1] == '*'):
    FILE = FILE.replace("*", "index")
    tcp.send(("GET " + FILE + " FSP/1.0" + "\r\n").encode('utf-8'))
    tcp.send(("Hostname: " + SERVER_NAME + "\r\n").encode('utf-8'))
    tcp.send(("Agent: xvanoj00\r\n").encode('utf-8'))
    tcp.send(("\r\n").encode('utf-8'))
    header = recv_header()
    length = recv_header()
    tcp.recv(2)
    #kontrola prebranej spravy
    if(re.match('FSP/1.0 Not Found', header)):
        sys.stderr.write(header + "\n")
        exit()
    if(re.match('FSP/1.0 Bad Request', header)):
            sys.stderr.write(header)
            exit()
    if(re.match('FSP/1.0 Server Error', header)):
            sys.stderr.write(header)
            exit()       
    length = length.split(":") 
    length = int(length[1])
    #prebranie a uprava zoznamu suborov ktore chceme prevzat
    Msg = tcp.recv(length).decode('utf-8')
    Msg = Msg.strip()
    Msg = Msg.split("\r\n")
    tcp.close()
    #cyklus na prevzatie a ulozenie jednotlivycg suborov
    for files in Msg:
        tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp.connect((HOST, FILEPORT))
        tcp.send(("GET " + files + " FSP/1.0" + "\r\n").encode('utf-8'))
        tcp.send(("Hostname: " + SERVER_NAME + "\r\n").encode('utf-8'))
        tcp.send(("Agent: xvanoj00\r\n").encode('utf-8'))
        tcp.send(("\r\n").encode('utf-8'))
        header = recv_header()
        length = recv_header()
        tcp.recv(2)
        #kontrola prebranej spravy
        if(re.match('FSP/1.0 Not Found', header)):
            sys.stderr.write(header)
            exit()
        if(re.match('FSP/1.0 Bad Request', header)):
            sys.stderr.write(header)
            exit()
        if(re.match('FSP/1.0 Server Error', header)):
            sys.stderr.write(header)
            exit()
        length = length.split(":", 2)
        length = int(length[1])
        save = files.split("/")
        f = open(save[-1], "wb")
        #cyklus na bytovy zapis do suboru
        buffer = 0
        while buffer < length:
            btcpMsg = tcp.recv(10)
            f.write(btcpMsg)
            buffer += 10
        remainder = tcp.recv(10)
        f.write(remainder)
        f.close
        tcp.close()
#ak chceme prebrat iba jeden subor
else:
    tcp.send(("GET " + FILE + " FSP/1.0" + "\r\n").encode('utf-8'))
    tcp.send(("Hostname: " + SERVER_NAME + "\r\n").encode('utf-8'))
    tcp.send(("Agent: xvanoj00\r\n").encode('utf-8'))
    tcp.send(("\r\n").encode('utf-8'))
    header = recv_header()
    length = recv_header()
    tcp.recv(2)
    #kontrola prebranej spravy
    if(re.match('FSP/1.0 Not Found', header)):
        sys.stderr.write(header + "\n")
        exit()
    if(re.match('FSP/1.0 Bad Request', header)):
            sys.stderr.write(header)
            exit()
    if(re.match('FSP/1.0 Server Error', header)):
            sys.stderr.write(header)
            exit()
    length = length.split(":")
    length = int(length[1])
    f = open(SAVEFILE[-1], "wb")
    #cyklus na bytovy zapis do suboru
    buffer = 0
    while buffer < length:
        btcpMsg = tcp.recv(10)
        f.write(btcpMsg)
        buffer += 10
    remainder = tcp.recv(10)
    f.write(remainder)
    f.close
    tcp.close()
    #====================================================