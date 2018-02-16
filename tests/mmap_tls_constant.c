#include <stdlib.h>
#include <stdio.h>
#include <errno.h>
#include <asm/prctl.h>
#include <sys/prctl.h>
#include <stdint.h>
#include <sys/mman.h>

typedef struct
{
	  int i[4];
} __128bits;


typedef struct
{
	void *tcb;		/* Pointer to the TCB.  Not necessarily the
						   thread descriptor used by libpthread.  */
	void *dtv;
	void *self;		/* Pointer to the thread descriptor.  */
	int multiple_threads;
	int gscope_flag;
	uintptr_t sysinfo;
	uintptr_t stack_guard;
	uintptr_t pointer_guard;
	unsigned long int vgetcpu_cache[2];
	int __glibc_reserved1;
	int __glibc_unused1;
	/* Reservation of some values for the TM ABI.  */
	void *__private_tm[4];
	/* GCC split stack support.  */
	void *__private_ss;
	long int __glibc_reserved2;
	/* Must be kept even if it is no longer used by glibc since programs,
	 *    like AddressSanitizer, depend on the size of tcbhead_t.  */
	__128bits __glibc_unused2[8][4] __attribute__ ((aligned (32)));

	void *__padding[8];
} tcbhead_t;


int main(int argc, char **argv, char **envp)
{
	int res;
	char buffer[256];
	sprintf(buffer, "%.255s",argv[0]);
	unsigned long * frame = __builtin_frame_address(0);
	unsigned long * tls;
        res = arch_prctl(ARCH_GET_FS, &tls);

	unsigned long * addr = mmap(0, 8 * 4096 *4096, 3, MAP_ANON | MAP_PRIVATE, -1, 0);
	if (addr == MAP_FAILED)
	{
		printf("failed mmap, sorry\n");
		return -1;
	}
	printf("TLS %p , FRAME %p\n", tls, frame);
	printf(" stack cookie: 0x%lx, from tls 0x%lx\n", frame[-1], tls[5]); 
	printf("from mmap to TLS: 0x%lx\n", (char *)tls - (char*)addr);
	unsigned long diff = tls - addr;
	tcbhead_t *head = (tcbhead_t*)&addr[diff];
	printf("cookie from addr: 0x%lx\n", head->stack_guard);
	printf("cookie == stack_cookie? %d\n", head->stack_guard == frame[-1]);
	return 0;
}

