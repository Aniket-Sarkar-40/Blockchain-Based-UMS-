import random

tempList = []

def select_item_without_repetition(item_set):
    global tempList
    if len(item_set) == 0:
        while tempList:  # While tempList is not empty, remove all items from it
            item_set.add(tempList.pop())
    selected_item = random.choice(list(item_set))
    item_set.remove(selected_item)
    tempList.append(selected_item)
    return selected_item


def select_member(peer_array, validators_array):
    voteCount = [0] * len(validators_array)

    for peer in peer_array:
        vote_index = random.randint(0, len(validators_array) - 1)
        
        voteCount[vote_index] += 1

    for validator in validators_array:
        vote_index = random.randint(0, len(validators_array) - 1)
        
        voteCount[vote_index] += 1

    max_vote_index = voteCount.index(max(voteCount))

    return max_vote_index


peer_array = ["Peer1", "Peer2", "Peer3", "Peer4"]
validators_array = ["Validator1", "Validator2", "Validator3"]

selected_member_index = select_member(peer_array, validators_array)
selected_member = validators_array[selected_member_index]

print(f"The selected member is: {selected_member}")

