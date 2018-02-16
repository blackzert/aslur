all:	
	gcc big_heap_thread_stack_constant.c -o big_heap_thread_stack_constant -lpthread
	gcc mmap_tls_constant.c -o mmap_tls_constant -lpthread
	gcc threads_stack_constant.c -o threads_stack_constant -lpthread
	gcc thread_stack_big_heap.c -o thread_stack_big_heap -lpthread
	gcc thread_stack_small_heap.c -o thread_stack_small_heap -lpthread
	gcc thread_stack_mmap_constant.c -o thread_stack_mmap_constant -lpthread
	gcc thread_stack_tls.c -g -o thread_stack_tls -lpthread	
	gcc multy_thread_stack_tls.c -g -o multy_thread_stack_tls -lpthread	
	gcc mmap_libc.c -o mmap_libc -ldl
	gcc pthread_cache.c -g -o pthread_cache -lpthread
	gcc self_maps.c -o self_maps -fPIE -fpie -pie

#gcc -fstack-protector-all -g 3.1.c -lpthread -o 3.1
