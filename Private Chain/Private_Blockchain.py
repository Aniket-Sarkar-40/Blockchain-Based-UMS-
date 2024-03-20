import random
from Block import Block
import time


class PrivateBlockchain:
    def __init__(self):
        self.peers = [] 
        self.validators = [] 
        self.blocks = []
        self.transaction_pool = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(0, [], time.time(), "0", "genesis")
        genesis_block.current_hash = genesis_block.compute_hash()

        self.blocks.append(genesis_block)

    def show_blocks(self):
        return self.blocks

    # adding transaction without checking sender and receiver existence (checked in mine fuunction)
    def add_transaction(self, transaction):
        self.transaction_pool.append(transaction)

    def add_peer(self, peer):
        self.peers.append(peer)

    def add_validator(self, validator):
        self.validators.append(validator)

    def select_member(self):
        voteCount = [0] * len(self.validators)

        for peer in self.peers:
            vote_index = random.randint(0, len(self.validators) - 1)
            
            voteCount[vote_index] += 1

        for validator in self.validators:
            vote_index = random.randint(0, len(self.validators) - 1)
            
            voteCount[vote_index] += 1

        max_vote_index = voteCount.index(max(voteCount))

        return self.validators[max_vote_index] 

    def mine(self):
        if len(self.validators) == 0:
            return False
        validator = self.select_member()
        validator_id = validator['id']

        valid_transactions = []
        for transaction in self.transaction_pool:
            peer_sender = None  # neglecting double spending condition
            peer_receiver = None
            for i in range(len(self.peers)):
                if transaction['sender'] == self.peers[i]['public_key']:
                    peer_sender = i
                if transaction['receiver'] == self.peers[i]['public_key']:
                    peer_receiver = i
            if peer_sender == None or peer_receiver == None:
                continue  # skip the transaction
            valid_transactions.append(transaction)

        last_block = self.last_block    
        new_block = Block(last_block.index + 1, valid_transactions, time.time(), last_block.current_hash, validator_id )
        
        self.blocks.append(new_block)
        self.transaction_pool.clear()
        return True

    def view_all_transactions(self):
        return self.transaction_pool

    def view_all_peers(self):
        return self.peers

    def view_all_validators(self):
        return self.validators
    
    @property
    def last_block(self)->Block:
        return self.blocks[-1]
