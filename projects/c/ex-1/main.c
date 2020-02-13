// example file to be sliced

#include "extras/main.h"

int main(int argc, char *argv[])
{
    if (argc != 3)
    {
        printf("Usage: prog a b\n");
        exit(1);
    }
    int a = 0;
    int b = 0;
    sscanf(argv[1], "%d", &a);
    sscanf(argv[2], "%d", &b);
    if (b > 0)
    {
        a = 7;
        for (int i = 0; i < 10; ++i)
        {
            a = a + b;
        }
    }
    else
    {
        a = 1;
    }
    printf("a = %d, b = %d\n", a, b);
}