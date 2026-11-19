
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import hashlib
import queue

from serverComm import ServerComm
from common.settings import BLOCK_LENGTH, MD5_TARGET
from time import perf_counter
# ===========================================================================
# Entry point
# ===========================================================================

def main():
    """
    :return: none
    """
    port = 9876
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
            pass

    recvQ = queue.Queue()
    comm = ServerComm(port, recvQ, debug)
    if debug:
        print(f"Listening on port {port}", flush=True)

    numbers = iter(range(1000000000, 10000000000, BLOCK_LENGTH))
    assignments = {}
    clients_connected = []
    found = False
    started_at = None
    try:
        while not found:
            sock, ip, data = recvQ.get()
            if sock not in clients_connected:
                clients_connected.append(sock)
            if started_at is None:
                started_at = perf_counter()
            if data is None or (data == '0' and sock in assignments):
                assignments.pop(sock, None)
                if not found:
                    number = next(numbers, None)
                else:
                    number = None
                if number is None:
                    comm.send_msg_by_sock(sock, 'DONE')
                else:
                    assignments[sock] = number
                    comm.send_msg_by_sock(sock, str(number // BLOCK_LENGTH))
                    if debug:
                        print(f"{ip}: sent {number // BLOCK_LENGTH}", flush=True)
            elif sock in assignments:
                number = assignments[sock]
                valid = (
                    len(data) == 10
                    and data.isascii()
                    and data.isdigit()
                    and number <= int(data) < number + BLOCK_LENGTH
                    and hashlib.md5(data.encode()).hexdigest().upper() == MD5_TARGET
                )
                if valid:
                    found = True
                    for client_sock in assignments:
                        comm.send_msg_by_sock(client_sock, 'DONE')
                    assignments.clear()
                else:
                    if debug:
                        print(f"{ip}: invalid answer {data}", flush=True)
                    assignments.pop(sock, None)
                    comm.close_client_by_sock(sock)
            if found and started_at is not None:
                elapsed = perf_counter() - started_at
                print(f"Time elapsed: {elapsed:.2f} seconds", flush=True)
                print(f"{ip}: answer is {data}", flush=True)
                print(f"Clients connected: {len(clients_connected)}", flush=True)
    except KeyboardInterrupt:
        if debug:
            print("\nServer stopped.", flush=True)


if __name__ == '__main__':
    main()
