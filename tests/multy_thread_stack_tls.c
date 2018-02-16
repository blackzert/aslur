#include <pthread.h>
#include <stdlib.h>
#include <stdio.h>
#include <errno.h>
#include <sys/mman.h>
#include <asm/prctl.h>
#include <sys/prctl.h>

pthread_mutex_t lock;

void * func(void *x)
{
	pthread_mutex_lock(&lock);
	int a = (int)x;
	unsigned long *addr;
	int res = arch_prctl(ARCH_GET_FS, &addr);
	if (res < 0)
	{
		printf("Failed get thread FS, sorry\n");
	}
	printf("thread FS %p\n", addr);
	printf("cookie thread: 0x%lx\n", addr[5]);
	unsigned long * frame = __builtin_frame_address(0);
	printf("stack_cookie addr %p \n", &frame[-1]);
	printf("diff : %lx\n", (char*)addr - (char*)&frame[-1]); 
	unsigned long len =(unsigned long)( (char*)addr - (char*)&frame[-1]);
	pthread_mutex_unlock(&lock);
	return 0;
}

#define threads_count 20

int main(int argc, char **argv, char **envp)
{
        int res;
	unsigned long *addr;
	res = arch_prctl(ARCH_GET_FS, &addr);
	if (res < 0)
	{
		printf("Failed get FS, sorry\n");
		return -1;
	}

	printf("main FS %p\n", addr);
	printf("cookie main: 0x%lx\n", addr[5]);
	if (pthread_mutex_init(&lock, NULL) != 0)
	{
		printf("\n mutex init failed\n");
		return 1;
	}


	pthread_t list[threads_count];
	
	// First create many threads and make them to wait
	pthread_mutex_lock(&lock);
	for(int i =0; i < threads_count; ++i)
	{
		res = pthread_create(&list[i], NULL, func, 0);
		if (res)
		{
			printf("Failed create thread %d\n", errno);
			return -1;
		}
		printf("started thread %d\n", i);
	}
	pthread_mutex_unlock(&lock);
	//release threads and let them do the job
	for (int i =0; i < threads_count; ++i)
	{
		void *val;
		// wait each thread to finish
		pthread_join(list[i],&val);
	}
        
	return 0;
}

