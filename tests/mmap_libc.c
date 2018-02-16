#define _GNU_SOURCE

#include <stdlib.h>
#include <stdio.h>
#include <errno.h>
#include <stdint.h>
#include <sys/mman.h>
#include <unistd.h>

#include <dlfcn.h>


int main(int argc, char **argv, char **envp)
{
	int res;

	system("");
	execv("", NULL);
	unsigned long  addr = (unsigned long)mmap(0, 8 * 4096 *4096, 3, MAP_ANON | MAP_PRIVATE, -1, 0);
	if (addr == MAP_FAILED)
	{
		printf("failed mmap, sorry\n");
		return -1;
	}

	unsigned long addr_system = (unsigned long)dlsym(RTLD_NEXT, "system");
	unsigned long addr_execv = (unsigned long)dlsym(RTLD_NEXT, "execv");
	
	printf("addr %lx system %lx execv %lx\n", addr, addr_system, addr_execv);
	printf("system - addr %lx execv - addr %lx\n", addr_system - addr, addr_execv - addr);
	return 0;
}

