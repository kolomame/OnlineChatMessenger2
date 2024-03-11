import socket
import sys
import os

def protocol_header(roomnamesize, operation, operationpayloadsize):
    return roomnamesize.to_bytes(1, "big") + operation.to_bytes(1, "big") + operationpayloadsize.to_bytes(29, "big")

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = input("Type in the server's address to connect to: ")
server_port = 9001

print('connecting to {}'.format(server_address, server_port))

try:
    sock.connect((server_address, server_port))
except socket.error as err:
    print(err)
    sys.exit(1)

username = input("My name is: ")
roomname = input("roomname: ")
operation = input("operation: ")

username_bits = username.encode('utf-8')
roomname_bits = roomname.encode('utf-8')
operation_bits = operation.encode('utf-8')

header = protocol_header(len(roomname_bits), len(operation_bits), len(username_bits))
data = roomname_bits + operation_bits + username_bits

sock.send(header)
sock.send(data)

roomid_bits = sock.recv(1)
roomid = int.from_bytes(roomid_bits, "big")
print("roomid: {}".format(roomid))

#udp
sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
port = 9050

def udpheader(roomnamesize, tokensize):
    return roomnamesize.to_bytes(1, "big") + tokensize.to_bytes(1, "big")

def sendmessage(sock_udp, roomname_bits, roomid_bits):
    while True:
        message = input("")
        print("\033[1A\033[1A") 
        print("You: " + message)
        message_bits = message.encode('utf-8')
        header = udpheader(len(roomname_bits), len(roomid_bits))
        




