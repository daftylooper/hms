from Crypto.Cipher import AES
from hashlib import sha256
from Crypto.Util.Padding import pad, unpad

class CryptUtils:
    def __init__(self, key: str):
        # Generate a 32-byte key from the provided key using SHA-256
        self.key = sha256(key.encode()).digest()
        self.iv = b'1234567890123456'  # You can generate this randomly if needed

    def encrypt(self, value: str):
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        encrypted = cipher.encrypt(pad(value.encode(), AES.block_size))
        return encrypted.hex()

    def decrypt(self, value: str):
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        decrypted = unpad(cipher.decrypt(bytes.fromhex(value)), AES.block_size)
        return decrypted.decode()
