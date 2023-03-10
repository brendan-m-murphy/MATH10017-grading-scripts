#include <stdio.h>

// write num_factors function below. 
// two inputs, i > j > 1
// one integer output. 
int count = 0;
int num_factors(int i, int j)
    {
        if(i > j && j > i)
        (
            if(i%j==0)
            {
                return 1 + num_factors(i, j-1);
            }else
            {
                return num_factors(i, j-1);
            }

            )
           return 0;
        }

void main()
{
    // test your num_factors below with different i, j
    // for example, 
    // printf("%d\n", num_factors(16, 5));
    for(int i; i >1 && i<=100; i++)
    {
        if(num_factors(i,2)==0)
        {
            printf("%d \n", i);
        }
    }
}