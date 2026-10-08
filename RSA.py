
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_OAEP as PKCS





class RSACipher:
    def __init__(self, bits=2048):
        """
        Initialize with an existing RSA key object.
        If none is provided, it can be used as a generator.
        """
        # self.others_public = None
        self.private_key = RSA.generate(bits)
        self.public_key = self.private_key.public_key()
        self.cipher = None
        if self.private_key:
            self.cipher = PKCS.new(self.private_key)


    def export_public_key(self):
        """Converts the public key to PEM string for sending over sockets."""
        return self.public_key.export_key()

    def import_key(self, key_bytes):
        """Client uses this to turn received bytes back into a Key Object."""
        # print(RSA.import_key(key_bytes), "key bytes", key_bytes)
        return RSA.import_key(key_bytes)


    def encrypt_data(self, data, public_key):
        """
        Correctly handles both strings (messages) and raw bytes (images).
        """
        # 1. Ensure we are working with BYTES before slicing
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        else:
            data_bytes = data

        # For 2048-bit RSA with OAEP, 190 bytes is the max safe chunk size
        chunk_size = 190
        encrypted_buffer = []
        cipher = PKCS.new(public_key)
        print("type of data_bytes -" ,type(data_bytes))
        # 2. Loop through the byte-array
        for i in range(0, len(data_bytes), chunk_size):
            chunk = data_bytes[i:i + chunk_size]

            # 3. Encrypt the chunk and append to list
            try:
                encrypted_buffer.append(cipher.encrypt(chunk))
            except Exception as e:
                print(f"Encryption failed at chunk {i}: {e}")
                raise

        # 4. Join the 256-byte blocks together
        return b"".join(encrypted_buffer)

    def decrypt_data(self, encrypted_data):
        """
        Decrypts RSA-encrypted data in 256-byte blocks.
        Works for both image bytes and string messages.
        """
        # RSA 2048 ciphertext blocks are always exactly 256 bytes
        block_size = 256
        decrypted_buffer = []

        # 1. Validation: Ensure we actually have data and it's in full blocks
        if not encrypted_data or len(encrypted_data) % block_size != 0:
            print(f"Error: Encrypted data length ({len(encrypted_data)}) is not a multiple of {block_size}")
            return b""

        try:
            for i in range(0, len(encrypted_data), block_size):
                block = encrypted_data[i:i + block_size]

                # 2. Decrypt the block
                decrypted_chunk = self.cipher.decrypt(block)
                decrypted_buffer.append(decrypted_chunk)

        except Exception as e:
            print(f"Decryption failed: {e}")
            return b""

        # 3. Join into a single byte-string
        return b"".join(decrypted_buffer)


if __name__ == "__main__":


    # --- 1. SETUP (Alice) ---
    print("--- ALICE'S SIDE ---")
    # Alice generates her private key (which stays on her machine)
    # alice_private_key = RSACipher.generate_new_pair()
    alice_cipher_instance = RSACipher()

    # Alice exports her Public Key to give to Bob
    public_key_to_send = alice_cipher_instance.export_public_key()
    print(f"Alice: 'Here is my public key, Bob: {public_key_to_send[:40].decode()}...'")

    # --- 2. ENCRYPTION (Bob) ---
    print("\n--- BOB'S SIDE ---")
    # Bob receives the bytes and imports them into his own RSACipher instance
    # bob_imported_key = RSACipher.import_key(public_key_to_send)
    bob_cipher_instance = RSACipher()

    secret_message = "The eagle lands at midnight."
    print(f"Bob: Encrypting message: '{secret_message}'")

    ciphertext = bob_cipher_instance.encrypt_data(secret_message)
    print(f"Bob: Sending encrypted bytes to Alice...")

    # --- 3. DECRYPTION (Alice) ---
    print("\n--- ALICE'S SIDE AGAIN ---")
    # Alice receives the ciphertext and uses her private instance to decrypt
    decrypted_bytes = alice_cipher_instance.decrypt_data(ciphertext)
    decrypted_message = decrypted_bytes.decode('utf-8')

    print(f"Alice: Decrypted the message: '{decrypted_message}'")

    # Final Check
    if decrypted_message == secret_message:
        print("\nSuccess: The secure exchange is complete!")