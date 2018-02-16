import subprocess

d = {}
i = 0
while i < 1000000:
    output = subprocess.check_output('./thread_stack_heap_hysto')
    key = int(output, 16)
    if key in d:
        d[key] += 1
    else:
        d[key] = 1
    i += 1
print 'total: ', len(d)
for key in d:
    print hex(key), d[key]
