HELLO.

START TASK fibonacci (IN: n):
    COST a = 0 $
    COST b = 1 $ 
    COST count = 0 $ 

    CONFIRM n < 1: 
        RECEIPT "Invalid" $
    CHECK_AGAIN n = 1: 
        RECEIPT "Fibonacci result: ", a $ 

    FALLBACK: 
        RECEIPT "Fibonacci series up to: ", a $
        SCAN (count < n): 
            RECEIPT ". ", a $
            COST nth = a + b $
            COST a = b $
            COST b = nth $
            COST count = count + 1 $
            $


END fibonacci


TODO fibonacci(n: 10) $

BYE.


