from hashlib import sha512
import json
import sys
from bson import ObjectId
import time
import random
from flask_pymongo import PyMongo

from flask import Flask, request, jsonify
import requests
from urllib.parse import urlparse


# Flask web application
# create Flask web application
app = Flask(__name__)

app.config["MONGO_URI"] = (
    "mongodb+srv://aniket15970:3Zmg1JzbEZWO3Gjw@esm.nrjexdy.mongodb.net/ums?retryWrites=true&w=majority"
)
mongo = PyMongo(app)
db = mongo.db


# A class that represents a Block, whcih stores one or more
# pieces of data, in the immutable Blockchain
class Block:
    # One or more piece of data(author, contetn of post and timestamp) will be stored in a block
    # The blocks containing the data are generated frequently and added to the blockchain. These block has unique ID.
    def __init__(self, index, transactions, timestamp, previous_hash):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.compute_hash()

    # A function that creates the hash of the block content
    def compute_hash(self):
        block_string = (
            str(self.index)
            + str(self.transactions)
            + str(self.previous_hash)
            + str(self.nonce)
        )
        # block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha512(block_string.encode()).hexdigest()


# End of Block class


def unconfirmed_transactions():
    all_pending_txn = db.pendingTransaction.find()
    pendingTxn = []

    for data in all_pending_txn:

        del data["_id"]
        pendingTxn.append(data)

    return pendingTxn


# A class that represents an immutable list of Block objects are chained together by hashes, a Blockchain.
class Blockchain:
    # Difficult of PoW algorithm
    difficulty = 2

    # One or more blocks will be stored and chained toghether on the Blockchain, starting by the genisi block
    def __init__(self):
        # self.unconfirmed_transactions = self.unconfirmed_transactions()  # These are pieces of data that are not yet added to the Blockchain.
        self.chain = []  # The immutable list that represets the actual Blockchain
        self.peers = set()
        self.create_genesis_block()

    # Generates genesis block and appends it to the Blockchain
    # The Block has index o, previous_hash of 0 and a valid hash
    def create_genesis_block(self):
        genesis_block = Block(0, [], time.time(), "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)
        self.peers.add("127.0.0.1:5000")

    # Verifed block can be added to the chain, add it and return True or False
    def add_block(self, block, proof):
        previous_hash = self.last_block.hash
        # Verify that the prvious_hash field of the block to be added points to the hash of the latest block
        # and tjhat the PoW that is provided is correct
        # print(self.is_valid_proof(block, proof))
        if previous_hash != block.previous_hash or not self.is_valid_proof(
            block, proof
        ):
            return False
        # Add new block to the chain after verification
        block.hash = proof
        self.chain.append(block)
        return True

    def register_node(self, address):
        parsed_url = urlparse(address)
        self.peers.add(parsed_url.netloc)

    # Serve as interface to add the transactions to the blockchain by adding them
    # and then figuring out the PoW
    def mine(self):
        # if uncofirmed_transactions is empyt, no mining to be done
        pending_txns = unconfirmed_transactions()
        if not pending_txns:
            return False
        last_block = self.last_block
        # Creates a new block to be added to the chain
        new_block = Block(
            last_block.index + 1, pending_txns, time.time(), last_block.hash
        )

        # Running PoW algorithm to obtain valid has and consensus
        # proof = self.proof_of_work(new_block)
        # Verifed block can be added to the chain (Previosu hash matches and PoW is valid) then add it
        # self.add_block(new_block, proof)
        # Empties the list of unconfirmed transactions since they are added to the chain
        # self.unconfirmed_transactions = []

        db.pendingTransaction.delete_many({})
        # Announce to the network once a block has been mined, other blocks can simply verify the PoW and add it to the respective chains
        announce_new_block(new_block)
        # Returns the index of the blockthat was added to the chain
        return new_block.index

        # proof of work algorithm that tries different values of nonce in order to get a hash
        # that satistfies the difficulty criteria

    def proof_of_work(self, block):
        block.nonce = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith("0" * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return computed_hash

    # Adds a new transaction to the list of unconfirmed transactions(not yet in the blockchain)
    def add_new_transaction(self, transaction):
        res = None
        prevTxn = unconfirmed_transactions()
        if len(prevTxn) >= 10:
            res = mine_in_interval()

        db.pendingTransaction.insert_one(transaction)

        return res
        # self.unconfirmed_transactions.append(transaction)
        # self.unconfirmed_transactions = self.unconfirmed_transactions()
        # print(self.unconfirmed_transactions)
        # Checks if the chain is valid at the current time

    @classmethod
    def check_chain_validity(cls, chain):
        result = True
        previous_hash = "0"
        for block in chain:
            block_hash = block.hash
            # Removes the hash attributes to recompute the hash again using compute_hash
            delattr(block, "hash")
            if (
                not cls.is_valid_proof(block, block.hash)
                or previous_hash != block.previous_hash
            ):
                result = False
                break
            block.hash = block_hash
            previous_hash = block_hash
        return result

        # Returns the current last Block in the Blockchain

    @classmethod
    def is_valid_proof(cls, block, block_hash):
        return (
            block_hash.startswith("0" * Blockchain.difficulty)
            and block_hash == block.compute_hash()
        )

    @property
    def last_block(self):
        return self.chain[-1]


# End of Blockchain class


# The node's copy of the blockchain
blockchain = Blockchain()


tempList = []
peerList = list(blockchain.peers)


def getMinner():
    global tempList
    global peerList
    if len(peerList) == 0:
        while tempList:  # While tempList is not empty, remove all items from it
            peerList.append(tempList.pop())
    selected_item = random.choice(list(peerList))
    peerList.remove(selected_item)
    tempList.append(selected_item)
    return selected_item


# Create a new endpoint and binds the function to the uRL
@app.route("/new_transaction", methods=["POST"])
# Submit a new transaction, which add new data to the blochain
def new_transaction():
    tx_data = request.get_json()
    print(tx_data)
    required_fields = ["sender_id", "message"]
    for field in required_fields:
        if not tx_data.get(field):
            return "Invalid transaction data", 404
    tx_data["timestamp"] = time.time()
    res = blockchain.add_new_transaction(tx_data)

    if res == None:
        response = {"message": "Transaction added successfully."}
    else:
        response = {"message": "Transaction added successfully.", "Mine": res}
    return response, 201


@app.route("/newPrivateBlockTransaction", methods=["POST"])
# Submit a new transaction, which add new data to the blochain
def newPrivateBlockTransaction():
    tx_data = json.loads(request.get_json())

    required_fields = ["sender_id", "message"]
    for field in required_fields:
        if not tx_data.get(field):
            return "Invalid transaction data", 404
    tx_data["timestamp"] = time.time()
    res = blockchain.add_new_transaction(tx_data)

    if res == None:
        response = {"message": "Transaction added successfully."}
    else:
        response = {"message": "Transaction added successfully.", "Mine": res}
    return response, 201


# *image upload
@app.route("/upload", methods=["POST"])
def upload_image():
    # Check if 'image' file was included in the request
    if "image" not in request.files:
        return "No image file provided", 400

    image_file = request.files["image"]

    image_data = image_file.read()
    tx_data = {"image": image_data, "timestamp": time.time()}

    res = blockchain.add_new_transaction(tx_data)

    if res == None:
        response = {"message": "Transaction added successfully."}
    else:
        response = {"message": "Transaction added successfully.", "Mine": res}
    return response, 201


@app.route("/chain", methods=["GET"])
def get_chain():
    # consensus()
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return {"length": len(chain_data), "chain": chain_data}, 200


# Create a new endpoint and bind the function to the URL
@app.route("/mine", methods=["GET"])
# Requests the node to mine the uncofirmed transaction (if any)
def mine_uncofirmed_transactions():
    result = blockchain.mine()
    if not result:
        return {"message": "There are not transactions to mine"}, 200
    response = "Block #{0} has been mined.".format(result)
    return {"message": response}, 200


@app.route("/nodes/register", methods=["POST"])
def register_nodes():
    values = request.get_json()
    Public_Address = values.get("Public_Address")
    Private_Address_Port = values.get("Private_Address")

    if (Public_Address or Private_Address_Port) is None:
        return "Please supply a valid Private and Public Address", 400
    blockchain.register_node(Public_Address)

    payload = {
        "Public_Address": Public_Address,
        "Private_Address_Port": Private_Address_Port,
    }

    db.Public_Private_Mapping.insert_one(payload)

    response = {
        "message": "New node have been successfully added",
        "total_nodes": list(blockchain.peers),
    }
    return jsonify(response), 201


# Create new endpoint and bind the function to the URL
@app.route("/pending_tx")
# Queries uncofirmed transactions
def get_pending_tx():
    all_pending_txn = db.pendingTransaction.find()
    pendingTxn = []

    for data in all_pending_txn:
        del data["_id"]
        pendingTxn.append(json.loads(json.dumps(data)))

    return {"data": pendingTxn}


# Create a new endpoint and binds the function to the URl
@app.route("/add_block", methods=["POST"])
# Adds a block mined by user to the node's chain
def validate_and_add_block():
    block_data = json.loads(request.get_json())
    # print((block_data) )
    # print("----------------")
    block = Block(
        block_data["index"],
        block_data["transactions"],
        block_data["timestamp"],
        block_data["previous_hash"],
    )
    # proof = block_data["hash"]
    proof = blockchain.proof_of_work(block)
    added = blockchain.add_block(block, proof)
    if not added:
        return "The Block was discarded by the node.", 400
    return "The block was added to the chain.", 201


# Announce to the network once a block has been moned


def announce_new_block(block):
    for peer in blockchain.peers:
        url = "http://{0}/add_block".format(peer)
        data = block.__dict__

        # Convert ObjectId to string before serialization
        data["previous_hash"] = str(data["previous_hash"])

        # Serialize the data to JSON
        json_data = json.dumps(data, default=str, sort_keys=True)

        requests.post(url, json=json_data)


def mine_in_interval():
    minner = getMinner()
    url = f"http://{minner}/mine"
    res = requests.get(url)
    return res.json().get("message")


# Run the Flask web app
if __name__ == "__main__":
    port = int(sys.argv[1])
    app.run(host="0.0.0.0", port=port, debug=True)
