#!/usr/bin/python3

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.fernet import Fernet

import sys
import os


def main():
    print("FarmCrypto Testing")

class FarmCrypto:
    KEYS_DIR =  "./keys"
    PUB_DIR = KEYS_DIR + "/public"
    PVT_DIR = KEYS_DIR + "/private"
    PUB_KEYFILE = PUB_DIR + "/mypub.pem"
    PVT_KEYFILE = PVT_DIR + "/mypvt.pem"
    SRV_PUB_KEYFILE = PUB_DIR + "/srvpub.pem"
    KEYSIZE = 1536

    public_key = None
    private_key = None
    server_public_key = None
    sym_keys = []

    def __init__(self):

        self.chkdirs()
        self.loadmykeys()
        self.loadsrvkeys()

    def add_symkey(self, newkey):
        self.sym_keys.insert(0,newkey)

    def gen_symkey(self):
        mykey = Fernet.generate_key()
        return mykey

    def sym_encrypt(self, msg):
        # We encrypt with the first item in the array
        if len(self.sym_keys) == 0:
            print("No Key")
        f = Fernet(self.sym_keys[0])
        return f.encrypt(msg)

    def pubkey_srv_encrypt(self, msg):
        print("Encrypting!")
        encrypted_msg = self.server_public_key.encrypt(msg, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),algorithm=hashes.SHA256(),label=None))
        return encrypted_msg

    def prvkey_decrypt(self, encmsg):
        msg = self.private_key.decrypt(encmsg, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),algorithm=hashes.SHA256(),label=None))
        return msg

    def chkdirs(self):
        dirs = [self.KEYS_DIR, self.PUB_DIR, self.PVT_DIR]
        for dir in dirs:
            if not os.path.isdir(dir):
                print("Directory of %s does not exist: Creating" % dir)
                os.mkdir(dir)
            else:
                print("Directory %s exists" % dir)

    def loadsrvkeys(self):
        if os.path.exists(self.SRV_PUB_KEYFILE):
            with open(self.SRV_PUB_KEYFILE, "rb") as key_file:
                my_server_public_key = serialization.load_pem_public_key(key_file.read(),backend=default_backend())
                self.server_public_key = my_server_public_key
        else:
            print("WARNING - Server Public Key file not found at %s Stuff probably won't work" % self.SRV_PUB_KEYFILE)



    def loadmykeys(self):
        if not os.path.exists(self.PVT_KEYFILE) and not os.path.exists(self.PUB_KEYFILE):
            print("Public and Private Key pairs do not exist. Generating")
            my_private_key = rsa.generate_private_key(public_exponent=65537, key_size=self.KEYSIZE, backend=default_backend())
            my_public_key = my_private_key.public_key()

            my_private_pem = my_private_key.private_bytes(encoding=serialization.Encoding.PEM,format=serialization.PrivateFormat.PKCS8,encryption_algorithm=serialization.NoEncryption())
            my_public_pem = my_public_key.public_bytes(encoding=serialization.Encoding.PEM,format=serialization.PublicFormat.SubjectPublicKeyInfo)

            with open(self.PVT_KEYFILE, 'wb') as f:
                f.write(my_private_pem)
            f.close()
            with open(self.PUB_KEYFILE, 'wb') as f:
                f.write(my_public_pem)
            f.close()
        elif os.path.exists(self.PVT_KEYFILE) and os.path.exists(self.PUB_KEYFILE):
            with open(self.PVT_KEYFILE, "rb") as key_file:
                my_private_key = serialization.load_pem_private_key(key_file.read(),password=None,backend=default_backend())
            with open(self.PUB_KEYFILE, "rb") as key_file:
                my_public_key = serialization.load_pem_public_key(key_file.read(),backend=default_backend())
        elif not os.path.exists(self.PVT_KEYFILE) or not os.path.exists(self.PUB_KEYFILE):
            print("Either the public or private key exists, and the opposite does not. We exit here for you to fix")
            sys.exit(1)
        self.public_key = my_public_key
        self.private_key = my_private_key



if __name__ == "__main__":
    main()
