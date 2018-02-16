#include <pthread.h>
#include <stdlib.h>
#include <stdio.h>
#include <errno.h>
#include <sys/mman.h>
#include <asm/prctl.h>
#include <sys/prctl.h>

void * func(void *x)
{
	long a[1024];
	printf("addr: %p\n", &a[0]);
	if (x)
		printf("value %lx\n", a[0]);
	else
	{
		a[0] = 0xdeadbeef;
		printf("value %lx\n", a[0]);
	}
	void * addr = malloc(32);
	printf("malloced %p\n", addr);
	free(addr);
	return 0;
}

int main(int argc, char **argv, char **envp)
{
    int res, val;
	pthread_t thread;
	res = pthread_create(&thread, NULL, func, 0);
	if (res)
	{
		printf("Failed create thread %d\n", errno);
		return -1;
	}
	pthread_join(thread, &val);
	res = pthread_create(&thread, NULL, func, 1);
	if (res)
	{
		printf("Failed create thread %d\n", errno);
		return -1;
	}
	pthread_join(thread, &val);
	return 0;
}

