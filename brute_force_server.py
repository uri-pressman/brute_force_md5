import socket

import deffihelman
import AESCLASS


host = "0.0.0.0"
port = 5000

def unpack(data):
    pass

def handle_recv_msgs(comm, recvQ, DB, gameWorld):
    """
    handles all the msgs from user
    :param gameWorld: world object to call funcs
    :param comm: teh object to use form communication
    :param recvQ: the queue for receiving
    :param DB: the database of users
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
        print(opcode)

