import base64
import os
from sys import platform
from shutil import copy2
from getpass import getpass

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def salt_gen():
    salt_new = os.urandom(16)
    with open(salt_path, "wb") as f:
        f.write(salt_new)

def key_write(key):
    with open(key_path, "wb") as f:     # wb = write bytes
        f.write(key)
    f.close()

def key_read():
    with open(key_path, "rb") as f:     # rb = read bytes
        key = f.read()
    f.close()
    return key

# If possible, return as few implementation detail as possible
def validate_key(key):
    with open(key_path, "rb") as f:     # rb = read bytes
        read_key = f.read()
    f.close()
    return read_key == key

def key_random():
    key = Fernet.generate_key()
    return key

def pw_to_key(pw_for_keygen):
    password = pw_for_keygen.encode()
    with open(salt_path, "rb") as f:
        salt = f.read()
    f.close()
    # salt = b'u\xbc\x17c\x8b\xff_\xc1\xc2go"\xa7\xa3}t'
    kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=101524,
            backend=default_backend()
        )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key

def file_encrypt(file_in, file_out, key, opt):
    with open(file_in, "rb") as f:   # Open the file to encrypt
        data = f.read()
    fernet = Fernet(key)
    if opt == "en":
        output = fernet.encrypt(data)
    elif opt == "de":
        output = fernet.decrypt(data)
    with open(file_out, "wb") as f: # Write the encrypted file
        f.write(output)

def str_encrypt(str_in, key, opt):
    fernet = Fernet(key)
    if opt == "en":
        str_out = fernet.encrypt(str_in.encode())
    elif opt == "de":
        str_out = fernet.decrypt(str_in).decode()
    return str_out

def login():
    while True:
        # pw_to_key is fine
        # key_from_pw: key_from_X, key_from_Y
        key = pw_to_key(getpass("Enter Master Password to continue: "))
        if validate_key(key):
            print("Master Password correct!")
            break
        else:
            print("Incorrect password!")
            continue

def new_master_pw():
    key = pw_to_key(input("Create a new Master Password: "))
    key_write(key)

def change_master_pw():
    key = pw_to_key(getpass("Enter a new Master Password: "))
    key_write(key)

if platform.startswith("linux"):
    key_path = os.path.expanduser("~/.keys/pwmngr.key")
elif platform.startswith("win32"):
    key_path = os.path.abspath(" /../../.keys/pwmngr.key")
else:
    key_path = os.path.expanduser("~/.keys/pwmngr.key")
salt_path = key_path.replace("pwmngr.key", "pwmngr.salt")
