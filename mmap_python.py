import rbtree


pagesize = 4096

def ALIGN_DOWN(base, size):
    return base & ((-size)&0xffffffffffffffff)

def ALIGN_UP(base, size):
    return ALIGN_DOWN (base + size - 1, size)

def getElfSize(elffile):
    pagesize = 4096
    mapstart = 0xffffffffffffffff
    mapend = 0
    for s in elffile.iter_segments():
        if s['p_type'] == 'PT_LOAD':
            start = ALIGN_DOWN (s['p_vaddr'], pagesize)
            # end = ALIGN_UP (s['p_vaddr'] + s['p_filesz'], pagesize)
            # dataend = s['p_vaddr'] + s['p_filesz']
            allocend = ALIGN_UP(s['p_vaddr'] + s['p_memsz'], pagesize)
            # mapoff = ALIGN_DOWN (s['p_offset'], pagesize)
            #start = s['p_vaddr'] & ~(pagesize - 1)
            #end = (s['p_vaddr'] + s['p_memsz'] + pagesize - 1) & (0xffffffffffffffff^(pagesize - 1))
            if start < mapstart:
                mapstart = start
            if allocend > mapend:
                mapend = allocend
    return mapend - mapstart


class vma_struct:
    def __init__(self, start=0, end=0, perm=0, offset=0, pathname=None):
        self.start = start
        self.end = end
        self.perm = perm
        self.offset = offset
        self.pathname = pathname
        self.next = None
        self.prev = None
        self.gap = 0
        self.rb = None
    def __repr__(self):
        return "vma: start 0x%x end 0x%x pathname %s gap 0x%x"%(self.start, self.end, self.pathname, self.gap)

class unmapped_area_info:
    def __init__(self, length):
        self.length = length
        self.low_limit = 0
        self.high_limit = 0
        self.align_offset = 0
        self.align_mask = 0

class VirtualMemory:
    MMAP_BITS  = 28 # to 32
    TASK_SIZE = (2**47) - 4096
    STACK_RND_SIZE = 16 * 1024 * 1024 * 1024 - 4096  # this is offset from task size to stack
    MMAP_BASE_RND_SIZE = TASK_SIZE - STACK_RND_SIZE - ((2**MMAP_BITS)<<12)
    
    def __init__(self, mmap_base=0x7ffffffff000 - MMAP_BASE_RND_SIZE):
        self.mmap_base = mmap_base
        self.curr_mmap = self.mmap_base
        self.mm_rb = rbtree.RedBlackTree()
        self.mmap = None

    def __repr__(self):
        return "VirtualMemor: base 0x%x "%self.mmap_base + "\n" + str(self.mm_rb) + "\n" + str(self.mmap)

    def add_stack(self, start, end):
        if self.mmap:
            raise Exception('Mmap already set to init with stack!')
        self.mmap_region(start, end-start, "[stack]")

    def add_bin(self, addr, length, name):
        self.mmap_region(addr, length, name)

    def populate_with_libs(self, build_info):
        # print self
        #print "Populating mm with base ", hex(self.mmap_base)
        for path, lib, elffile in build_info:
            #print "[-] MMapping  ", lib
            self.mmap_lib(elffile, lib, lib != "ld-linux-x86-64.so.2")
            #totalsize = getElfSize(elffile)
            #self.curr_mmap -= totalsize
            #region = vma_struct(self.curr_mmap, totalsize+self.curr_mmap, 0, 0, path)
            #self.regions.append(region)
            #self.regions_by_name[path] = region

    def __fixup_gap(self, node):
        vma = node.value
        gap = vma.start
        if vma.prev:
            gap -= vma.prev.end
        if node.left:
            sub_gap = self.__fixup_gap(node.left)
            if sub_gap > gap:
                gap = sub_gap
        if node.right:
            sub_gap = self.__fixup_gap(node.right)
            if sub_gap > gap:
                gap = sub_gap
        vma.gap = gap
        return gap

    def __find_rb_node(self, key):
        node = self.mm_rb.root
        while node is not None:
            if key == node.key:
                return node
            elif key < node.key:
                node = node.left
            else:
                node = node.right
        raise KeyError(str(key))        


    def __link_vma(self, vma):
        if self.mmap is None:
            self.mmap = vma
            return
        prev_vma = None
        link_vma = self.mmap
        while link_vma and vma.start > link_vma.start:
            prev_vma = link_vma
            link_vma = link_vma.next
        if prev_vma is None:
            self.mmap = vma
        else:
            prev_vma.next = vma
            vma.prev = prev_vma
        if link_vma:
            vma.next = link_vma
            link_vma.prev = vma


    def __link_rb_vma(self, vma):
        self.mm_rb.add(vma.start, vma)
        vma.rb = self.__find_rb_node(vma.start)

    def insert_vma(self, vma):
        self.__link_vma(vma)
        self.__link_rb_vma(vma)
        self.__fixup_gap(self.mm_rb.root)
        
    def rebase_to(self, new_base):
        offset = self.mmap_base - new_base
        for region in self.regions:
            region.start -= offset
            region.end -= offset
        self.mmap_base = new_base

    def mmap_lib(self, elffile, pathname, fill_holes=True):
        totalsize = getElfSize(elffile)
        info = unmapped_area_info(totalsize)
        info.low_limit = 65536
        info.high_limit = self.mmap_base

        addr = self.unmapped_area_topdown(info)
        #print " Mmaping to addr ", hex(addr)
        if fill_holes:
            self.mmap_region(addr, totalsize, pathname)
            return

        first = None
        for seg in elffile.iter_segments():
            if seg['p_type'] == 'PT_LOAD':
                if first is None:
                    first = ALIGN_DOWN (seg['p_vaddr'], pagesize)
                start = ALIGN_DOWN (seg['p_vaddr'], pagesize)+ addr - first
                end = ALIGN_UP (seg['p_vaddr'] + seg['p_filesz'], pagesize) - first + addr
                self.mmap_region(start, end, pathname)
                # dataend = s['p_vaddr'] + s['p_filesz']
                #allocend = ALIGN_UP(s['p_vaddr'] + s['p_memsz'], pagesize)
                # mapoff = ALIGN_DOWN (s['p_offset'], pagesize)
                #start = s['p_vaddr'] & ~(pagesize - 1)
                #end = (s['p_vaddr'] + s['p_memsz'] + pagesize - 1) & (0xffffffffffffffff^(pagesize - 1))


    def mmap_region(self, addr, length, pathname):
        # TBD: check expand
        # TBD: clear old mapping

        # TBD: vma_merge : Can we just expand an old mapping

        vma = vma_struct(addr, addr + length, pathname=pathname)
        self.insert_vma(vma)



    def unmapped_area_topdown(self, info):
        
        #print "Searching unmapped area topdown: len 0x%x"%info.length,  self

        length = info.length

        gap_end = info.high_limit
        if gap_end < length:
            return -1
        high_limit = gap_end - length;

        if info.low_limit > high_limit:
            return -1
        low_limit = info.low_limit + length;

        #gap_start = mm->highest_vm_end;
        #if (gap_start <= high_limit)        
        #   goto found_highest;

        node = self.mm_rb.root
        vma = node.value
        if vma.gap < length:
            return -1
        

        while 1:
            if vma.prev:
                gap_start = vma.prev.end
            else:
                gap_start = 0
            if gap_start <= high_limit and vma.rb.right:
                right = vma.rb.right.value
                if right.gap > length:
                    vma = right
                    continue
            
#check_current:
            while 1:
                gap_end = vma.start
                if gap_end < low_limit:
                    return -1

                if gap_start <= high_limit and gap_end - gap_start >= length:

                    if gap_end > info.high_limit:
                        gap_end = info.high_limit

                    return gap_end - length


                if vma.rb.left:
                    left = vma.rb.left.value
                    if left.gap >= length:
                        vma = left
                        break


                while 1:
                    prev = vma.rb
                    if prev == self.mm_rb:
                        return -1
                    vma = prev.parent.value
                    if prev.parent.right == prev:
                        if vma.prev:
                            gap_start = vma.prev.end
                        else:
                            vma.prev = 0
                        break
#found:
        raise "Did you got it really?"
        if gap_end > info.high_limit:
            gap_end = info.high_limit

        gap_end -= info.high_limit
        gap_end -= (gap_end - info.aligh_offset)&info.align_mask

        return gap_end
