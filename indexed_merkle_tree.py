import hashlib
import random
class IndexedMerkleTree:
    def __init__(self, data):
        self.data_chain = self.build_data_chain(data)
        self.concatenated_chain = self.concatenate_chain(self.data_chain)
        self.tree = self.build_indexed_tree()
        self.root = self.tree[-1][0]


    def build_indexed_tree(self):
        hashes = [hashlib.sha256(x.encode('utf-8')).hexdigest() for x in self.concatenated_chain]
        tree = [hashes]

        while len(hashes) > 1:
            new_level = []
            for i in range(0, len(hashes), 2):
                left = hashes[i]
                right = hashes[i + 1] if i + 1 < len(hashes) else hashes[i]
                combined = left + right
                new_level.append(hashlib.sha256(combined.encode('utf-8')).hexdigest())
            hashes = new_level
            tree.append(hashes)
        return tree

    def build_data_chain(self, data):
        sorted_data = sorted(str(x) for x in data)
        if not data:
            return []

        chain = []
        for i in range(len(sorted_data)):
            val = sorted_data[i]
            nextIdx = 0
            nextVal = ""
            for j in range(i + 1, len(sorted_data)):
                if sorted_data[j] > val:
                    nextIdx = j
                    nextVal = sorted_data[j]
                    break
            chain.append((val, nextIdx, nextVal))
        return chain

    def concatenate_chain(self, data_chain):
        concatenated_chain = []
        for node in data_chain:
            concatenated = f"{node[0]}{node[1]}{node[2]}"
            concatenated_chain.append(concatenated)
        return concatenated_chain

    def find_membership_proof(self, target):
        target = str(target)
        target_node = None
        for node in self.data_chain:
            if node[0] == target:
                target_node = node
                break

        if target_node is None:
            return []

        concatenated_target = f"{target_node[0]}{target_node[1]}{target_node[2]}"
        target_hash = hashlib.sha256(concatenated_target.encode('utf-8')).hexdigest()

        if target_hash not in self.tree[0]:
            return []

        target_index = self.tree[0].index(target_hash)
        proof = []

        for level in self.tree[:-1]:
            level_size = len(level)
            is_right_node = target_index % 2 == 1
            sibling_index = target_index - 1 if is_right_node else target_index + 1

            if sibling_index >= level_size:
                sibling_index = target_index

            sibling_hash = level[sibling_index]
            proof.append((sibling_hash, is_right_node))

            target_index //= 2

        return [target_hash, proof]


    def verify_membership_proof(self, proof):
        if not proof:
            return False

        computed_hash = proof[0]

        for sibling_hash, is_right_node in proof[1]:
            if is_right_node:
                combined = sibling_hash + computed_hash
                combined_hash = hashlib.sha256(combined.encode('utf-8')).hexdigest()
            else:
                combined = computed_hash + sibling_hash
                combined_hash = hashlib.sha256(combined.encode('utf-8')).hexdigest()

            computed_hash = combined_hash

        return computed_hash == self.root


    def find_exclusion_proof(self, target):
        target = str(target)
        target_node = None
        for i, node in enumerate(self.data_chain):
            if node[0] > target:
                target_node = node
                if i == 0:
                    prev_node = None
                else:
                    prev_node = self.data_chain[i - 1]
                break

        if target_node is None:
            prev_node = self.data_chain[-1]
            target_node = ((chr(255) * 256), 0, 0) # щоб програма працювала з строками, тут повинен бути аналог нескінченності для строки
            # якщо більшого елемента знайти не вдалось, значить елемент для перевірки вже найбільший
            # в такому випадку попереднім елементом стає найбільший елемент в ланцюгу, а найбільший об'єкт - нескінченністю

        return [target, prev_node, target_node]

    def verify_exclusion_proof(self, proof):

        target, prev_node, next_node = proof

        if prev_node is None:
            return target < next_node[0]
        else:
            return prev_node[0] < target < next_node[0]


f = open("data_list_indexed_binary.txt", "r")
data = []
for m in f:
    data.append(m.strip().split(", ")[0])
f.close()
#print("Input data: ", data)

indexed_tree = IndexedMerkleTree(data)

#print("Data chain: ", indexed_tree.data_chain)

target = 218482
print("Target: ", target)
membership_proof = indexed_tree.find_membership_proof(target)
print(membership_proof)
print("Membership verification: ", indexed_tree.verify_membership_proof(membership_proof))

exclusion_proof = indexed_tree.find_exclusion_proof(target)

print("Exclusion_proof verification: ", indexed_tree.verify_exclusion_proof(exclusion_proof))




