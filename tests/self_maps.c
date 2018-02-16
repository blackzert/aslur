#include <stdio.h>

int main() {
	char buffer[65536];
	int fd = open("/proc/self/maps", 0);
	int size = read(fd, buffer, sizeof(buffer));
	write(1, buffer, size);
	return 0;
}
