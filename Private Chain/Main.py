from flask import Flask, request
import flask
import json
from Private_Blockchain import PrivateBlockchain
app = Flask(__name__)
import requests


blockchain = PrivateBlockchain()

mapping = {
    "publicChainNode" : 5001,
}

@app.route("/")
def home():
    show_blocks = blockchain.show_blocks()
    blocks_dict = [block.to_dict() for block in show_blocks]
    return flask.jsonify({
        "message": "Blockchain with PoA",
        "Blockchain": blocks_dict
    })

# validators get permission to join the network from project Leadership team
# by submitting required documents.


@app.route("/register/validator", methods=['POST'])
def register_validator():
    # payload should have id key
    payload = request.get_json(force=True)
    if not payload['id']:
        return flask.jsonify({
            "message": "validator id is missing ...."
        })
    blockchain.add_validator(payload)
    return flask.jsonify({
        "message": "validator added successfully.."
    })


@app.route("/register/peer", methods=["POST"])
def register_peer():
    # payload should contain public_key and amount
    payload = request.get_json(force=True)
    if not payload['public_key']:
        return flask.jsonify({
            "message": "peer public key is missing ...."
        })
    blockchain.add_peer(payload)
    return flask.jsonify({
        "message": "peer added successfully.."
    })


@app.route("/view_all_peers")
def view_all_peers():
    peers = blockchain.view_all_peers()
    return flask.jsonify({
        "peers": peers
    })


@app.route("/view_all_validators")
def view_all_validators():
    validators = blockchain.view_all_validators()
    return flask.jsonify({
        "validators": validators
    })


@app.route("/view_transaction_pool")
def view_transaction_pool():
    transaction_pool = blockchain.view_all_transactions()
    return flask.jsonify({
        "transaction_pool": transaction_pool
    })


@app.route("/add_transaction", methods=['POST'])
def add_transaction():
    # transaction should contain sender public key , receiver public key and amount
    transaction = request.get_json(force=True)
    if not transaction['sender'] or not transaction['receiver']:
        return flask.jsonify({
            "message": "Transaction format invalid...transaction should contain sender public key , receiver public key ."
        })
    blockchain.add_transaction(transaction)
    return flask.jsonify({
        "message": "transaction added successfully."
    })

# validate transactions and add new blocks


@app.route("/mine")
def mine():
    if not blockchain.mine():
        return flask.jsonify({
            "message": "No Validators ...."
        })
    return flask.jsonify({
        "message": "mining successfull."
    })

# Todo : create a mapping table for which node is connetced to which node and later on also the public key also

@app.route("/sendDataToPublicChain", methods=["POST"])
def sendDataToPublicChain():
    data = request.get_json()
    if not data:
        return flask.jsonify({
            "message": "No data provided"
        })
    validators = blockchain.view_all_validators()
    sender_id = data.get("sender_id")
    sender_id_found = False

    for validator in validators:
        if validator.get("id") == sender_id:
            sender_id_found = True
            break

    if not sender_id_found:
        return flask.jsonify({
            "message": f"sender_id '{sender_id}' is not in the list of validators"
        })

    
    url = "http://127.0.0.1:{0}/newPrivateBlockTransaction".format(mapping.get("publicChainNode"))

    json_data = json.dumps(data, default=str, sort_keys=True)
    
    requests.post(url, json=json_data)

    return flask.jsonify({
        "message": "Transaction successfull."
    })


if __name__ == '__main__':
    app.run(host="0.0.0.0", port="8000", debug=True)
