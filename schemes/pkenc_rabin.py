'''
| From: "Digitalized Signatures and Public-Key Functions as Intractable as Factorization".
| Published in: 1979
| Security Assumption: Integer Factorization

* type:           public-key encryption
* setting:        Integer

:Authors: Christina Garman
:Date:            09/2011
'''
from __future__ import print_function
from charm.integer import integer,isPrime,gcd,random,randomPrime
from toolbox.PKEnc import PKEnc
from toolbox.PKSig import PKSig
from toolbox.paddingschemes import OAEPEncryptionPadding,PSSPadding,SAEPEncryptionPadding
from toolbox.redundancyschemes import InMessageRedundancy
from toolbox.conversion import Conversion
from toolbox.bitstring import Bytes
from math import ceil, floor

debug = False
class Rabin():
    '''Rabin Module'''
    def __init__(self):
        pass
    # generate p,q and n
    def paramgen(self, secparam):
        while True:
            p = randomPrime(secparam)
            if isPrime(p) and (((p-3)%4) == 0):
                break
        while True:
            q = randomPrime(secparam)
            if isPrime(q) and (((q-3)%4) == 0) and not(q == p):
                break
        N = p * q
        yp = (p % q) ** -1
        yq = (q % p) ** -1

        return (p, yp, q, yq, N)
    
    def keygen(self, s0, secparam=1024, params=None):
        if params: 
            (N, p, q, yp, yq) = self.convert(params)
            pk = { 'N':N, 'n':secparam, 's0':s0 }
            sk = { 'p':p, 'q':q, 'N':N , 'yp':yp, 'yq':yq }
            return (pk, sk)

        (p, yp, q, yq, N) = self.paramgen(secparam)
        
        pk = { 'N':N, 'n':secparam, 's0':s0 }
        sk = { 'p':p, 'q':q, 'N':N , 'yp':yp, 'yq':yq }

        return (pk, sk)
    
    def convert(self, N, p, q, yp, yq):
        return (integer(N), integer(p), integer(q), integer(yp), integer(yq))
    
class Rabin_Enc(Rabin,PKEnc):
    def __init__(self, padding=SAEPEncryptionPadding(), redundancy=InMessageRedundancy(), params=None):
        Rabin.__init__(self)
        PKEnc.__init__(self)
        self.paddingscheme = padding 
        self.redundancyscheme = redundancy
    # m : Bytes
    def encrypt(self, pk, m, salt=None):
        if(self.paddingscheme.name == "SAEPEncryptionPadding"):
            EM = self.paddingscheme.encode(m, pk['n'], pk['s0'])
        else:
            m = self.redundancyscheme.encode(m)
            octetlen = int(ceil(int(pk['N']).bit_length() / 8.0))
            EM = self.paddingscheme.encode(m, octetlen, "", salt)

        if debug: print("EM == >", EM)
        i = Conversion.OS2IP(EM)
        ip = integer(i) % pk['N']  #Convert to modular integer

        return (ip ** 2) % pk['N']
    
    def decrypt(self, pk, sk, c):
        p = sk['p']
        q = sk['q']
        yp = sk['yp']
        yq = sk['yq']

        mp = (c ** ((p+1)/4)) % p
        mq = (c ** ((q+1)/4)) % q

        if(not(((c % p) == (mp ** 2)) and ((c % q) == (mq ** 2)))):
            assert False, "invalid ciphertext"

        r1 = ((int(yp)*int(p)*int(mq)) + ((int(yq)*int(q)*int(mp)))) % int(sk['N'])
        r2 = int(sk['N']) - int(r1)

        s1 = (int(yp)*int(p)*int(mq) - int(yq)*int(q)*int(mp)) % int(sk['N'])
        s2 = int(sk['N']) - int(s1)

        m1 = r1 % int(sk['N'])
        m2 = r2 % int(sk['N'])
        m3 = s1 % int(sk['N'])
        m4 = s2 % int(sk['N'])

        if(self.paddingscheme.name == "SAEPEncryptionPadding"):        
            if(m1 < int(sk['N']/2)):
                os1 = Conversion.IP2OS(int(m1))
                if(m2 < int(sk['N']/2)):
                    os2 = Conversion.IP2OS(int(m2))
                else:
                    if(m3 < int(sk['N']/2)):
                        os2 = Conversion.IP2OS(int(m3))
                    else:
                        os2 = Conversion.IP2OS(int(m4))
            else:
                if(m2 < int(sk['N']/2)):
                    os1 = Conversion.IP2OS(int(m2))
                    if(m3 < int(sk['N']/2)):
                        os2 = Conversion.IP2OS(int(m3))
                    else:
                        os2 = Conversion.IP2OS(int(m4))
                else:
                    os1 = Conversion.IP2OS(int(m3))
                    os2 = Conversion.IP2OS(int(m4))
                
            if debug:
                print("OS1  =>", os1)
                print("OS2  =>", os2)

            (m1, t1) = self.paddingscheme.decode(os1, pk['n'], pk['s0'])
            (m2, t2) = self.paddingscheme.decode(os2, pk['n'], pk['s0'])

            if((t1 == Bytes.fill(b'\x00', pk['s0']/8)) and (t2 == Bytes.fill(b'\x00', pk['s0']/8))):
                assert False, "invalid ciphertext"

            if(t1 == Bytes.fill(b'\x00', pk['s0']/8)):
                return m1
            else:
                if(t2 == Bytes.fill(b'\x00', pk['s0']/8)):
                    return m2
                else:
                    assert False, "invalid ciphertext"
        else:
            octetlen = int(ceil(int(pk['N']).bit_length() / 8.0))
            os1 = Conversion.IP2OS(int(m1), octetlen)
            os2 = Conversion.IP2OS(int(m2), octetlen)
            os3 = Conversion.IP2OS(int(m3), octetlen)
            os4 = Conversion.IP2OS(int(m4), octetlen)
            if debug:
                print("OS1  =>", os1)
                print("OS2  =>", os2)
                print("OS3  =>", os3)
                print("OS4  =>", os4)

            for i in [os1, os2, os3, os4]:
                (isMessage, message) = self.redundancyscheme.decode(self.paddingscheme.decode(i))
                if(isMessage):
                   return message        

class Rabin_Sig(Rabin, PKSig):
    '''RSASSA-PSS'''
    def __init__(self, padding=OAEPEncryptionPadding()):
        Rabin.__init__(self)
        PKSig.__init__(self)
        self.paddingscheme = padding 

    def sign(self,sk, M, salt=None):
        #apply encoding

        while True:
            octetlen = int(ceil(int(sk['N']).bit_length() / 8.0))
            em = self.paddingscheme.encode(M, octetlen, "", salt)

            m = Conversion.OS2IP(em)
            m = integer(m) % sk['N']  #ERRROR m is larger than N
      
            p = sk['p']
            q = sk['q']
            yp = sk['yp']
            yq = sk['yq']

            mp = (m ** ((p+1)/4)) % p
            mq = (m ** ((q+1)/4)) % q

            r1 = ((int(yp)*int(p)*int(mq)) + ((int(yq)*int(q)*int(mp)))) % int(sk['N'])
            r2 = int(sk['N']) - int(r1)

            s1 = (int(yp)*int(p)*int(mq) - int(yq)*int(q)*int(mp)) % int(sk['N'])
            s2 = int(sk['N']) - int(s1)

            if(((int((integer(r1) ** 2) % sk['N'] - m)) == 0) or ((int((integer(r2) ** 2) % sk['N'] - m)) == 0) or ((int((integer(s1) ** 2) % sk['N'] - m)) == 0) or ((int((integer(s2) ** 2) % sk['N'] - m)) == 0)):
                break

        S = { 's1':r1, 's2':r2, 's3':s1, 's4':s2 }

        if debug:
            print("Signing")
            print("m     =>", m)
            print("em    =>", em)
            print("S     =>", S)

        return S
    
    def verify(self, pk, M, S, salt=None):
        #M = b'This is a malicious message'

        octetlen = int(ceil(int(pk['N']).bit_length() / 8.0))

        sig_mess = (integer(S['s1']) ** 2) % pk['N']
        sig_mess = Conversion.IP2OS(int(sig_mess), octetlen)
        if debug: print("OS1  =>", sig_mess)
        dec_mess = self.paddingscheme.decode(sig_mess)

        if debug:
            print("Verifying")
            print("sig_mess     =>", sig_mess)
            print("dec_mess    =>", dec_mess)
            print("S     =>", S)

        return (dec_mess == M)
    
def main():
    rabin = Rabin_Enc()
    
    (pk, sk) = rabin.keygen(128, 1024)
    
    m = b'This is a test'
    #m = 55
    #m = b'A'
    c = rabin.encrypt(pk, m)
    if debug: print("ct =>", c)
    
    orig_m = rabin.decrypt(pk, sk, c)
    if debug: print("recovered m =>", orig_m)

    assert m == orig_m
    if debug: print("Successful Decryption!!!")
    
def main2():
    M = b'This is a test message.'
    rabin = Rabin_Sig()
    (pk, sk) = rabin.keygen(1024)
    S = rabin.sign(sk, M)
    assert rabin.verify(pk, M, S)
    if debug: print("Successful Signature!")
        
if __name__ == "__main__":
    debug = True
    main()
    main2()    
