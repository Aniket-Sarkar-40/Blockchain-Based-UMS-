from hashlib import sha512
import json
from bson import ObjectId
import time
import random
from flask_pymongo import PyMongo

from flask import Flask, request
import requests



# Flask web application
# create Flask web application
app = Flask(__name__)

app.config['MONGO_URI'] = "mongodb+srv://aniket15970:3Zmg1JzbEZWO3Gjw@esm.nrjexdy.mongodb.net/pendingTxn?retryWrites=true&w=majority"
mongo = PyMongo(app)
dbPendingTxn = mongo.db

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
        block_string = str(self.index)  + str(self.transactions) + str(self.previous_hash) + str(self.nonce)
        # block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha512(block_string.encode()).hexdigest()
# End of Block class

def unconfirmed_transactions():
    all_pending_txn = dbPendingTxn.pendingTransaction.find()
    pendingTxn = []

    for data in all_pending_txn:
        collegeName = data["collegeName"]
        phoneNo = data["phoneNo"]
        email = data["email"]
        message = data["message"]
        timestamp = data["timestamp"]
        dataDict = {
            "collegeName" : collegeName,
            "phoneNo" : phoneNo,
            "email" : email,
            "message" : message,
            "timestamp" : timestamp
        }

        pendingTxn.append(dataDict)

    return pendingTxn

# A class that represents an immutable list of Block objects are chained together by hashes, a Blockchain.
class Blockchain:
    # Difficult of PoW algorithm
    difficulty = 2
    # One or more blocks will be stored and chained toghether on the Blockchain, starting by the genisi block
    def __init__(self):
        # self.unconfirmed_transactions = self.unconfirmed_transactions()  # These are pieces of data that are not yet added to the Blockchain.
        self.chain = [] # The immutable list that represets the actual Blockchain
        self.create_genesis_block()

    # Generates genesis block and appends it to the Blockchain
    # The Block has index o, previous_hash of 0 and a valid hash
    def create_genesis_block(self):
        genesis_block = Block(0, [], time.time(), "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    # Verifed block can be added to the chain, add it and return True or False
    def add_block(self, block, proof):
        previous_hash = self.last_block.hash
        # Verify that the prvious_hash field of the block to be added points to the hash of the latest block
        # and tjhat the PoW that is provided is correct
        # print(self.is_valid_proof(block, proof))
        if (previous_hash !=block.previous_hash or not self.is_valid_proof(block, proof)):
            return False
        # Add new block to the chain after verification
        block.hash = proof
        self.chain.append(block)
        return True


    # Serve as interface to add the transactions to the blockchain by adding them
    # and then figuring out the PoW
    def mine(self):
        # if uncofirmed_transactions is empyt, no mining to be done
        pending_txns = unconfirmed_transactions()
        if not pending_txns:
            return False
        last_block = self.last_block
        # Creates a new block to be added to the chain
        new_block = Block(last_block.index + 1, \
                    pending_txns, \
                    time.time(), \
                    last_block.hash)

        # Running PoW algorithm to obtain valid has and consensus
        # proof = self.proof_of_work(new_block)
        # Verifed block can be added to the chain (Previosu hash matches and PoW is valid) then add it
        # self.add_block(new_block, proof)
        # Empties the list of unconfirmed transactions since they are added to the chain
        # self.unconfirmed_transactions = []

        dbPendingTxn.pendingTransaction.delete_many({})
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
        if(len(prevTxn)>=10):
            res = mine_in_interval()

        dbPendingTxn.pendingTransaction.insert_one(transaction)

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
            if not cls.is_valid_proof(block, block.hash) or previous_hash != block.previous_hash:
                result = False
                break
            block.hash = block_hash
            previous_hash = block_hash
        return result


            # Returns the current last Block in the Blockchain
    @classmethod
    def is_valid_proof(cls, block, block_hash):
        return (block_hash.startswith("0" * Blockchain.difficulty) and block_hash == block.compute_hash())

    @property
    def last_block(self):
        return self.chain[-1]
# End of Blockchain class



# The node's copy of the blockchain
blockchain = Blockchain()
# A set that stores the addresses to other participating members in the network
peers = set()
peers.add("127.0.0.1:5000")
peers.add("127.0.0.1:5001")
peers.add("127.0.0.1:5002")
peers.add("127.0.0.1:5003")
peers.add("127.0.0.1:5004")

# previous_item = None

tempList = []
peerList = list(peers)

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

# def getMinner(item_set):
#     global previous_item
#     item_list = list(item_set)
#     while True:
#         selected_item = random.choice(item_list)
#         if selected_item != previous_item:
#             previous_item = selected_item
#             return selected_item

# Create a new endpoint and binds the function to the uRL
@app.route("/new_transaction", methods=["POST"])
# Submit a new transaction, which add new data to the blochain
def new_transaction():
    tx_data = request.get_json()
    required_fields = ["collegeName", "phoneNo", "email", "message" ]
    for field in required_fields:
        if not tx_data.get(field):
            return "Invalid transaction data", 404
    tx_data["timestamp"] = time.time()
    res = blockchain.add_new_transaction(tx_data)
    
    if res==None:
        response = {"message": "Transaction added successfully."}
    else:
        response = {"message" : "Transaction added successfully." , "Mine" : res}
    return response, 201




#*image upload
@app.route('/upload', methods=['POST'])
def upload_image():
    # Check if 'image' file was included in the request
    if 'image' not in request.files:
        return 'No image file provided', 400

    image_file = request.files['image']

    image_data = image_file.read()
    tx_data = {"image" : image_data , "timestamp":time.time()}

    res = blockchain.add_new_transaction(tx_data)
    
    if res==None:
        response = {"message": "Transaction added successfully."}
    else:
        response = {"message" : "Transaction added successfully." , "Mine" : res}
    return response, 201



@app.route("/chain", methods=["GET"])
def get_chain():
    # consensus()
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return {"length" : len(chain_data), "chain" : chain_data} , 200
        

# Create a new endpoint and bind the function to the URL
@app.route("/mine", methods=["GET"])
# Requests the node to mine the uncofirmed transaction (if any)
def mine_uncofirmed_transactions():
    result = blockchain.mine()
    if not result:
        return {"message": "There are not transactions to mine"},200
    response = "Block #{0} has been mined.".format(result)
    return {"message" : response},200


# Cretes a new endpoint and binds the function to the URL
# Adds new peers to the network
def register_new_peers():
    nodes = request.get_json()
    if not nodes:
        return "Invalid data", 400
    for node in nodes:
        peers.add(node)
    return "Success", 201


# Create new endpoint and bind the function to the URL
@app.route("/pending_tx")
# Queries uncofirmed transactions
def get_pending_tx():
    all_pending_txn = dbPendingTxn.pendingTransaction.find()
    pendingTxn = []

    for data in all_pending_txn:
        collegeName = data["collegeName"]
        phoneNo = data["phoneNo"]
        email = data["email"]
        message = data["message"]
        timestamp = data["timestamp"]
        dataDict = {
            "collegeName" : collegeName,
            "phoneNo" : phoneNo,
            "email" : email,
            "message" : message,
            "timestamp" : timestamp
        }

        pendingTxn.append(dataDict)


    return {"data" : pendingTxn}


# A simple algorithm to achieve consensus to mantain the intergrity of Blochain
# If a longer valid chain is found, the chain is replaced with it and returns True, otherwise nothing happens and returns false
#* def consensus():
#     global blockchain
#     longest_chain = None
#     curr_len = len(blockchain.chain)
#     # Achieve consensus by chacking th Json fields of every node in the network
#     for node in peers:
#         response = requests.get("http://{0}".format(node))
#         length = response.json()["length"]
#         chain = response.json()["chain"]
#         if length > curr_len and blockchain.check_chain_validity(chain):
#             curr_len = length
#             longest_chain = chain
#     if longest_chain:
#         blockchain = longest_chain
#         return True
#     return False


# Create a new endpoint and binds the function to the URl
@app.route("/add_block", methods=["POST"])
# Adds a block mined by user to the node's chain
def validate_and_add_block():
    block_data = json.loads(request.get_json())
    # print((block_data) )
    # print("----------------")
    block = Block(block_data["index"],  block_data["transactions"],  block_data["timestamp"], block_data["previous_hash"])
    # proof = block_data["hash"]
    proof = blockchain.proof_of_work(block)
    added = blockchain.add_block(block, proof)
    if not added:
        return "The Block was discarded by the node.", 400
    return "The block was added to the chain.", 201


# Announce to the network once a block has been moned

def announce_new_block(block):
    for peer in peers:
        url = "http://{0}/add_block".format(peer)
        data = block.__dict__

        # Convert ObjectId to string before serialization
        data['previous_hash'] = str(data['previous_hash'])

        # Serialize the data to JSON
        json_data = json.dumps(data,  default=str, sort_keys=True)

        requests.post(url, json=json_data)



def mine_in_interval():
    minner = getMinner()
    # print(minner,peerList,tempList)
    url = f'http://{minner}/mine'
    res = requests.get(url)
    return res.json().get('message')


# Run the Flask web app
if __name__ == "__main__":
    port = int(input("Enter the port number for this node: "))
    app.run(host="0.0.0.0", port=port)
