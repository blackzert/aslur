#include <stdio.h>
#include <stdlib.h>
#include <inttypes.h>

int main() {
	long len;
	long offset;
	unsigned long value;
	char c;
	printf("This is a simple example how to use hole in ld to bypass aslr\n");
	printf("First we get length of array\n");
	scanf("%"SCNu64,&len);
	unsigned long *ptr = malloc(len);
	printf("%p\n", ptr);

	while (1) {
		printf("Now lets use this array to read/write values. Read or Write?\n");

		scanf("%c", &c);
		switch(c) {
			case 'r':
				scanf("%"SCNi64, &offset);
				if (offset > len)
					printf("too big\n");
				else
					printf("%llx\n", *(unsigned long *)((char*)ptr + offset));
			break;
			case 'w':
				scanf("%"SCNi64" %"SCNi64, &offset, &value);
				if (offset > len)
					printf("too big\n");
				else
					ptr[offset] = value;
			break;
			case '\n':
				break;
			default:
				goto finish;
			break;
		}
	}

finish:
	free(ptr);
	printf("Bye.\n");
}