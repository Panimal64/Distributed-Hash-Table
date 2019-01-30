import hashlib
import socket
import sys
import linecache
import struct
import math

HOST = None
PORT = None
NODE_ID = None
SUCCESSOR = None
SUCCESSOR_HOST = None
SUCCESSOR_PORT = None
HOSTLIST = []
PORTLIST = []
NODELIST = []
DICTIONARY = {}

FINGERHOST = []
FINGERPORT = []
FINGERNODE = []

#Open file provided with command line arguement
try:
    f = open(sys.argv[1], "r")
    for line in f:
        split = line.split(" ")
        loop_host = str(split[0])
        addr_IP = str(socket.gethostbyname(loop_host))
        HOSTLIST.append(addr_IP)
        loop_port = int(split[1])
        PORTLIST.append(loop_port)
    f.close()
except OSError:
    print("File not found")
    sys.exit(1)

#Read in file, splitting at white space, getting IP address and PORT numbers 
#and appending to corresponding list


#Loop though HOSTLIST and PORTLIST and obtain nodeID and append to NODELIST
for line in range(0,len(HOSTLIST)):
    nbo_IP = socket.inet_aton(HOSTLIST[line])
    nbo_PORT = (PORTLIST[line]).to_bytes(2, byteorder='big')
    node_ID_hex = hashlib.sha1(nbo_IP + nbo_PORT).hexdigest()
    NODELIST.append(node_ID_hex)


#Assign HOST/PORT/NODE_ID to the corresponding index from commandline
HOST = HOSTLIST[int(sys.argv[2])]
PORT = PORTLIST[int(sys.argv[2])]
NODE_ID = NODELIST[int(sys.argv[2])]


#Sort HOST/PORT/NODE lists together by NODELIST
NODELIST, HOSTLIST, PORTLIST = zip(*sorted(zip(NODELIST, HOSTLIST, PORTLIST)))

#find index of NODE_ID in sorted list
index = NODELIST.index(NODE_ID)


#Create Finger Table  (Yes, I could have done this as a Tuple and initially did
#but it lead to issues such as it appending ')' to the end of the nodeid when trying
#to extract it from the finger table resulting in more code to correct it
half_way = 1
while(half_way < len(NODELIST)):
    FINGERHOST.append(HOSTLIST[(index+half_way)%len(NODELIST)])
    FINGERPORT.append(PORTLIST[(index+half_way)%len(NODELIST)])
    FINGERNODE.append(NODELIST[(index+half_way)%len(NODELIST)])
    half_way = 2 * half_way

#Mod arthicmatic on finger table so that all values have same base
for x in range(0,len(FINGERNODE)):
    temp = int(FINGERNODE[x], 16)
    node_dec = int(NODE_ID, 16)
    finger_dec = ((temp-node_dec)%int(math.pow(2,160)))
    FINGERNODE[x]=finger_dec

#DEBUG
#print("Fingertable")
#print(FINGERNODE)

'''# Dead Code for determining successor linearly
#Assign SUCESSOR from sorted NODELIST
if(index == len(NODELIST)-1):
    SUCCESSOR = NODELIST[0]
    SUCCESSOR_HOST = HOSTLIST[0]
    SUCCESSOR_PORT = PORTLIST[0]
else:
    SUCCESSOR = NODELIST[index + 1]
    SUCCESSOR_HOST = HOSTLIST[index + 1]
    SUCCESSOR_PORT = PORTLIST[index + 1]

print(NODELIST)
print('\n')
print("NODE_ID")
print(NODE_ID)
print("SUCCESSOR")
print(SUCCESSOR)
'''

#Bind UDP socket
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
except OSError:
    print("Could not bind to socket")

#Main Node code
while(True):
    #Recieve from socket, seperate message from address, decode message and split into list
    bytes_address_pair = sock.recvfrom(4096)
    message = bytes_address_pair[0]
    address = bytes_address_pair[1]
    message = message.decode()
    message = message.split(" ")
    #print(message)

    #Note on message format from client
    '''Message format from client:
        HOP1 + get|put + KEY + VALUE|-1 '''
    #Note on what message is modified to on First Node and how remaining nodes recieve message
    '''MODIFIED MESSAGE FORMAT: 
        HOP# + get|put + KEY + VALUE|-1 + CLIENT ADDR + CLIENT PORT + Y|N (Store Tag)'''

    #Obtain the Hash of the key in hex and set dictionary result (for 'get' messages) to None
    key_hash = message[2].encode()
    key_hash = hashlib.sha1(key_hash).hexdigest()
    dict_result = None

    #If message is first hop from client, append client IP/Port & Y/N 
    if(message[0] == '1'):
        message.append(address[0])
        print(address[0])
        message.append(str(address[1]))
        print(address[1])
        message.append('N')

    #If this is first hop and message is a get, check to see if hash key exists in this node, if so don't want to pass to next node, just return to client and not increment hop counter
    if(message[0] == '1') and (message[1] =='get'):
        key = message[2]
        if(key in DICTIONARY):
            message[6] = 'Y'

    
    '''#Dead code, was for linear successor lookup
    if (message[6] == 'N'):
        if(NODE_ID < key_hash <= SUCCESSOR):
            message[6] = 'Y'
        elif(SUCCESSOR < NODE_ID) and (key_hash <= SUCCESSOR):
            message[6] = 'Y'
        elif(SUCCESSOR < NODE_ID) and (key_hash > NODE_ID):
            message[6] = 'Y'
        hop = int(message[0])
        hop += 1
        message[0]= str(hop)
     '''
    
    #Set successorIP and PORT to default of furthest node in fingertable
    SUCCESSOR_HOST = FINGERHOST[len(FINGERNODE)-1]
    SUCCESSOR_PORT = FINGERPORT[len(FINGERNODE)-1]

    #If check is N, compare key to fingertable to see where to store key
    if(message[6] == 'N'):
        counter = len(FINGERNODE)-1
        for i in reversed(FINGERNODE):
            fingerdec = FINGERNODE[counter]
            nodedec = int(NODE_ID,16)
            keydec = int(key_hash, 16)
            comparison = ((keydec - nodedec)%int(math.pow(2,160)))
            
            if(comparison <= fingerdec):
                if(counter > 1):
                    SUCCESSOR_HOST = FINGERHOST[counter-1]
                    SUCCESSOR_PORT = FINGERPORT[counter-1]
                else:
                    SUCCESSOR_HOST = FINGERHOST[counter]
                    SUCCESSOR_PORT = FINGERPORT[counter] 
                    message[6]='Y'
            else:
                break
            counter = counter-1
        hop = int(message[0])
        hop += 1
        message[0]= str(hop)

    #Storage tag is YES, put/get k:v
    elif(message[6] == 'Y'):
        if(message[1] == 'get'):
            dict_result = DICTIONARY.get(message[2])

        elif(message[1] == 'put'):
            if(message[3] != '-1'):
                DICTIONARY[message[2]] = message[3]

            elif(message[3] == '-1'):
                try:
                    del DICTIONARY[message[2]]
                except:
                    dict_result = '-1'

        message[6] = 'Return'


    '''Send to client MESSAGE FORMAT: 
    HOP# + get|put + KEY + VALUE|-1 + CLIENT ADDR + CLIENT PORT + Y|N|Return (Store Tag) + key_hash + NODE_ID + dict_result'''
    
    #If message wasn't a get, set dict_result to -1 for simplier parsing on client
    if(dict_result == None):
        dict_result = '-1'

    #Code to break on infinite loops, shouldn't be needed anymore but left incase
    if(int(message[0]) > 2*len(NODELIST)):
        message[6] = 'Return'

    #IF Return, send to client, else send to next node
    if(message[6] == "Return"):
        client_host = message[4]
        client_port = int(message[5])
        message.append(key_hash)
        message.append(NODE_ID)
        message.append(dict_result)
        message = ' '.join(message)
        size = message.encode()
        send_addr = (client_host, client_port)
        sock.sendto(size,send_addr)
    else:
        message = ' '.join(message)
        size = message.encode()
        send_addr = (SUCCESSOR_HOST, SUCCESSOR_PORT)
        sock.sendto(size,send_addr) 