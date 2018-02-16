

#include <pthread.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <ctype.h>

#define handle_error_en(en, msg) \
       do { errno = en; perror(msg); exit(EXIT_FAILURE); } while (0)

#define handle_error(msg) \
       do { perror(msg); exit(EXIT_FAILURE); } while (0)

struct thread_info {    /* Used as argument to thread_start() */
   pthread_t thread_id;        /* ID returned by pthread_create() */
   int       thread_num;       /* Application-defined thread # */
   char     *argv_string;      /* From command-line argument */
};

/* Thread start function: display address near top of our stack,
  and return upper-cased copy of argv_string */

static void *
thread_start(void *arg)
{
   struct thread_info *info = (struct thread_info *)arg;
   printf("sep thread(%d) has stack at %p\n", info->thread_num, &info);
   sleep(-1);

   return 0;
}


int main(int argc, char *argv[])
{
   int s, tnum, opt, num_threads, i;
   struct thread_info tinfo[10];
   pthread_attr_t attr;
   int stack_size;
   void *res;
   s = getpid();
   printf("pid %d\n", s);
   s = pthread_attr_init(&attr);
   if (s != 0)
       handle_error_en(s, "pthread_attr_init");

   /* Create one thread for each command-line argument */

   for (i =0; i < 10; ++i) {
   		tinfo[i].thread_num = i;
       s = pthread_create(&tinfo[i].thread_id, &attr,
                          &thread_start, &tinfo[i]);
       if (s != 0)
           handle_error_en(s, "pthread_create");
   }

   /* Destroy the thread attributes object, since it is no
      longer needed */

   s = pthread_attr_destroy(&attr);
   if (s != 0)
       handle_error_en(s, "pthread_attr_destroy");

   /* Now join with each thread, and display its returned value */
   sleep(-1);
   exit(EXIT_SUCCESS);
}

