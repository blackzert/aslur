import subprocess
import sys
import re
import os
import os.path
import elftools
from elftools.elf.elffile import ELFFile
from elftools.elf.sections import SymbolTableSection
from elftools.common.exceptions import ELFError
import mmap_python


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
        with open("/proc/%d/cmdline"%pid, "r") as fd:
            self.cmdline = fd.read()
        self.concat_len = 0
        try:
            with open("/proc/%d/maps"%pid,"r") as fd:
                r_prev = None
                for region in fd:
                    m_region = maps_region(region.strip())
                    m_region.prev = r_prev
                    r_prev = m_region
                    self.regions.append( m_region )
                for region in self.regions[1:]:
                    region.prev.next = region
        except IOError as e:
            raise OSError()


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



def usage():
    print "Usage: %s <pid1> <pid2>"%sys.argv[0]
    sys.exit(-1)    

def inspect(pid1, pid2):
    proc1 = proc_maps(pid1)
    proc2 = proc_maps(pid2)
    if proc1.cmdline != proc2.cmdline:
        print "[WARNING] cmdline not the same, may be wrong result"






'''
def getElfSize(stream):
    elffile = ELFFile(stream)
    pagesize = 4096
    mapstart = 0xffffffffffffffff
    mapend = 0
    for s in elffile.iter_segments():
        if s['p_type'] == 'PT_LOAD':
            start = s['p_vaddr'] & ~(pagesize - 1)
            end = (s['p_vaddr'] + s['p_memsz'] + pagesize - 1) & (0xffffffffffffffff^(pagesize - 1))
            if start < mapstart:
                mapstart = start
            if end > mapend:
                mapend = end
    return mapend - mapstart

if __name__ == "__main__":
    if len(sys.argv) != 3:
        usage()
    try:
        pid1 = int(argv[1])
        pid2 = int(argv[2])
    except e:
        usage()
    inspect(pid)
'''
class lib_mapped:
    def __init__(self):
        self.start = 0xffffffffffffffff
        self.end = 0
        self.name = ''
        self.size = 0

def check_sizes():
    global_libs = {}
    for pid in range(1,65536):
            try:
                proc = proc_maps(pid)
                libs = {}
                for region in proc.regions:
                    if region.pathname == "":
                        continue
                    if not (region.pathname.startswith("/lib") or region.pathname.startswith("/usr/lib")):
                        continue
                    if region.pathname in libs:
                        lib = libs[region.pathname]
                        if lib.start > region.start:
                            lib.start = region.start
                        if lib.end < region.end:
                            lib.end = region.end
                    else:
                        lib = lib_mapped()
                        lib.name = region.pathname
                        lib.start = region.start
                        lib.end = region.end
                        libs[region.pathname] = lib
                for lib_name in libs:
                    lib = libs[lib_name]
                    size = lib.end - lib.start
                    if lib_name in global_libs:
                        if global_libs[lib_name] != size:
                            print "Size mistmach with %s pid %d size 0x%x expected 0x%x"%(lib_name, pid, size, global_libs[lib_name])
                    else:
                        global_libs[lib_name] = size
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
    for name in global_libs:
        fd = open(name, "rb")
        try:
            elffile = ELFFile(fd)
            size = mmap_python.getElfSize(elffile)
        except ELFError as e:
            #print "Failed parse ", name, str(e)
            pass
        #print "Name %s size 0x%x compute size 0x%x"%(name, global_libs[name], size)
        if size < global_libs[name]:
            print " %s Size mismatch size 0x%x compute size 0x%x"%(name, global_libs[name], size)


def getElfInterp(elffile):
    for s in elffile.iter_segments():
        if s['p_type'] == 'PT_INTERP':
            return s.get_interp_name()

def getDynamicSection(elffile):
    dyn = None
    dyn = elffile.get_section_by_name('.dynamic')
    if dyn is None:
        for s in elffile.iter_sections():
            if s['sh_type'] == 'SHT_DYNAMIC':
                dyn = s
                break
    if dyn is None:
        raise Exception('Not a dyn pe')
    return dyn

def getSoname(elffile):
    dyn = getDynamicSection(elffile)
    for tag in dyn.iter_tags():
        if tag['d_tag'] == 'DT_SONAME':
            return tag.soname
    return None


def getNeeded(elffile):
    res = []
    dyn = getDynamicSection(elffile)
    for tag in dyn.iter_tags():
        if tag['d_tag'] == 'DT_NEEDED':
            res.append(tag.needed)
    return res


all_files = []

def getLibs():
    global all_files
    paths = ['/lib64', '/lib/x86_64-linux-gnu', '/usr/lib/x86_64-linux-gnu', '/lib', '/usr/lib',
             '/home/blackzert/pycharm-community-2017.1.3/jre64/lib/amd64/jli/']
    for path in paths:
        for subdir, dirs, files in os.walk(path):
            for file in files:
                all_files.append(os.path.join(subdir, file))

def findLib(libname):
    if len(all_files) == 0:
        getLibs()
    #print 'Searching ', libname
    for file in all_files:
        #print 'try ', fname
        if file.endswith(libname):
            if os.path.islink(file):
                return  os.path.join(os.path.dirname(file), os.readlink(file))
            if os.path.isfile(file):
                return file
    return None


def build_order(elffile):
    build = []
    namespace = {}    
    interp = getElfInterp(elffile)
    if interp is None:
        print "Warning: not a dinmaicaly linked"
        return None # not a dinamicaly linked, now we need to fall back
    if os.path.islink(interp):
        interp = os.readlink(interp)
    fd = open(interp, "rb")
    interp_elf = ELFFile(fd)
    soname = getSoname(interp_elf)
    
    build.append((interp, soname, interp_elf))
    namespace[soname] = interp
    needed = getNeeded(elffile)
    while needed:
        lib = needed.pop(0)
        if lib in namespace:
            continue # omit repeate.
        path = findLib(lib)
        if path is None:
            print 'Warning: failed to find lib ', lib
            return None
        namespace[lib] = path
        fd = open(path, 'rb')
        neededFile = ELFFile(fd)
        build.append((path, lib, neededFile))
        needed.extend(getNeeded(neededFile))
    return build



def check_process_theory(pid):
    proc = proc_maps(pid)
    #print "Checkin pid ", pid
    fd = open(proc.exe, 'rb')
    elffile = ELFFile(fd)
    build_info = build_order(elffile)
    if build_info is None:
        print "error with  pid: ", pid
        return
    mmap_base = None
    prev_reg = None
    bin_addr = None
    for region in proc.regions:
        if region.pathname == proc.exe and bin_addr is None:
            bin_addr = region.start
        if '[stack]' in region.pathname:
            stack_segm = region
            mmap_base = prev_reg.end
        prev_reg = region
    if mmap_base is None:
        print "Failed get mmap_base for pid ", pid
        return False
    mm = mmap_python.VirtualMemory(mmap_base)
    mm.add_stack(stack_segm.start, stack_segm.end)


    if elffile.header['e_type'] != 'ET_DYN':
        addr = None
        for s in elffile.iter_segments():
            if s['p_type'] == 'PT_LOAD':
                addr = s['p_vaddr']
    else:
        addr =  (0x7ffffffff000 * 2/3)&0x7ffffffff000
        addr = bin_addr
    length = mmap_python.getElfSize(elffile)
    mm.add_bin(addr, length, proc.exe)
    for x in build_info:
        print x[0]
    mm.populate_with_libs(build_info)
    vma = mm.mmap
    match = True
    while vma:
        #print "Matching ", vma
        found = False
        for r in proc.regions:
            if r.start == vma.start:
                found = True
                break
        if not found:
            #print "Failed to find ", vma
            match = False
        vma = vma.next
    print mm
    return match


def check_theory():
    global_libs = {}
    good = []
    bad = []
    error = []
    for pid in range(1,65536):
        try:
            if check_process_theory(7591):
                good.append(pid)
            else:
                bad.append(pid)
            break
        except OSError:
            error.append(pid)
        except IOError:
            error.append(pid)
    print "Good: ", good
    #print "Bad", bad
    #print "error", error
        

check_theory()