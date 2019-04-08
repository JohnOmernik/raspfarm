#!/usr/bin/python3

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import sys
import os

keysdir =  "./keys"
pubdir = keysdir + "/public"
pvtdir = keysdir + "/private"
pubkey = pubdir + "/mypub.pem"
pvtkey = pvtdir + "/mypvt.pem"
srvkey = pubdir + "/srvpuv.pem"

public_key = ""
private_key = ""
server_public_key = ""
def main():
    print("Hello")
    chkdirs()
    loadkeys()



def chkdirs():

    dirs = [keysdir, pubdir, pvtdir]

    for dir in dirs:
        if not os.path.isdir(dir):
            print("Directory of %s does not exist: Creating" % dir)
            os.mkdir(dir)
        else:
            print("Directory %s exists" % dir)

def loadkeys():
    global public_key
    global private_key
    global server_public_key

    if not os.path.exists(pvtkey) and not os.path.exists(pubkey):
        print("Public and Private Key pairs do not exist. Generating")
        my_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
        my_public_key = my_private_key.public_key()

        my_private_pem = my_private_key.private_bytes(encoding=serialization.Encoding.PEM,format=serialization.PrivateFormat.PKCS8,encryption_algorithm=serialization.NoEncryption())
        my_public_pem = my_public_key.public_bytes(encoding=serialization.Encoding.PEM,format=serialization.PublicFormat.SubjectPublicKeyInfo)

        with open(pvtkey, 'wb') as f:
            f.write(my_private_pem)
        f.close()
        with open(pubkey, 'wb') as f:
            f.write(my_public_pem)
        f.close()
    elif os.path.exists(pvtkey) and os.path.exists(pubkey):
        with open(pvtkey, "rb") as key_file:
            my_private_key = serialization.load_pem_private_key(key_file.read(),password=None,backend=default_backend())
        with open(pubkey, "rb") as key_file:
            my_public_key = serialization.load_pem_public_key(key_file.read(),backend=default_backend())
    elif not os.path.exists(pvtkey) or not os.path.exists(pubkey):
        print("Either the public or private key exists, and the opposite does not. We exit here for you to fix")
        sys.exit(1)
    public_key = my_public_key
    private_key = my_private_key
    if os.path.exists(srvkey):
        with open(srvkey, "rb") as key_file:
            my_server_public_key = serialization.load_pem_public_key(key_file.read(),backend=default_backend())
            server_public_key = my_server_public_key
    else:
        print("WARNING - Server Public Key file not found at %s Stuff probably won't work" % srvkey)




if __name__ == "__main__":
    main()
