import queue
import threading
import hashlib
from client_comm import ClientComm
import os


def finder(ip, port, thead_id):
    """

    :param ip: ip of the host
    :param port: port to connect to
    :param thead_id: the ID of this worker
    :return:
    """

    recvQ = queue.Queue
    comm = ClientComm(ip, port, recvQ)
    hash = recvQ.get
    chunk = str(recvQ.get)

    for n in range(int(chunk)):

        digest = hashlib.md5(str(n).encode("utf-8")).hexdigest()
        if digest == hash:
            comm.send_msg(f"1${n}")
        else:
            comm.send_msg(0)





if __name__ == '__main__':
    # all the games queues
    recvQ = queue.Queue()

    logical_cores = os.cpu_count()
    print("Logical cores:", logical_cores)

    # establishes connection to server and starts queue for server msgs
    comm = ClientComm("127.0.0.1", 1001, recvQ)
    threading.Thread(target=handle_recv_msgs, args=(recvQ, ), daemon=True).start()




