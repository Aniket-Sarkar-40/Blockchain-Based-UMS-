import rsa
from cryptography.fernet import Fernet
import json
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
import getKey

def encrypt(messageObject, sender_public_key):
    message = json.dumps(messageObject)
    
    key = Fernet.generate_key()

    f_obj = Fernet(key)
    encryption_message1 = f_obj.encrypt(message.encode())
    # Encrypt the Fernet key using RSA public key
    encrypted_fernet_key = sender_public_key.encrypt(
        key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Now 'encrypted_fernet_key' contains the encrypted Fernet key
    # sending data
    data = {
        "key" : encrypted_fernet_key,
        "encryptedMsg" : encryption_message1
    }
    return data

def decrypt(data, sender_private_key):
    # data = encrypt(messageObject)
    # Decrypt the encrypted data using sender's private key
    decrypted_key = sender_private_key.decrypt(
        data["key"],
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # print("Decrypted Key:", decrypted_key)

    f1_obj = Fernet(decrypted_key)
    decrypted_msg = f1_obj.decrypt(data["encryptedMsg"])
    output = json.loads(decrypted_msg.decode())
    return output

messageObject = {
    "id" : 1,
    "message" : "hello i am aniket",
}

reciever_public_key = getKey.sender_public_key
reciever_private_key = getKey.sender_private_key

output = decrypt(encrypt(messageObject, reciever_public_key), reciever_private_key)
print("Decripted" , output["message"])

# proof of authority - papers , r and d, drawback
