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


# Example usage
item_set = {1,2,3,4,5}

# print(item_set)

selc1 = select_item_without_repetition(item_set)
print("Selected Item:", selc1)
print("Remaining Set:", item_set)  # The original set is changed, and the selected item is removed
print (tempList)

print()

selc1 = select_item_without_repetition(item_set)
print("Selected Item:", selc1)
print("Remaining Set:", item_set)  # The original set is changed, and the selected item is removed
print (tempList)

print()

selc1 = select_item_without_repetition(item_set)
print("Selected Item:", selc1)
print("Remaining Set:", item_set)  # The original set is changed, and the selected item is removed
print (tempList)

print()

selc1 = select_item_without_repetition(item_set)
print("Selected Item:", selc1)
print("Remaining Set:", item_set)  # The original set is changed, and the selected item is removed
print (tempList)

print()

selc1 = select_item_without_repetition(item_set)
print("Selected Item:", selc1)
print("Remaining Set:", item_set)  # The original set is changed, and the selected item is removed
print (tempList)

print()

selc1 = select_item_without_repetition(item_set)
print("Selected Item:", selc1)
print("Remaining Set:", item_set)  # The original set is changed, and the selected item is removed
print (tempList)