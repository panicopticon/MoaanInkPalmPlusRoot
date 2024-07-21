#!/usr/bin/python

# minimal hack'n'slash of https://github.com/DorianRudolph/pinenotes/blob/main/py/uboot_img.py
# by panicopticon 20240721

import fdt
from hashlib import sha256
from sys import argv

SZ = 0x200000

def parse_boot_img( img ): 
    assert img[SZ:] == img[:SZ]  # the uboot image contains the same data two times
    dt = fdt.parse_dtb(img[:SZ])
    print(dt.to_dts())
    ub = dt.get_node('images/uboot')
    sz = ub.get_property('data-size').value
    print(f'sz = 0x{sz:x}')
    pos = ub.get_property('data-position').value
    print(f'pos = 0x{pos:x}')
    return( { 'ub':ub, 'sz':sz, 'pos':pos } )

def check_hash_and_dump( fin, fout, dump=False ):
    with open(fin, 'rb') as f:
        img = f.read()

    ret = parse_boot_img( img )
    ub = ret['ub']
    sz = ret['sz']
    pos = ret['pos']

    h = ub.get_subnode('hash').get_property('value')
    hash_hex = ''.join(f'{i:08x}' for i in h)
    uboot_bin = img[pos:pos + sz]
    assert hash_hex == sha256(uboot_bin).hexdigest()
    if dump:
        with open(fout, 'wb') as f:
            f.write(uboot_bin)


def patch( boot_a, fin, fout ):  # patch manually instead of using fdt to keep the differences minimal

    # since we reparse the boot_a anyway, just read extract them from it
    #sz = 0x128288
    #sz = 0x129ab0
    #pos = 0xe00
    
    with open(boot_a, 'rb') as f:
        img = f.read()
    
    ret = parse_boot_img( img )
    sz = ret['sz']
    pos = ret['pos']

    h = sha256(img[pos:pos + sz]).digest()
    hash_offset = img.find(h)
    assert hash_offset > 0

    with open(fin, 'rb') as f:
        uboot_patched = f.read()
    assert len(uboot_patched) == sz
    h2 = sha256(uboot_patched).digest()

    img2 = bytearray(img[:SZ])
    img2[pos:pos + sz] = uboot_patched
    img2[hash_offset:hash_offset + len(h)] = h2

    with open(fout, 'wb') as f:
        f.write(img2)
        f.write(img2)

def help():
    print( "To dump: ")
    print( f"{argv[0]} d uboot_a.img uboot.bin")
    print( f"   Extract u-boot.bin from u-boot.img for patching" )
    print( "\nTo Repack:" )
    print( f"{argv[0]} p boot_a uboot-patched.bin uboot-patched.img")
    print( f"   Take in original boot_a, manually created uboot-patched.bin, then recompute hashes," )
    print( "    replace both uboots in boot_a with patched version while keeping original dtb, and" )
    print( "    output  as uboot-patched.img for flashing" )
    exit( 1 )

if __name__ == '__main__':

    if len( argv ) == 1:
        help()

    if argv[1] == 'd':
        check_hash_and_dump( argv[2], argv[3], dump=True )
    elif argv[1] == 'p':
        patch( argv[2], argv[3], argv[4] )
    else:
        help()

