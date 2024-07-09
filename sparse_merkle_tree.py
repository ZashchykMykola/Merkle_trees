import hashlib
import random
class SparseMerkleTree:
    def __init__(self, data, dummy_value='0'*64):
        self.dummy_value = dummy_value
        self.dummy_value_hash = hashlib.sha256(self.dummy_value.encode('utf-8')).hexdigest()    # фіктивний хеш
        self.tree = self.build_sparse_tree(data)
        self.root = self.tree[-1][0]

    def hash_data(self, data):
        if data is None:
            return self.dummy_value_hash
        else:
            return hashlib.sha256(data.encode('utf-8')).hexdigest()

    def build_sparse_tree(self, data):
        hashes = [self.hash_data(x) for x in data]
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

    def find_proof(self, target):
        str_target = str(target)
        target_hash = hashlib.sha256(str_target.encode('utf-8')).hexdigest()

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

        return proof

    def find_proof_by_index(self, target_index):
        if target_index >= len(self.tree[0]):
            return []   #доказ порожній

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

        return proof


    def verify_membership_proof(self, proof, target):
        str_target = str(target)
        target_hash = hashlib.sha256(str_target.encode('utf-8')).hexdigest()
        computed_hash = target_hash

        for sibling_hash, is_right_node in proof:
            if is_right_node:
                combined = sibling_hash + computed_hash
                combined_hash = hashlib.sha256(combined.encode('utf-8')).hexdigest()
            else:
                combined = computed_hash + sibling_hash
                combined_hash = hashlib.sha256(combined.encode('utf-8')).hexdigest()

            computed_hash = combined_hash

        #print("Computed root in verify: ", computed_hash)
        #print("Expected root: ", self.root)
        #print(f"Computed root == Expected root: {computed_hash == self.root}")
        return computed_hash == self.root

    def verify_exclusion_proof(self, proof):
        computed_hash = self.dummy_value_hash

        for sibling_hash, is_right_node in proof:
            if is_right_node:
                combined = sibling_hash + computed_hash
                combined_hash = hashlib.sha256(combined.encode('utf-8')).hexdigest()
            else:
                combined = computed_hash + sibling_hash
                combined_hash = hashlib.sha256(combined.encode('utf-8')).hexdigest()

            computed_hash = combined_hash

        return computed_hash == self.root


f = open("data_list_indexed_sparse.txt", "r")
data = []
for m in f:
    data.append(m.strip().split(", ")[0])
f.close()

empty_data = [None]*len(data)
data_shuffled = data + empty_data

random.seed(10)
random.shuffle(data_shuffled)
#print("Data shuffled: ", data_shuffled)

f_shuffled = open("data_list_indexed_sparse_shuffled.txt", "w")
i = 0
for m in data_shuffled:
    f_shuffled.write(f"{m}, {i}\n")
    i += 1

f_shuffled.close()

# створення і заповнення дерева
sparse_tree = SparseMerkleTree(data_shuffled)

# пошук елемента за відомим індексом
target_and_index = [18845, 1]
membership_proof = sparse_tree.find_proof_by_index(target_and_index[1])
is_target_and_index_valid = sparse_tree.verify_membership_proof(membership_proof, target_and_index[0])
print(f'Membership validation of {target_and_index[0]} by index {target_and_index[1]}:', is_target_and_index_valid)

# верифікація невключення елемента за відомим індексом
exclusion_index = 65486
exclusion_proof = sparse_tree.find_proof_by_index(exclusion_index)
is_target_and_index_valid = sparse_tree.verify_exclusion_proof(exclusion_proof)
print(f'Exclusion validation of element by index {exclusion_index}:', is_target_and_index_valid)
