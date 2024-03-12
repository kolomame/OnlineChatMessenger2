import socket
import os
from pathlib import Path
import time

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
user_room_info = {} # user_room_info[roomid] = [address]
user_time = {} #user_time[address] = time
hostusers = []
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

        user_info[address] = username
        #cureate new chatroom
        if operation == 1:
            room_info[roomid] = roomname
            user_room_info[roomid] = [address]
            hostusers.append(address)
            roomid += 1
            connection.sendall((roomid-1).to_bytes(1, "big"))
            break

        #join chatroom
        elif operation == 2:
            for key, value in room_info.items():
                if value == roomname:
                    user_room_info[key].append(address)
                    connection.sendall(key.to_bytes(1, "big"))                    
                    break
            #not exist roomname
            """
            send to status code
            error 100: not exist room
            200: exist room
            """


    finally:
        print("Closing current connection")
        connection.close()

def sendreceivemessage(sock, user_time, user_room_info):
    while True:
        print('\nwaiting to receive message')
        header, address = sock.recvfrom(2)
        data, address = sock.recvfrom(4096)
        user_time[address] = time.time()

        roomnamesize = int.from_bytes(header[:1],"big")
        roomidsize = int.from_bytes(header[1:2], "big")
        roomname_bits = data[:roomnamesize]
        roomid_bits = data[roomnamesize:roomidsize]
        message_bits = data[roomnamesize+roomidsize:]

        roomname = roomname_bits.decode('utf-8')
        roomid = roomid_bits.decode('utf-8')
        message = message_bits.decode('utf-8')
        username = user_info[address]
        print(f'roomname: {roomname}, roomid: {roomid}, message: {message}, username: {username} ')
        senddata = f'{username}: {message}'.encode('utf-8')

        for user in user_room_info[roomid]:
            if user == address: continue
            sock.sendto(senddata, user)
        

def removeuser(sock, user_time, hostusers, user_info, user_room_info, room_info):
    while True:
        current_time = time.time()
        for address, t in user_time.items():
            if current_time-t >= 10:
                sendmessage = f'Communication has been lost'
                #find roomid
                for roomid, user in user_room_info.items():
                    #get roomid
                    if address in user:
                        #host or nothost
                        if address in hostusers:
                            hostusers.remove(address)
                            for u in user:
                                sock.sendto(sendmessage, u)
                                del user_info[u]
                            del room_info[roomid]
                            del user_room_info[roomid]
                            del user_time[address]

                        else:
                            sock.sendto(sendmessage, address)
                            del user_info[address]
                            del user_time[address]
                            user_room_info[roomid].remove(address)


"""
                if address in hostusers:#replace
                    hostusers.remove(address)
                    #find hostaddress roomid
                    for roomid, user in user_room_info.items():#replace
                        #get roomid
                        if address in user:
                            for u in user:
                                sock.sendto(sendmessage, u)
                                del user_info[u]
                            del room_info[roomid]
                            del user_room_info[roomid]
                            del user_time[address]



                else:
                    
                    sock.sendto(sendmessage, address)
                    del user_info[address]
                    del user_time[address]
                    #user_room_info[roomid].remove(address)
"""




