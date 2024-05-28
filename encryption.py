import rsa
from cryptography.fernet import Fernet
import json
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
import getKey
from cryptography.hazmat.backends import default_backend


def encrypt(messageObject, public_key_bytes):
    sender_public_key = serialization.load_der_public_key(
        public_key_bytes, backend=default_backend()
    )
    print("after public key: ", sender_public_key.public_numbers())
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
            label=None,
        ),
    )

    # Now 'encrypted_fernet_key' contains the encrypted Fernet key
    # sending data
    data = {"key": encrypted_fernet_key, "encryptedMsg": encryption_message1}
    return data


def decrypt(data, private_key_bytes):
    # data = encrypt(messageObject)
    # Decrypt the encrypted data using sender's private key
    sender_private_key = serialization.load_der_private_key(
        private_key_bytes,
        password=None,  # Passphrase or encryption key used during encryption
        backend=default_backend(),
    )
    print(data["key"])
    print(sender_private_key)
    decrypted_key = sender_private_key.decrypt(
        data["key"],
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    # print("Decrypted Key:", decrypted_key)

    f1_obj = Fernet(decrypted_key)
    decrypted_msg = f1_obj.decrypt(data["encryptedMsg"])
    output = json.loads(decrypted_msg.decode())
    return output


messageObject = {
    "id": 1,
    "message": "hello i am aniket",
}

reciever_public_key = getKey.public_key
reciever_private_key = getKey.private_key

print("public key:1st-", reciever_public_key.public_numbers())

public_key_bytes = reciever_public_key.public_bytes(
    encoding=serialization.Encoding.DER,  # Use DER or another appropriate format
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
)

private_key_bytes = reciever_private_key.private_bytes(
    encoding=serialization.Encoding.DER,  # Use DER or another appropriate format
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
)

encrypted_msg = encrypt(messageObject, public_key_bytes)
# print("Encrypted Message - ", type(encrypted_msg["key"]))
output = decrypt(encrypted_msg, private_key_bytes)
print("Decripted", output["message"])

# proof of authority - papers , r and d, drawback
