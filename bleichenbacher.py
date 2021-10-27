import os
import base64
from base64 import b64encode, b64decode
import sys
import json
import getopt
import requests

checks=0
c=0

e=0
n=0

def ceil(a,b):
    return (a//b + ((a%b)>0))

def int_to_bytes(n):
    return n.to_bytes((n.bit_length() + 7) // 8, 'big')

def bytes_to_int(bytes):
    return int.from_bytes(bytes, 'big')

def base64_to_int(base64_string):
    base64_bytes = base64_string.encode('ascii')
    bytes = b64decode(base64_bytes)
    return bytes_to_int(bytes)

def extract(m):
    m = int_to_bytes(m)
    a = m.find(b'\x00')
    m = m[a+1:].decode('utf-8')
    return m


def union(M):
    new = []
    M_ = sorted(M)
    for l,r in M_:
        if new and new[-1][1] >= l - 1:
            new[-1] = (new[-1][0], r)
        else:
            new.append((l, r))
    return new

def check(cipher):
    global checks
    header = {'Accept': 'application/json',
              'Content-type': 'application/json'}    
    cipher = base64.b64encode(int_to_bytes(cipher)).decode('utf-8')
    url="http://127.0.0.1:8080"
    payload = {'message': cipher}
    r=requests.post(url,json=payload, headers=header)
    res_json=json.loads(r.text)
    result=res_json['message']
    result=b64decode(result).decode('utf-8')
    checks+=1
    return result

def step2ab(n,B,c,s,e):
    s_new = s
    while(1):
        cipher = (c * (pow(s_new,e,n))) % n
        result = check(cipher)
        if(result=="True"):
            return s_new
        else:
            s_new+=1 
    
def step2c(a,b,n,B,c,e,s):
    r=ceil( (2*b*s - 4*B),(n) )
    new_s = s   
    while(1):
        low = ceil( (2*B+r*n) , b) 
        up  = (3*B+r*n)//a - ((3*B+r*n % a) == 0)
        while(low <= up):
            new_s = low
            cipher=(c * (pow(new_s,e,n))) % n
            result = check(cipher)
            if(result=="True"):
                return new_s
            else:
                low+=1         
        r+=1 

def step3(M,B,s):
    M_new=[]
    for (a,b) in M:
        r = ceil((a*s-3*B+1) , n)
        r_end = ((b*s-2*B) // n - ((b*s-2*B) % n == 0))
        while(r <= r_end):
            
            in_begin = max(a, ceil((2*B+r*n),s) )

            in_end = min(b, (3*B-1+r*n)//s )          
            
            if(in_end >= in_begin):
                M_new.append( (in_begin,in_end) )
            r+=1
    return union(M_new)

def check_step4(M,s):
    global checks
    if(len(M)==1 and M[0][0]==M[0][1]):
        message=M[0][0]
        print(extract(message))
        print(checks)
        return 0
    return 1

def crack():
    global c, e, n
    k=8*(len(int_to_bytes(n))-2)
    B=2**k
    M=[(2*B,3*B-1)]
    s=ceil( n,(3*B) )
    loop=1
    i=1
    while(loop):
        if(i==1):
            s=step2ab(n,B,c,s,e)
        if(i>1 and len(M)>1):
            s+=1
            s=step2ab(n,B,c,s,e)
        if(i>1 and len(M)==1):
            s=step2c(M[0][0],M[0][1],n,B,c,e,s)
        M=step3(M,B,s)
        loop=check_step4(M,s)      
        i+=1
    return 0

def main(argv):
    global c, e, n
    try:
        opts, args = getopt.getopt(argv, "hc:e:n:")
    except getopt.GetoptError:
        print('bleichenbacher.py -c [path to cipher.txt] -e [path to encryption_key.txt] -n [path to modulus.txt]')
        sys.exit(1)
    for opt, arg in opts:
        if opt == '-h':
            print('usage: bleichenbacher.py -c [path to cipher.txt] -e [path to encryption_key.txt] -n [path to modulus.txt]')
            sys.exit(0)
        elif opt == '-c':
            try:
                f = open(arg, 'r')
                cc = f.read()[:-1]
                c = base64_to_int(cc)
            except:
                print('File Error')
                sys.exit(1)
        elif opt == '-e':
            try:
                f = open(arg, 'r')
                ee = f.read()[:-1]
                e = base64_to_int(ee)
            except:
                print('File Error')
                sys.exit(1)
        elif opt == '-n':
            try:
                f = open(arg, 'r')
                nn = f.read()[:-1]
                n = base64_to_int(nn)
            except:
                print('File Error')
                sys.exit(1)        


if __name__ == "__main__":
    main(sys.argv[1:])
    crack()

