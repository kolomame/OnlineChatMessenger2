import socket
import os
from pathlib import Path
import time
import threading

sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = '0.0.0.0'
server_port = 9001

dpath = 'temp'
if not os.path.exists(dpath):
    os.makedirs(dpath)

print('Starting up on {} port {}'.format(server_address, server_port))

sock_tcp.bind((server_address, server_port))

sock_tcp.listen(1)




#user_room_info[roomid] = [str(roomid) + ',' + str(len(user_room_info[roomid]))] <--listnum = usernum
#token = str(roomid) + ',' + str(usernum)
#token = tcpaddress
#not think roomid...

tcp_udp_address = {} #tcp_udp_address[tcpaddress] = udpaddress
user_info = {} #user_info[address] = username
room_info = {} #room_info[roomid] = roomname
user_room_info = {} # user_room_info[roomid] = [address]
user_time = {} #user_time[address] = time
roomid = 0

while True:
    connection, address = sock_tcp.accept()
    try:
        print('connection from', address)
        header = connection.recv(31)
        print(header)
        straddress = str(address)
        print(f'straddress: {straddress}')
        print(type(straddress))

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

        print('roomname: {}, operation: {}, username: {}, address: {}'.format(roomname, operation, username, address))

        user_info[straddress] = username
        print(f'address: {address}')
        print(f'username: {user_info[straddress]}')
        #cureate new chatroom
        if operation == 1:
            room_info[roomid] = roomname
            user_room_info[roomid] = [straddress]
            roomid += 1
            connection.sendall((straddress).encode('utf-8'))
            break

        #join chatroom
        elif operation == 2:
            for key, value in room_info.items():
                if value == roomname:
                    user_room_info[key].append(straddress)
                    connection.sendall(straddress.encode('utf-8'))                    
                    break
            #not exist roomname
            """
            send to status code
            error 100: The room you are trying to join does not exist
            200: The room you are trying to join does exist
            """


    finally:
        print("Closing current connection")
        connection.close()

def sendreceivemessage(sock, user_time, user_room_info, user_info, tcp_udp_address):
    while True:
        print('\nwaiting to receive message')
        header, address = sock.recvfrom(2)
        data, address = sock.recvfrom(4096)
        print(f'data: {data}')
        

        roomnamesize = int.from_bytes(header[:1],"big")
        tcpaddresssize = int.from_bytes(header[1:2], "big")
        print(f'tcpaddresssize: {tcpaddresssize}')
        roomname_bits = data[:roomnamesize]
        tcpaddress_bits = data[roomnamesize:roomnamesize + tcpaddresssize]
        message_bits = data[roomnamesize+tcpaddresssize:]

        roomname = roomname_bits.decode('utf-8')
        tcpaddress = tcpaddress_bits.decode('utf-8')
        user_time[tcpaddress] = time.time()
        tcp_udp_address[tcpaddress] = address
        message = message_bits.decode('utf-8')
        print(f'address: {address}')
        print(f'tcpaddress: {tcpaddress}')
        print(f'user_info: {user_info}')
        username = user_info[tcpaddress]
        print(f'roomname: {roomname}, message: {message}, username: {username} ')
        senddata = f'{username}: {message}'.encode('utf-8')

        for roomid, users in user_room_info.items():
            if tcpaddress in users:
                for user in users:
                    if user == tcpaddress: continue
                    sock.sendto(senddata, tcp_udp_address[user])



        

def removeuser(sock, user_time, user_info, user_room_info, room_info, tcp_udp_address):
    while True:
        current_time = time.time()
        for tcpaddress, t in user_time.items():
            if current_time-t >= 10:
                sendmessage = f'Communication has been lost'
                #find roomid
                for roomid, tcpusers in user_room_info.items():
                    #get roomid
                    if tcpaddress in tcpusers:
                        #host or nothost
                        if tcpaddress == tcpusers[0]:
                            for user in tcpusers:
                                sock.sendto(sendmessage, tcp_udp_address[user])
                                del user_info[user]
                                del tcp_udp_address[user]
                            del room_info[roomid]
                            del user_room_info[roomid]
                            del user_time[tcpaddress]

                        else:
                            sock.sendto(sendmessage, tcp_udp_address[tcpaddress])
                            del user_info[tcpaddress]
                            del user_time[tcpaddress]
                            user_room_info[roomid].remove(tcpaddress)
                            del tcp_udp_address[tcpaddress]


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


print('starting up on port {}'.format(server_port))

sock.bind((server_address, server_port))
user_info = {} #user_info[address] = username
usertime = {} #usertime[address] = time.time()

send_thread = threading.Thread(target=sendreceivemessage, args=(sock, user_time, user_room_info, user_info, tcp_udp_address))
remove_thread = threading.Thread(target=removeuser, args=(sock, user_time, user_info, user_room_info, room_info, tcp_udp_address))

send_thread.start()
remove_thread.start()

send_thread.join()
remove_thread.join()




