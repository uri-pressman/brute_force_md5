import queue
import threading

from client_comm import ClientComm


def handle_recv_msgs(recvQueue):
    """
    handles all the msg from the server and calls the correct command
    :param recvQueue: the queue to get the params and opcode form communication

    :return:
    """
    while True:
        data = recvQueue.get()





if __name__ == '__main__':
    # all the games queues
    recvQ = queue.Queue()


    # establishes connection to server and starts queue for server msgs
    comm = ClientComm("127.0.0.1", 1001, recvQ)
    threading.Thread(target=handle_recv_msgs, args=(recvQ, ), daemon=True).start()