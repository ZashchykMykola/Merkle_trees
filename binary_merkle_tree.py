import hashlib

class BinaryMerkleTree:
    def __init__(self, data):
        self.tree = self.build_binary_tree(data)
        self.root = self.tree[-1][0]

    def build_binary_tree(self, data):
        hashes = [hashlib.sha256(x.encode('utf-8')).hexdigest() for x in data]
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

    def find_membership_proof(self, target):
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

    def find_membership_proof_by_index(self, target_index):
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


f = open("data_list_indexed.txt", "r")
data = []
for m in f:
    data.append(m.strip().split(", ")[0])
f.close()
#print("Input data: ", data)

binary_tree = BinaryMerkleTree(data)

# пошук елемента перебором, індекс невідомий
target = 202265
proof = binary_tree.find_membership_proof(target)
is_target_valid = binary_tree.verify_membership_proof(proof, target)
print(f'Validation of {target} without index: ', is_target_valid)

# пошук елемента за відомим індексом
target_and_index = [202265, 65526]
proof = binary_tree.find_membership_proof_by_index(target_and_index[1])
is_target_and_index_valid = binary_tree.verify_membership_proof(proof, target_and_index[0])
print(f'Validation of {target_and_index[0]} by index {target_and_index[1]}:', is_target_and_index_valid)
