import hashlib
import socket
import sys

HOP = 1
command_arg = sys.argv


if (len(command_arg) < 5) or (len(command_arg) > 6):
    print("Incorrect arguement format")
    print("USE: python3 dht_client.py NODE_ADDRESS NODE_PORT get KEY")
    print("USE: python3 dht_client.py NODE_ADDRESS NODE_PORT put KEY VALUE")
    print("USE: python3 dht_client.py NODE_ADDRESS NODE_PORT put KEY")
    sys.exit(1)

if not (command_arg[3] == "get" or command_arg[3] == "put"):
    print("Arguement must contain get or put message")
    print("USE: python3 dht_client.py NODE_ADDRESS NODE_PORT get KEY")
    print("USE: python3 dht_client.py NODE_ADDRESS NODE_PORT put KEY VALUE")
    print("USE: python3 dht_client.py NODE_ADDRESS NODE_PORT put KEY")
    sys.exit(1)

node_IP = command_arg[1]
node_PORT = command_arg[2]
message_type = command_arg[3]
message_key = command_arg[4]
message_value = '-1'



if(len(message_key) < 1) or (len(message_key) > 255):
    print("Key length too long, enter string with length between 1 and 255 characters")
    sys.exit(1)



if(message_type == 'put') and (len(command_arg) == 6):
    message_value = command_arg[5]
    if(len(message_value) > 255):
        print("Value length too long, enter string with length between 1 and 255 characters")
        sys.exit(1)



elif(message_type == 'get') and (len(command_arg) > 5):
    print("Excecessive arguements for 'get' statement")
    print("USE: python3 dht_client.py NODE NODE_PORT get KEY")
    sys.exit(1)


#Build message from client
msg_from_client = str(HOP) + " " + message_type + " " + message_key + " " + message_value
bytes_to_send = str.encode(msg_from_client)
server_address_port = (node_IP, int(node_PORT))

# Create a UDP socket at client side
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('',10559))
except OSError:
    print("Could not bind to socket")
# Send to server using created UDP socket
sock.sendto(bytes_to_send, server_address_port)


bytes_address_pair = sock.recvfrom(4096)
message = bytes_address_pair[0]
message = message.decode()
message = message.split(" ")

#Note for incoming message from Node Format
'''Message Format:
    HOP + put|get + key + value|-1 + my_ip + my_port + Return + key_hash + NODE_ID + dict_result|-1'''
#message_key_hex = hashlib.sha1(message_key.encode()).hexdigest()
#print(message_key_hex)
print("Key Hash: {}".format(message[7]))
print("Node Hash: {}".format(message[8]))
print("Hops: {}".format(message[0]))
print("Key String: {}".format(message[2]))

if(message[9]!= '-1'):
    print("Value String: {}".format(message[9]))
elif(message[1]=='get') and (message[9] == '-1'):
    print("No Value stored for Key")
