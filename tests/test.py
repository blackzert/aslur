import subprocess

d = {}

def dump(iteration, hysto):
    print 'Iteration %d len %d'%(iteration, len(hysto))
    for key in sorted(hysto):
        print hex(key), hysto[key]


i = 0
while i < 1000000:
    out = subprocess.check_output(['./t'])
    addr = int(out, 16)
    #omit page size
    addr >>= 12
    if addr in d:
        d[addr] += 1
    else:
        d[addr] = 1
    i += 1
dump(i,d)
