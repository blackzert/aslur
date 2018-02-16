#include <pthread.h>
#include <stdlib.h>
#include <stdio.h>
#include <errno.h>



int * p_a = 0;
int * p_b = 0;


void * first(void *x)
{
	int a = (int)x;
	p_a = &a;
	sleep(1);
	return 0;
}

void *second(void *x)
{
	int b = (int)x;
	p_b = &b;
	sleep(1);
	return 0;
}

int main()
{
	int res;
	pthread_t one, two;

	res = pthread_create(&one, NULL, &first, 0);
	if (res)
	{
		printf("Failed create first %d\n", errno);
		return -1;
	}
	res = pthread_create(&two, NULL, &second, 0);
	if (res)
	{
		printf("Failed create second %d\n", errno);
		return -1;
	}
	void *val;
	pthread_join(one,&val); 
	pthread_join(two, &val);

	printf("Diff: 0x%x\n", (unsigned long)p_a - (unsigned long)p_b);
	printf("first thread stack variable: %p second thread stack vairable: %p\n", p_a, p_b);
	return 0;
}

