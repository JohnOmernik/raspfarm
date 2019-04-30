#!/usr/bin/python3

#from cryptography.hazmat.primitives.asymmetric import padding
import sys
import os
import farmcrypto
def main():

    fc = farmcrypto.FarmCrypto()

    print("Hello")

    msg = b"Hello, my name is encdsaddasdasdsadasdasssssssssssssssssdadsafdsfafdsfasfdsafdsafdafdasfdsafdsafdsafafdafdasdasdasdasdsadas"

    encrypted_msg = fc.pubkey_srv_encrypt(msg)

    mynewsymkey = fc.gen_symkey()
    fc.add_symkey(mynewsymkey)
    sym_enc_msg = fc.sym_encrypt(msg)
    print("Sym Key Len: %s" % len(mynewsymkey))


    print("Message: %s" % msg)
    print("Message Length: %s" % len(msg))
    print("Encrypted Message Length: %s " % len(encrypted_msg))
    print("Sym Encrypted Message Length: %s " % len(sym_enc_msg))






if __name__ == "__main__":
    main()
