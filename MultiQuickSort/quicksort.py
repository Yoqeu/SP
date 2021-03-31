from threading import Thread
import threading
import time


def qsort(sets, left, right):
    print("thead {0} is sorting {1}".format(threading.current_thread(), sets[left:right]))

    i = left
    j = right
    pivot = int(sets[int((left + right) / 2)])
    temp = 0
    while i <= j:
        while pivot > sets[i]:
            i = i + 1
        while pivot < sets[j]:
            j = j - 1
        if i <= j:
            temp = sets[i]
            sets[i] = sets[j]
            sets[j] = temp
            i = i + 1
            j = j - 1

    lthread = None
    rthread = None

    if (left < j):
        lthread = Thread(target=lambda: qsort(sets, left, j))
        lthread.start()

    if (i < right):
        rthread = Thread(target=lambda: qsort(sets, i, right))
        rthread.start()

    if lthread is not None: lthread.join()
    if rthread is not None: rthread.join()
    return sets


'''testing below'''
ls = [1, 3, 6, 9, 1, 2, 3, 8, 6, 11, 15, 25, 3, 64, 17]
res = qsort(ls, 0, len(ls) - 1)
print(res)
