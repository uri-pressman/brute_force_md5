
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import hashlib
import queue

from clientComm import ClientComm
from common.settings import BLOCK_LENGTH, MD5_TARGET
from multiprocessing import Process, Queue

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 9876


# ===========================================================================
# Main
# ===========================================================================

def worker(host, port, thread_id, debug):
    """
    search assigned batches and report a matching input or zero
    :param host: server ip
    :param port: server port
    :param thread_id: id of this thread
    :return: none
    """
    recvQ = queue.Queue()
    comm = ClientComm(host, port, recvQ, debug)
    numberS = str(recvQ.get())
    while numberS != 'DONE':
        if debug:
            print(numberS, flush=True)
        answer = '0'
        suffix_width = len(str(BLOCK_LENGTH - 1))
        for i in range(BLOCK_LENGTH):
            candidate = numberS + f"{i:0{suffix_width}d}"
            md5_hash = hashlib.md5(candidate.encode()).hexdigest().upper()
            if md5_hash == MD5_TARGET:
                answer = candidate
                break
        comm.send_msg(answer)
        numberS = str(recvQ.get())


def main():
    """
    run the client game loop, connect to the server 
    :return: none
    """
    host = DEFAULT_HOST
    port = DEFAULT_PORT
    debug = False
    for arg in sys.argv[1:]:
        if arg == '-debug':
            debug = True
            continue
        try:
            v = int(arg)
            if v > 20:
                port = v
        except ValueError:
            host = arg

    n = os.cpu_count() or 1
    if debug:
        print(f"Starting {n} worker threads to connect to {host}:{port}", flush=True)
    results = Queue()
    processes = []
    for worker_id in range(n):
        process = Process(target=worker, args=(host, port, worker_id, debug))
        process.start()
        processes.append(process)

    for process in processes:
        process.join()

    sys.exit()


if __name__ == '__main__':
    main()
