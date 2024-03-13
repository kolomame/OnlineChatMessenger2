import socket
import sys
import os
import threading

def protocol_header(roomnamesize, operation, operationpayloadsize):
    return roomnamesize.to_bytes(1, "big") + operation.to_bytes(1, "big") + operationpayloadsize.to_bytes(29, "big")

sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = input("Type in the server's address to connect to: ")
server_port = 9001

print('connecting to {}'.format(server_address, server_port))

try:
    sock_tcp.connect((server_address, server_port))
except socket.error as err:
    print(err)
    sys.exit(1)

username = input("My name is: ")
roomname = input("roomname: ") #roomname
operation = input("operation: ")

username_bits = username.encode('utf-8')
roomname_bits = roomname.encode('utf-8')
operation_bits = operation.encode('utf-8')

header = protocol_header(len(roomname_bits), len(operation_bits), len(username_bits))
data = roomname_bits + operation_bits + username_bits

sock_tcp.send(header)
sock_tcp.send(data)

roomid_bits = sock_tcp.recv(1)
roomid = int.from_bytes(roomid_bits, "big") #token
print("roomid: {}".format(roomid))
print('closing tcpsocket')
sock_tcp.close()

#udp

def udpheader(roomnamesize, tokensize):
    return roomnamesize.to_bytes(1, "big") + tokensize.to_bytes(1, "big")

def sendmessage(sock, server_address, server_port, roomname_bits, roomid_bits):
    while True:
        message = input("")
        print("\033[1A\033[1A") 
        print("You: " + message)
        message_bits = message.encode('utf-8')
        header = udpheader(len(roomname_bits), len(roomid_bits))
        data = roomname_bits + roomid_bits + message_bits

        sock.sendto(header, (server_address, server_port))
        sock.sendto(data, (server_address, server_port))

def receivemessage(sock):
    while True:
        receive = sock.recvfrom(1024)[0].decode('utf-8')
        print(receive)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)



server_address = input("Type in the server's address to connect to: ")
address = ''
port = 9050

sock.bind((address,port))

name = input("My name is: ")

send_thread = threading.Thread(target=sendmessage, args=(sock, server_address, server_port, roomname_bits, roomid_bits))
receive_thread = threading.Thread(target=receivemessage, args=(sock,))


send_thread.start()
receive_thread.start()

send_thread.join()
receive_thread.join()
sock.close()


        




