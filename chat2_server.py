import socket
import os
from pathlib import Path

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = '0.0.0.0'
server_port = 9001

dpath = 'temp'
if not os.path.exists(dpath):
    os.makedirs(dpath)

print('Starting up on {} port {}'.format(server_address, server_port))

sock.bind((server_address, server_port))

sock.listen(1)





user_info = {} #user_info[address] = username
room_info = {} #room_info[roomid] = roomname
user_room_info = {} # user_room_info[roomid] = address
roomid = 0

while True:
    connection, address = sock.accept()
    try:
        print('connection from', address)
        header = connection.recv(31)
        print(header)

        roomname_length = int.from_bytes(header[:1], "big")
        operation_length = int.from_bytes(header[1:2], "big")
        username_length = int.from_bytes(header[3:], "big")

        data = connection.recv(1024)
        print("receve_data: {}".format(data))
        roomname_bits = data[:roomname_length]
        operation_bits = data[roomname_length:roomname_length + operation_length]
        username_bits = data[roomname_length + operation_length:roomname_length + operation_length + username_length]

        roomname = roomname_bits.decode('utf-8')
        operation = int(operation_bits.decode('utf-8'))
        username = username_bits.decode('utf-8')

        print('roomname: {}, operation: {}, username: {}'.format(roomname, operation, username))
        """
        send to status code
        100: username is exist another username please
        200: created chatroom
        """
        user_info[address] = username
        #cureate new chatroom
        if operation == 1:
            room_info[roomid] = roomname
            user_room_info[roomid] = [address]
            roomid += 1
            connection.sendall((roomid-1).to_bytes(1, "big"))

        #join chatroom
        elif operation == 2:
            for key, value in room_info.items():
                if value == roomname:
                    break
            user_room_info[key].append(address)
            connection.sendall(key.to_bytes(1, "big"))

        

            


    finally:
        print("Closing current connection")
        connection.close()




