import socket
import threading

import deffihelman, AESCLASS
from RSA import RSACipher


class ClientComm():
    def __init__(self, serverIp, port, recvQ):
        """
        Builder of client communication with RSA support.
        """
        self.my_sock = socket.socket()
        self.recvQ = recvQ

        # 1. Generate the Client's RSA Key Pair (Private + Public)
        # This stays on the client and is used to DECRYPT
        # messages the server sends to YOU.
        self.symmetricalKey = None

        # 2. Initialize the class with that key to enable encryption/decryption
        self.my_private_cipher = RSACipher()
        self.server_public = None
        self.image_port = None
        # 2. This will eventually hold the SERVER'S public key
        # (Used to ENCRYPT messages you send to the server)


        # Start the communication thread
        threading.Thread(target=self._mainLoop, args=(serverIp, port,)).start()

    def _mainLoop(self, serverIp, port):
        """
        the main loop for collecting data from the server
        :param serverIp: the ip of the server
        :param port: the port of the server
        :return:
        """
        try:
            #tries connecting to server and switching keys
            self.my_sock.connect((serverIp,port))
            self.exchangeKeys()
        except Exception as e:
            print(f"in connect {str(e)}")
            exit("server is down - try later")
        print("client connected")
        while True:
            # receiving length then data and does all the decryption
            try:
                data_len = self.my_sock.recv(4).decode().lstrip('0')
                try:
                    data_len = int(data_len)
                except Exception as e:
                    data_len = 0
                    print(f"in len of data - {str(e)}")
                if data_len != 0:
                    data = self.my_sock.recv(data_len)
                    print(data_len)
                    data = self.symmetricalKey.decrypt(data)
                    print("data - ", data)
                else:
                    data = ""
            except Exception as e:
                print(f"in main loop - {str(e)}")
                data = ""
            if data == "":
                self.close_client()
            else:
                #adds data to the queue
                print("data from server - " , data)
                self.recvQ.put(data)


    def close_client(self):
        """
        closes the socket
        :return:
        """
        print("client disconnected")
        #closes the socket
        self.my_sock.close()
        exit("server is down - try later")

    def send_msg(self, msg):
        """
        sends msg to server
        :param msg: the msg to send
        :return:
        """
        #encryptes msg and saves the length
        print("msg - ", msg)
        encryptedMsg = self.symmetricalKey.encrypt(msg)
        msg_len = str(len(encryptedMsg)).zfill(4)
        try:
            #sends length then the msg
            self.my_sock.send(msg_len.encode())
            self.my_sock.send(encryptedMsg)
        except Exception as e:
            print(f"in send msg - {str(e)}")
            self.close_client()

    def exchangeKeys(self):
        """
        Step 1: RSA Public Key Exchange.
        This method swaps RSA public keys with the server so both parties
        can send encrypted messages that only the intended recipient can decrypt.
        """
        # Export our own public key into a byte format so it can be sent over the network
        my_public_key_bytes = self.my_private_cipher.export_public_key()

        try:
            # 2. Receive the Server's Public Key
            # The first 5 bytes represent the length of the incoming key (padded with zeros, e.g., '00450')
            header = self.my_sock.recv(5).decode().lstrip('0')
            server_key_length = int(header)

            # Loop until we have received the full length of the server's public key
            server_key_bytes = b""
            while len(server_key_bytes) < server_key_length:
                chunk = self.my_sock.recv(server_key_length - len(server_key_bytes))
                if not chunk:
                    break
                server_key_bytes += chunk

            # Convert the raw bytes from the server into a usable RSA Public Key object
            self.server_public = self.my_private_cipher.import_key(server_key_bytes)

            # 3. Send our Client Public Key to the Server
            # We create a 5-digit header (e.g., 450 bytes becomes '00450') to tell the server how much to read
            my_length_header = str(len(my_public_key_bytes)).zfill(5)
            self.my_sock.send(my_length_header.encode())  # Send the size header
            self.my_sock.send(my_public_key_bytes)  # Send the actual key

            print("RSA Key Exchange Finished")

        except Exception as e:
            print(f"RSA Key Exchange Error: {e}")

        # Move to the next phase: Establishing the Symmetrical (AES) key
        self.exchangeKeysAES()

    def exchangeKeysAES(self):
        """
        Step 2: Diffie-Hellman Key Exchange via RSA.
        We use the RSA keys we just swapped to securely share Diffie-Hellman values.
        This results in a 'Shared Secret' that both sides know, but no one on the outside can see.
        """
        # Initialize a new Diffie-Hellman key pair
        Key = deffihelman.SimpleDH()

        # Encrypt our DH Public Key using the SERVER'S RSA public key
        # Only the server (with its private key) can decrypt this.
        my_dh_public_encrypted = self.my_private_cipher.encrypt_data(str(Key.get_public_key()), self.server_public)

        server_dh_public = None
        try:
            # 1. Receive the Server's DH Public Key
            # Note: This arrives encrypted with our RSA public key.
            encrypted_server_data = self.my_sock.recv(1024)

            # Decrypt the server's DH value using our own RSA private key
            server_dh_public = int(self.my_private_cipher.decrypt_data(encrypted_server_data))

            # 2. Send our encrypted DH Public Key to the server
            self.my_sock.send(my_dh_public_encrypted)

        except Exception as e:
            print("Error in AES/DH key exchange: ", str(e))

        if server_dh_public:
            # Step 3: Generate the Shared Secret
            # This math combines our private DH part and the server's public DH part.
            # Both sides will arrive at the exact same number.
            sharedSecret = Key.get_shared_secret(server_dh_public)

            # Step 4: Initialize the Symmetrical Cipher (AES)
            # We now use that shared secret to create an AES object for fast, secure communication.
            self.symmetricalKey = AESCLASS.AESCipher(sharedSecret)
            print("Symmetrical AES Key Established.")