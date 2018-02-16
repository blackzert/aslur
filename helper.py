import gdb

#class mmap_break (gdb.Breakpoint):
#      def stop (self):
#        inf_val = gdb.parse_and_eval("foo")
#        if inf_val == 3:
#          return True
#        return False

def handle_do_mmap(event):
    gdb.execute("finish")
    global hit_wait
    hit_wait = True
    #print("hit set ", hit_wait)

handled_breaks = {'do_mmap' : handle_do_mmap}



def stop_handler (event):
    global hit_wait
    global handled_breaks
    if isinstance(event, gdb.BreakpointEvent):
        if event.breakpoint.location in handled_breaks:
            #print('we know how handle it')
            handled_breaks[event.breakpoint.location](event)
        return
    if isinstance(event, gdb.StopEvent):
        #print("Got stop...")
        #if not hit_wait:
        #    print("No hit, you need handle it")
        #    return
        hit_wait = False
        rax = int(gdb.parse_and_eval("$rax")) & 0xffffffffffffffff
        #print("got value %x"%rax)
        if rax&0x8000000000000000:
            print("wut?")
        else:
         #   print("continue...")
            gdb.execute("c")
        return
    return

#gdb.execute("finish")
#rax = int(gdb.parse_and_eval("$rax")) & 0xffffffffffffffff

gdb.events.stop.connect(stop_handler)


