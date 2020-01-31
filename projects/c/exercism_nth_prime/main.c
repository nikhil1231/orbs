/* Licensed under MIT License from https://github.com/exercism/c/blob/master/exercises/nth-prime/src/example.c
Modified to take command line arguments and print result to stdout
 */

#include <stdbool.h>

int main(int argc, char *argv[])
{
    int result = nth(argv[1]);
    printf("The %dth prime is: %d", argv[1], result);
    return 0;
}

static bool is_prime(int n)
{
   for (int i = 2; (i * i) < (n + 1); ++i) {
      if (n % i == 0) {
         return false;
      }
   }

   return true;
}

int nth(int n)
{
   int candidate = 1;
   int count = 0;

   if (n < 1) {
      return 0;
   }

   while (count < n) {
      if (is_prime(++candidate)) {
         count++;
      }
   }

   return candidate;
}

