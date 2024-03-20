from hashlib import sha512


class Block:
    # One or more piece of data(author, contetn of post and timestamp) will be stored in a block
    # The blocks containing the data are generated frequently and added to the blockchain. These block has unique ID.
    def __init__(self, index, transactions, timestamp, previous_hash, validator_id):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.validator_id = validator_id
        self.current_hash = self.compute_hash()


    # A function that creates the hash of the block content
    def compute_hash(self):
        block_string = str(self.index)  + str(self.transactions) + str(self.previous_hash) + str(self.validator_id) + str(self.timestamp)
        # block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha512(block_string.encode()).hexdigest()
    
    def to_dict(self):
        return {
            'index': self.index,
            'transactions': self.transactions,
            'timestamp': self.timestamp,
            'previous_hash': self.previous_hash,
            'current_hash': self.current_hash,
            'validator_id': self.validator_id
        }
# End of Block class
