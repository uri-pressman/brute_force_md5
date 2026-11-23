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

def handle_recv_msgs(comm, recvQ, hash):
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
        opcode, params = unpack(data)
        if opcode == 1:




if __name__ == '__main__':
    #initializing queue of receiving
    receivingQ = queue.Queue()
    #table of users

    #table of images
    print("listing...")
    server_comm = ServerComm(1001, receivingQ)
    threading.Thread(target=handle_recv_msgs, args=(server_comm, receivingQ)).start()




