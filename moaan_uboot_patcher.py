#!/usr/bin/python

# quick'n'dirty Rockchip RK3566 uboot patcher to deal with rk uboot 32M i
# security/bug that gives you all 0xCCs

# note that this is designed to only patch a uboot.bin that is identical to mine
# however it should provide some assistance in figuring out how to patch others
# good luck, we're all counting on you

# panicopticon 20240721

import re
from binascii import a2b_hex, b2a_hex
from hashlib import sha256
from sys import argv

expected_uboot_sha256 = "8d4368901b755c4c6e04749d764712ce5718ecee4e28b504f4054efeb5ede70e"
expected_patch_offset = 0x12B74
bls = "49010054"
b_patch = "0A000014"
# this target string is the same between mooan and pinenote uboot
# maybe it generalizes? skeptical
search_hex_bytes = "9F4040F149010054F30302AA81198052"
uboot_patched_sha256 = "90221930681a9ab27f64769dd6658e8e2d9c3a0f8004c8a0c4a5f70c08bfd872"


def patch( fin, fout ):

    with open(fin, 'rb') as f:
        uboot_bin = f.read()
    uboot_bin_len = len( uboot_bin )
    
    # list the match offsets for search_hex_bytes
    print( "Searching for all patch candidates:" )
    for m in re.finditer( a2b_hex( search_hex_bytes ), uboot_bin ):
        print( f"   search_hex_bytes match at {hex( m.start() )}" )

    assert expected_uboot_sha256 == sha256(uboot_bin).hexdigest()

    uboot_loc_bytes = b2a_hex( uboot_bin[ expected_patch_offset:expected_patch_offset+4 ] ).decode()
    print( f"\nOk to patch offset {hex(expected_patch_offset)}, target bytes are bytes are {uboot_loc_bytes}" )
    assert bls == uboot_loc_bytes

    img2 = uboot_bin[:expected_patch_offset] + a2b_hex( b_patch ) + uboot_bin[expected_patch_offset+4:]

    # this is not needed, but why not...
    assert len( img2 ) == uboot_bin_len
    assert uboot_patched_sha256 == sha256( img2 ).hexdigest()

    with open(fout, 'wb') as f:
        f.write( img2 )
    print( "Successful patch." )

def help():
    print( "To patch uboot.bin: ")
    print( f"{argv[0]} uboot.bin uboot-patched.bin")
    print( "\nNote that is is a very basic patcher and does not try particularly" )
    print( "hard, it may result in bricks, please confirm that it has done" )
    print( "something sane manually, you have been warned." )

if __name__ == '__main__':

    if len( argv ) == 1:
        help()
        exit()

    patch( argv[1], argv[2] )
