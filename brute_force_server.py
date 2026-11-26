import queue
import socket
import threading

import deffihelman
import AESCLASS
from server_comm import ServerComm

host = "0.0.0.0"
port = 5000

def unpack(data):
    pass

def send_starting(ip, comm, hash_number, chunk_size):
    hash_number = f"4${hash_number}"
    chunk_size = f"4${chunk_size}"

    comm.send_msg(ip, hash_number)
    comm.send_msg(ip, chunk_size)


def handle_recv_msgs(comm, recvQ):
    """
    handles all the msgs from user
    :param comm: teh object to use form communication
    :param recvQ: the queue for receiving
    :return:
    """
    running = True
    #starts of loop
    while running:
        #gets data from the Queue
        ip, data = recvQ.get()
        # print(data)
        #splits data to opcode and params
        opcode, params = data.split("$")
        if opcode == 1:
            recvQ.put((opcode, params))
        elif opcode == 2:
            send_starting(ip)




if __name__ == '__main__':
    #initializing queue of receiving
    receivingQ = queue.Queue()
    #table of users
    hashed_number = "EC9C0F7EDCC18A98B1F31853B1813301"

    #table of images
    print("listing...")
    server_comm = ServerComm(1155, receivingQ)
    threading.Thread(target=handle_recv_msgs, args=(server_comm, receivingQ)).start()


    running = True
    while running:
        found = None
        try:
            found = True
            message = receivingQ.get()
            todo, potential = message

        except Exception as e:
            pass
        if found:
            if todo == 1:
                if potential == hashed_number:
                    print("done!")



