import gensafeprime
from random import randint
# Code for generating P,G for diffie-hellman key
def power(x, y, p) : 
    res = 1   
    x = x % p  
    if (x == 0) : 
        return 0
    while (y > 0) : 
        if ((y & 1) == 1) : 
            res = (res * x) % p 
        # y must be even now 
        y = y >> 1      # y = y/2 
        x = (x * x) % p 
          
    return res 

def get_generator(p):
    one = 1
    gen = 0
    while one == 1:
        gen = randint(2, p-2)
        one = power(gen, 2, p)
    return gen

def generate_pg(n = 128):
    p = gensafeprime.generate(n)
    print("Prime: ",p)
    g = get_generator(p)
    print("Generator: ", g)

generate_pg()
