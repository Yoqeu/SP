import tempfile
from random import randint
import os
import random

file = "numbers.txt"
with open(file, 'w') as f:
    f.writelines('{}\n'.format(random.randint(-1000000, 1000000)) for _ in range(100000))

all_files = []


def merge_sort(list):
    if len(list) <= 1:
        return list
    else:
        left = list[:len(list) // 2]
        right = list[len(list) // 2:]
    merge_sort(left)
    merge_sort(right)
    i = 0
    j = 0
    k = 0
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            list[k] = left[i]
            i = i + 1
        else:
            list[k] = right[j]
            j = j + 1
        k = k + 1

    while i < len(left):
        list[k] = left[i]
        i = i + 1
        k = k + 1

    while j < len(right):
        list[k] = right[j]
        j = j + 1
        k = k + 1


def split_files(file_path, size):
    with open(file_path, 'r') as file:
        i = 1
        temp = []
        for line in file:
            temp.append(int(line))
            i += 1
            if i > size:
                i = 1
                merge_sort(temp)
                with tempfile.NamedTemporaryFile(delete=False, mode='w') as temp_file:
                    temp_file.writelines(f'{i}\n' for i in temp)
                    all_files.append(temp_file.name)
                temp = []


def merge_sorted_files():
    while len(all_files) > 1:
        with tempfile.NamedTemporaryFile(delete=False, mode='w') as temp_file:
            with open(all_files[0], 'r') as first, open(all_files[1], 'r') as second:
                line_of_first = first.readline()
                line_of_second = second.readline()
                while line_of_first and line_of_second:
                    if int(line_of_first) <= int(line_of_second):
                        temp_file.writelines(line_of_first)
                        line_of_first = first.readline()
                    else:
                        temp_file.writelines(line_of_second)
                        line_of_second = second.readline()

                while line_of_second:
                    temp_file.writelines(line_of_second)
                    line_of_second = second.readline()
                while line_of_first:
                    temp_file.writelines(line_of_first)
                    line_of_first = first.readline()
                all_files.append(temp_file.name)

        if os.path.exists(first.name):
            all_files.pop(0)
            os.remove(first.name)

        if os.path.exists(second.name):
            all_files.pop(0)
            os.remove(second.name)


if __name__ == '__main__':
    split_files(file, 5)
    merge_sorted_files()
    with open(all_files[0], 'r') as file:
        with open("sorted_numbers.txt", 'w') as sorted:
            for line in file:
                sorted.writelines(line)
