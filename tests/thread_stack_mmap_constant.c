#include <pthread.h>
#include <stdlib.h>
#include <stdio.h>
#include <errno.h>
#include <sys/mman.h>

void * first(void *x)
{
	int a = (int)x;
	int *p_a = &a;
	void *ptr;
	ptr = mmap(0, 8 * 4096 *4096, 3, MAP_ANON | MAP_PRIVATE, -1, 0);
	if (ptr == MAP_FAILED)
	{
		printf("Failed to mmap %d\n", errno);
		return -1;
	}
	printf("%lx\n%p, %p\n", (unsigned long long)p_a - (unsigned long long)ptr, ptr, p_a);
	return 0;
}

int main()
{
	int res;
	pthread_t one;

	res = pthread_create(&one, NULL, &first, 0);
	if (res)
	{
		printf("Failed create thread %d\n", errno);
		return -1;
	}
	void *val;
	pthread_join(one,&val); 
	return 0;
}

