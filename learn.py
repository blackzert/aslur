import random

def make_array(leng):
    r = []
    for x in range(leng):
        r.append(random.randrange(4096, 2**47-4096, 4096))
    return sorted(r)[::-1]

def check_gap(array, gap):
    hi = len(array) - 1
    if gap < array[hi]:
        # in this case whole array is fine.
        return
    if array[0] < gap:
        return
    low = 0
    idx = (hi - low)/2
    while (hi - low)/2:
        if gap > array[idx]:
            hi = idx
        else:
            low = idx
        idx = (hi - low)/2 + low
    #print gap, idx, array[idx - 1], array[idx], array[idx+1]
    if array[idx] < gap:
        print "wut?"
    if array[idx + 1] >= gap:
        print "at"
    if not( (array[idx] >= gap) and (gap > array[idx + 1]) ):
        print('false ?')

while 1:
    a = make_array(random.randint(1, 65536))
    check_gap(a, random.randrange(4096, 2**47-4096, 4096))
    check_gap(a,  random.randint(0, 65536))


