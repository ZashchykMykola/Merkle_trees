import random

number_of_elements = 65536  #2^16

random_range_min = 0
random_range_max = 1000000

generated_numbers = set()

f_indexed = open("data_list_indexed_binary.txt", "w")
for i in range(0, number_of_elements):
    while True:
        value = random.randint(random_range_min, random_range_max)
        if value not in generated_numbers:
            generated_numbers.add(value)
            break
    f_indexed.write(f"{value}, {i}\n")

f_indexed.close()