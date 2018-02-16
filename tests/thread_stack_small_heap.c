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
        ptr = malloc(8);
        if (ptr == 0)
        {
                printf("Failed to alloc %d\n", errno);
                return -1;
        } 
	printf("%lx\n%p, %p\n", (unsigned long long)ptr - (unsigned long long)p_a, ptr, p_a);
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

