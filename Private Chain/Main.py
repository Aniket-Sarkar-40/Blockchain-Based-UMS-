from flask import Flask, request
import flask
import json
from Private_Blockchain import PrivateBlockchain
from flask_pymongo import PyMongo
import sys
from cryptography.fernet import Fernet
import json
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

app = Flask(__name__)
import requests


blockchain = PrivateBlockchain()


app.config["MONGO_URI"] = (
    "mongodb+srv://aniket15970:3Zmg1JzbEZWO3Gjw@esm.nrjexdy.mongodb.net/ums?retryWrites=true&w=majority"
)
mongo = PyMongo(app)
db = mongo.db


def encrypt(messageObject, public_key_str):
    public_key_bytes = public_key_str.encode()
    sender_public_key = serialization.load_pem_public_key(
        public_key_bytes, backend=default_backend()
    )
    print("Public key: ", sender_public_key.public_numbers())
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
    print("key:1 -", encrypted_fernet_key)
    data = {"key": encrypted_fernet_key, "encryptedMsg": encryption_message1}
    return data


@app.route("/")
def home():
    show_blocks = blockchain.show_blocks()
    blocks_dict = [block.to_dict() for block in show_blocks]
    return flask.jsonify({"message": "Blockchain with PoA", "Blockchain": blocks_dict})


# validators get permission to join the network from project Leadership team
# by submitting required documents.


@app.route("/register/validator", methods=["POST"])
def register_validator():
    # payload should have id key
    payload = request.get_json(force=True)
    if not payload["id"]:
        return flask.jsonify({"message": "validator id is missing ...."})
    blockchain.add_validator(payload)
    return flask.jsonify({"message": "validator added successfully.."})


@app.route("/register/peer", methods=["POST"])
def register_peer():
    # payload should contain public_key and amount
    payload = request.get_json(force=True)
    if not payload["public_key"]:
        return flask.jsonify({"message": "peer public key is missing ...."})
    blockchain.add_peer(payload)
    return flask.jsonify({"message": "peer added successfully.."})


@app.route("/view_all_peers")
def view_all_peers():
    peers = blockchain.view_all_peers()
    return flask.jsonify({"peers": peers})


@app.route("/view_all_validators")
def view_all_validators():
    validators = blockchain.view_all_validators()
    return flask.jsonify({"validators": validators})


@app.route("/view_transaction_pool")
def view_transaction_pool():
    transaction_pool = blockchain.view_all_transactions()
    return flask.jsonify({"transaction_pool": transaction_pool})


@app.route("/add_transaction", methods=["POST"])
def add_transaction():
    # transaction should contain sender public key , receiver public key and amount
    transaction = request.get_json(force=True)
    if not transaction["sender"] or not transaction["receiver"]:
        return flask.jsonify(
            {
                "message": "Transaction format invalid...transaction should contain sender public key , receiver public key ."
            }
        )
    blockchain.add_transaction(transaction)
    return flask.jsonify({"message": "transaction added successfully."})


# validate transactions and add new blocks


@app.route("/mine")
def mine():
    if not blockchain.mine():
        return flask.jsonify({"message": "No Validators ...."})
    return flask.jsonify({"message": "mining successfull."})


@app.route("/sendDataToPublicChain", methods=["POST"])
def sendDataToPublicChain():
    data = request.get_json()
    port = request.environ.get("SERVER_PORT")
    mapping = db.Public_Private_Mapping.find_one({"Private_Address_Port": int(port)})

    if not data:
        return flask.jsonify({"message": "No data provided"})
    validators = blockchain.view_all_validators()
    sender_id = data.get("sender_id")
    sender_id_found = False
    public_key_bytes = mapping.get("Public_Key_Bytes")
    encrypted_msg = encrypt(data, public_key_bytes)

    for validator in validators:
        if validator.get("id") == sender_id:
            sender_id_found = True
            break

    if not sender_id_found:
        return flask.jsonify(
            {"message": f"sender_id '{sender_id}' is not in the list of validators"}
        )

    url = "{0}/newPrivateBlockTransaction".format(mapping.get("Public_Address"))

    json_data = json.dumps(encrypted_msg, default=str, sort_keys=True)

    requests.post(url, json=json_data)

    return flask.jsonify({"message": "Transaction successfull."})


if __name__ == "__main__":
    port = int(sys.argv[1])
    app.run(host="0.0.0.0", port=port, debug=True)
