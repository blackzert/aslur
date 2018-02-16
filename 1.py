import re
import os
import sys

class device_desc:
    def __init__(self, major, minor):
        self.major = major
        self.minor = minor

class maps_region:
    PERM_READ = 1
    PERM_WRITE = 2
    PERM_EXECUTE = 4
    PERM_PRIVATE = 0x100
    PERM_SHARED = 0x200
    def __init__(self, s):
        s = re.sub(' +', ' ', s)
        try:
            l = s.split(' ', 5)
            if len(l) == 5:
                l.append('anonymouse')
            addr, perm, offt, dev, inode, path = l
        except ValueError as e:
            print e, '=====>', s.split(' '), '<====='
            raise
        addr = addr.split('-')
        self.start = int(addr[0], 16)
        self.end = int(addr[1], 16)
        self.perm = self._parse_perm(perm)
        self.offset = int(offt, 16)
        major, minor = self._parse_dev(dev)
        self.dev = device_desc(major, minor)
        self.inode = int(inode, 10)
        self.pathname = path
        self.next = None
        self.prev = None

    def __str__(self):
        return "%x-%x %x"%(self.start, self.end, self.perm)

    def _parse_dev(self, dev):
        dev = dev.split(':')
        major = int(dev[0], 16)
        minor = int(dev[1], 16)
        return major, minor

    def _parse_perm(self, perm):
        result = 0
        while perm:
            c = perm[0]
            perm = perm[1:]
            if c == 'r':
                result |= maps_region.PERM_READ
                continue
            if c == 'w':
                result |= maps_region.PERM_WRITE
                continue
            if c == 'x':
                result |= maps_region.PERM_EXECUTE
                continue
            if c == 'p':
                result |= maps_region.PERM_PRIVATE
                continue
            if c == 's':
                result |= maps_region.PERM_SHARED
                continue
            if c == '-':
                continue
            print 'unexpected symbo "%c" in perm'%c
        return result

class proc_maps:
    def __init__(self, pid):
        self.regions = []
        self.pid = pid
        self.exe = os.readlink("/proc/%d/exe"%pid)
        self.concat_len = 0
        with open("/proc/%d/maps"%pid,"r") as fd:
            r_prev = None
            for region in fd:
                m_region = maps_region(region.strip())
                m_region.prev = r_prev
                r_prev = m_region
                self.regions.append( m_region )
            for region in self.regions[1:]:
                region.prev.next = region

    def __str__(self):
        s = ''
        for region in self.regions:
            s += str(region) + "\n"
        return s

    def analyze(self):
        holes_info = ''
        libs_info = ''
        current_name = self.regions[0].pathname
        current_end = self.regions[0].end
        self.concat_len = 0
        concat_start = 0
        concat_end = 0
        for region in self.regions[1:]:
            if current_end != region.start:
                holes_info += 'Hole %d(0x%x) between %s(0x%x) and %s(0x%x)\n'%(region.start - current_end, region.start - current_end, current_name, current_end, region.pathname, region.start)
            elif current_name != region.pathname: 
                libs_info += 'libs concat %s(0x%x) and %s\n'%(current_name, current_end, region.pathname)
            current_end = region.end
            current_name = region.pathname
        return holes_info, libs_info

if __name__ == '__main__':
    if len(sys.argv) < 2:
        for pid in range(1,65536):
                try:
                    proc = proc_maps(pid)
                    holes_info, libs_info = proc.analyze()
                    if holes_info == '' and libs_info == '':
                        continue
                    print proc.exe, pid, hex(proc.concat_len)
                    print 'Holes:\n'+holes_info + 'Libs\n' + libs_info
                    print ''
                except IOError as e:
                    if e.errno == 13:
                        continue
                    if e.errno == 2:
                        continue
                    print pid, e
                except OSError as e:
                    if e.errno == 13:
                        continue
                except Exception as e:
                    raise
        exit(0)
    pid = int (sys.argv[1])
    proc = proc_maps(pid)
    rsp = [ 0x7f00dc5fcbc0, 0x7f00d76fcbc0, 0x7f00d7efdec0, 0x7f00c5bfe7d0, 0x7f00d22fe7d0, 0x7f00d96fdcf0, 0x7f00d86fec70, 0x7f00dcdfdc70, 0x7f00ddffcc70, 0x7f00de7fdc70, 0x7f00deffec70, 0x7f00fb451dd0, 0x7f00dfcfec70, 0x7f00e35fec70, 0x7f00ec48db50, 0x7f00e6dfccf0, 0x7f00e4bfd7d0, 0x7f00e62fe7d0, 0x7f00e75fdc70, 0x7f00e7dfec70, 0x7f00ea1fcc70, 0x7f00ea9fdc70, 0x7f00eb1fec70, 0x7f00ed9fab50, 0x7f00ee1fbc70, 0x7f00ee9fcc90, 0x7f00ef1fdc90, 0x7f00ef9feb50, 0x7f00f0ffec70, 0x7f00f1cfec70, 0x7f00f50f7c70, 0x7f0100842dd0, 0x7f00f5afee20, 0x7f00f68f8e20, 0x7f00f70f9e20, 0x7f00f78fae20, 0x7f00f80fbe20, 0x7f00f88fce20, 0x7f00f90fde20, 0x7f00f98fedc0, 0x7f00fa2fc910, 0x7f00faafdcd0, 0x7f00fb2febe0, 0x7f00fdc73b88, 0x7f00ff882e60, 0x7f0100083e70, 0x7f0101abce70, 0x7ffdb8a1bc70 ]
    tinfo = {}
    for s in rsp:
        for region in proc.regions:
            if s >= region.start and s < region.end:
                tinfo[s] = region
                break
        if not s in tinfo:
            print "[-] Failed to find baby %x"%s
    for s in tinfo:
        print hex(s), str(tinfo[s]), str(tinfo[s].prev), str(tinfo[s].next)







