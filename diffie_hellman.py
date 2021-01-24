import gensafeprime
from random import randint
from pyDes import *
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

def generate_diffie_hellman_key(n = 128):
    p = 307662152597849524039519709992560403259
    print("Prime: ",p)
    # print("Prime p = "+str(p.to_bytes(32, byteorder='little')))
    x_a = randint(p - 100, p)
    x_b = randint(p - 100, p)
    g = get_generator(p)
    print("gen: ", g)
    y_a = power(g, x_a, p)
    y_b = power(g, x_b, p)
    z_a = power(y_b, x_a, p)
    z_b = power(y_a, x_b, p)
    return z_a, z_a

# def 
# print(z_a.to_bytes(24, byteorder='little'))
data = "Please encrypt my data"
key, key1 = generate_diffie_hellman_key()
print(key)
key = key.to_bytes(24, byteorder='little')
# s = "hi"
# try:
#     print(int.from_bytes(s, byteorder='little'))
# except:
#     print(s)
print(bytes("str" + str(key), "UTF-8"))
k = triple_des(key, CBC, "\0\0\0\0\0\0\0\0", pad=None, padmode=PAD_PKCS5)
d = k.encrypt(data)
# print(d.decode("utf-8"))
print("Encrypted: %r" % d)
print("Decrypted: %r" % k.decrypt(d))
decrypt = k.decrypt(d, padmode=PAD_PKCS5)
print(str(decrypt, 'UTF-8'))
key1 = key1.to_bytes(24, byteorder='little')
k = triple_des(key1, CBC, "\0\0\0\0\0\0\0\0", pad=None, padmode=PAD_PKCS5)
# d = k.encrypt(d)
# print("Encrypted: %r" % d)
decrypt = k.decrypt(d, padmode=PAD_PKCS5)
# print("Decrypted: %r" % decrypt)
string = decrypt.decode("utf-8")
print(string)
# print(z_a == z_b)
# print(x_a, x_b, g)


p1 = 16727283276457562652997044783833787842
p2 = 129787760104914998891142915104634395893
s1 =   278058185418413002133391287334001250517
# Shared secret key:  173198417211247415393525082667749659551

# Received key:  16727283276457562652997044783833787842
# Public key to send:  129787760104914998891142915104634395893
s2 = 290766323582678362961171322658497798455
# print(pow(p1, s2, ))
# Shared secret key:  255808485053107039399392902579611056910


