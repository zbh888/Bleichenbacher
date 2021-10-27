# Bleichenbacher 

Implementation of [Chosen ciphertext attacks against protocols based on the RSA encryption standard PKCS #1](https://link.springer.com/chapter/10.1007/BFb0055716)

# Running Description

## 1. Run the server

`python3 ./Server/server.py -d ../Test/t1/decryption_key.txt -n ../Test/t1/modulus.txt`

This brings up a HTTP server at `127.0.0.1:8080` that you will use as your oracle for the attack.

## 2. Run the attack

`python3 bleichenbacher.py -c ./Test/t1/cipher.txt -e ./Test/t1/encryption_key.txt -n ./Test/t1/modulus.txt`

