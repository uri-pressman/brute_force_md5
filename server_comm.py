import hashlib
import os
import socket
import threading

import select

import deffihelman, AESCLASS
from RSA import RSACipher


class ServerComm():
    def __init__(self, port, recvQ, worldObject):
        """
        establishes connection to the client
        :param port: the port
        :param recvQ: the queue to put media into
        """
        #initializing all params of comm object
        self.server = socket.socket()
        self.recvQ = recvQ
        # 1. Generate the key pair
        self.worldObject = worldObject

        # 2. Initialize the class with that key to enable encryption/decryption
        self.my_private_cipher = RSACipher()

        self.open_clients = {}
        #start the main loop thread
        threading.Thread(target = self._mainLoop, args=(port,)).start()

    def _mainLoop(self, port):
        """
        loop that collect media from user
        :param port: the port to listen to
        :return:
        """
        # connects to server
        self.server.bind(("0.0.0.0", port))
        self.server.listen(3)
        self.running = True

        while self.running:
            #collects all clients for sending and receiving

            rlist, wlist, xlist = select.select([self.server]+list(self.open_clients.keys()),self.open_clients.keys(), [], 0.01)
            #accepts all new clients
            for current_sock in rlist:
                if current_sock is self.server:
                    client, addr = self.server.accept()
                    #exchanges public keys
                    threading.Thread(target=self.exchangeKeys, args=(client, addr)).start()

                else:
                    try:
                        #receives the length of data and the data
                        data_len = current_sock.recv(4)
                        if data_len != 0:
                            data_len = int(data_len.decode().lstrip('0'))
                            print("len - ",data_len)
                            data = current_sock.recv(data_len)

                            #decrypting the msg with the current client key
                            decryptedData = self.open_clients[current_sock][1].decrypt(data)
                            print("data - ", decryptedData)
                        else:
                            decryptedData = ""
                    except Exception as e:
                        print(f"in main loop - {str(e)}")
                        decryptedData = ""
                    if decryptedData == "":
                        #closes the client if an error occurs
                        print("Client closed")
                        self._close_client(current_sock)

                    else:
                        #adds the data to the receiving queue
                        self.recvQ.put((self.open_clients[current_sock], decryptedData))

    def _close_client(self, client_soc):
        """
        closes the client sock
        :param client_soc: the client sock
        :return:
        """
        #checks if the client is in the dict of open clients

        if client_soc in self.open_clients.keys():
            #delets the client if exists and closes the socket
            #if world created closes all clients connected
            if self.worldObject.world_created:
                for player in self.worldObject.current_players.values():
                    ip = player["ipAndKey"]

                    current_soc = self._find_soc_by_ip(ip)
                    # if not the original one closing
                    if current_soc != client_soc:
                        self.send_msg(ip, "z")
                        current_soc.close()
                        del self.open_clients[current_soc]
                client_soc.close()
                del self.open_clients[client_soc]
                self.recvQ.put((None, "z"))
                self.closeServer()
                exit()

            else:
                print("deleted from open clients")
                del self.open_clients[client_soc]
                client_soc.close()

    def closeServer(self):
        self.server.close()

    def _find_soc_by_ip(self, ip):
        """
        finds the client corresponding to the given ip
        :param ip: the IP to check
        :return: the socket of the client
        """
        #initializing the socket object
        sock = None
        #starts search loop
        for client_sock in self.open_clients.keys():
            #if the ip of the current socket is the same returns that one | else return None
            if self.open_clients[client_sock] == ip:
                sock = client_sock
                break
        return sock

    def send_msg(self, ip, msg):
        """
        sends a msg to the client with encryption
        :param ip: the ip to send to
        :param msg: the msg to send
        :return:
        """
        print(msg, '+=====================')
        #seperats the ip and key
        ipClient = ip[0]
        key = ip[1]
        #finds the correct socket to send to
        sock = self._find_soc_by_ip(ip)
        if sock:
            #if its finds one sends the length of msg then the msg in encryption
            # print(f"sock - {sock}, msg - {msg}")
            encrypted_msg = key.encrypt(msg)

            msg_len = str(len(encrypted_msg)).zfill(4)
            try:
                # print("socket in send -", sock)
                sock.send(msg_len.encode())
                sock.send(encrypted_msg)
            except Exception as e:
                print(f"in send msg - {str(e)}")
                self._close_client(sock)
        print("sent================")

    def broadCast_msg(self, msg):
        """
        sends a msg to all the connected players
        :param msg: the msg to send
        :return:
        """
        for player in self.worldObject.current_players.values():
            full_ip = player["ipAndKey"]  # gets the (ip, RsaKey) tuple
            self.send_msg(full_ip, msg)

    def exchangeKeys(self, client, addr):
        """
        Server-side Phase 1: RSA Public Key Exchange.
        Establishes a secure 'handshake' by swapping RSA public keys with a
        newly connected client.
        """
        # 1. Send the Server's Public Key to the Client
        # We export the key to bytes so it can travel over the socket.
        server_pub_key_bytes = self.my_private_cipher.export_public_key()

        # Create a 5-digit header (e.g., '00450') so the client knows how many bytes to read.
        length_header = str(len(server_pub_key_bytes)).zfill(5)

        try:
            client.send(length_header.encode())  # Send the size header
            client.send(server_pub_key_bytes)  # Send the actual RSA public key

            # 2. Prepare to receive the Client's Public Key
            # The client will send back its own 5-digit length header.
            header = client.recv(5).decode()
        except Exception as e:
            print("Failed during RSA key transfer - ", str(e))

        if not header:
            return None

        # Convert header (e.g., '00256') into an integer (256)
        key_length = int(header.lstrip('0'))

        # Loop to ensure we receive every single byte of the client's public key
        client_key_bytes = b""
        while len(client_key_bytes) < key_length:
            try:
                chunk = client.recv(key_length - len(client_key_bytes))
                if not chunk:
                    break
                client_key_bytes += chunk
            except Exception as e:
                print(f"Failed during recv of client key - {str(e)}")

        # Import the raw bytes and turn them into a usable RSA Public Key object for this client
        client_public = self.my_private_cipher.import_key(client_key_bytes)

        # Now that we have their RSA key, move to Phase 2: Generating the Symmetrical (AES) key
        session_key = self.exchangeKeysAES(client, client_public)

        # Store the client's information (IP address and their specific AES key) in the server's memory
        self.open_clients[client] = [addr[0], session_key]

    def exchangeKeysAES(self, client, client_public):
        """
        Server-side Phase 2: Diffie-Hellman Key Exchange.
        Uses RSA encryption to safely agree on a shared secret without anyone
        sniffing the traffic knowing what it is.
        """
        print("Starting AES key generation...")

        # Initialize a new Diffie-Hellman (DH) mathematical pair
        Key = deffihelman.SimpleDH()
        my_dh_public = Key.get_public_key()

        client_dh_public = None
        try:
            # 1. Encrypt our DH Public Key using the CLIENT'S RSA public key.
            # This ensures ONLY that specific client can read our DH value.
            encrypted_my_dh = self.my_private_cipher.encrypt_data(str(my_dh_public), client_public)
            client.send(encrypted_my_dh)

            # 2. Receive the Client's DH Public Key.
            # It arrives encrypted with the Server's RSA public key; we decrypt it with our private key.
            encrypted_client_data = client.recv(1024)
            client_dh_public = int(self.my_private_cipher.decrypt_data(encrypted_client_data))

        except Exception as e:
            print("Error during DH exchange: ", str(e))

        if client_dh_public:
            # Step 3: The Magic of Diffie-Hellman
            # By combining our private part + their public part, both sides generate
            # the EXACT same secret number without ever sending the secret itself.
            sharedSecret = Key.get_shared_secret(client_dh_public)

            # Step 4: Create the final AES Cipher object
            # This will be used for all future fast, encrypted messaging.
            print("Symmetrical AES Key successfully created for client.")
            return AESCLASS.AESCipher(sharedSecret)

