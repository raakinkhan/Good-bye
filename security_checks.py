import os
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from io import BytesIO


def secure_shred(file_path, passes=10):
    if not os.path.exists(file_path):
        pass

    file_size = os.path.getsize(file_path)

    try:
        with open(file_path, "r+b") as file:
            for _ in range(passes):
                file.seek(0)
                file.write(os.urandom(file_size))
                file.flush()
        os.remove(file_path)
        pass
    except:
        pass


def key_generator(text, salt_random=True, salt_=b""):
    if salt_random:
        salt = os.urandom(16)
    else:
        salt = salt_
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=500,
    )
    key = kdf.derive(text.encode())
    return (key, salt)


def AES_enc(file_path, password):
    try:
        file_path_ = os.path.basename(file_path)
        print(file_path_)
        auth = key_generator(text=password)
        nonce = os.urandom(16)
        ciper = Cipher(algorithms.AES(auth[0]), modes.CTR(nonce))
        encrypter = ciper.encryptor()
        chunk_size = 8 * 1024 * 1024
        try:
            with open(file_path, "rb") as f_in, open("encrypted main/"+file_path_[:-4]+".enc", "wb") as f_out:
                while chunk := f_in.read(chunk_size):
                    cipertext = encrypter.update(chunk)
                    f_out.write(cipertext)
                f_out.write(encrypter.finalize())
            with open("extra info/"+file_path_[:-4]+".bin", "wb") as f:
                f.write(auth[1] + nonce)
        except:
            secure_shred(file_path="encrypted main/" + file_path_[:-4] + ".enc")
            secure_shred(file_path="extra info/"+file_path_[:-4]+".bin")
        secure_shred(file_path=file_path)
    except:
        secure_shred(file_path=file_path)




def AES_dec(file_path, password, info_dir="extra info"):
    filename = os.path.basename(file_path)
    info_path = os.path.join(info_dir, filename[:-4] + ".bin")
    if not os.path.exists(info_path):
        raise FileNotFoundError(f"Info file {info_path} not found")

    with open(info_path, "rb") as f:
        key_info = f.read()
        salt = key_info[:16]
        nonce = key_info[16:]

    auth = key_generator(text=password, salt_random=False, salt_=salt)
    cipher = Cipher(algorithms.AES(auth[0]), modes.CTR(nonce))
    decrypter = cipher.decryptor()

    chunk_size = 8 * 1024 * 1024
    decrypted_buffer = BytesIO()

    with open(file_path, "rb") as f_in:
        while chunk := f_in.read(chunk_size):
            plaintext = decrypter.update(chunk)
            decrypted_buffer.write(plaintext)
        decrypted_buffer.write(decrypter.finalize())

    decrypted_buffer.seek(0)
    return decrypted_buffer



