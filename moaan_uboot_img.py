#!/usr/bin/env python3

# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "fdt",
# ]
# ///

# minimal hack'n'slash of https://github.com/DorianRudolph/pinenotes/blob/main/py/uboot_img.py
# by panicopticon 20240721

import sys
from hashlib import sha256
from pathlib import Path
from typing import TypedDict

import fdt

SZ = 0x200000


class ParsedBootImg(TypedDict):
    ub: fdt.Node
    sz: int
    pos: int


def parse_boot_img(img: bytes) -> ParsedBootImg:
    assert img[SZ:] == img[:SZ]  # the uboot image contains the same data two times
    dt = fdt.parse_dtb(img[:SZ])
    print(dt.to_dts())
    ub = dt.get_node("images/uboot")
    sz = ub.get_property("data-size").value
    print(f"sz = 0x{sz:x}")
    pos = ub.get_property("data-position").value
    print(f"pos = 0x{pos:x}")
    return ParsedBootImg(ub=ub, sz=sz, pos=pos)


def check_hash_and_dump(fin: Path, fout: Path, *, dump: bool = False) -> None:
    with fin.open("rb") as f:
        img = f.read()

    ret = parse_boot_img(img)
    ub = ret["ub"]
    sz = ret["sz"]
    pos = ret["pos"]

    h = ub.get_subnode("hash").get_property("value")
    hash_hex = "".join(f"{i:08x}" for i in h)
    uboot_bin = img[pos : pos + sz]
    assert hash_hex == sha256(uboot_bin).hexdigest()
    if dump:
        with fout.open("wb") as f:
            f.write(uboot_bin)

    sys.exit(0)


def patch(uboot_a: Path, fin: Path, fout: Path) -> None:
    # patch manually instead of using fdt to keep the differences minimal
    # since we reparse the boot_a anyway, just read extract them from it
    # sz = 0x128288
    # sz = 0x129ab0
    # pos = 0xe00

    with uboot_a.open("rb") as f:
        img = f.read()

    ret = parse_boot_img(img)
    sz = ret["sz"]
    pos = ret["pos"]

    h = sha256(img[pos : pos + sz]).digest()
    hash_offset = img.find(h)
    assert hash_offset > 0

    with fin.open("rb") as f:
        uboot_patched = f.read()
    assert len(uboot_patched) == sz
    h2 = sha256(uboot_patched).digest()

    img2 = bytearray(img[:SZ])
    img2[pos : pos + sz] = uboot_patched
    img2[hash_offset : hash_offset + len(h)] = h2

    with fout.open("wb") as f:
        f.write(img2)
        f.write(img2)

    sys.exit(0)


def print_help() -> None:
    print("To dump: ")
    print(f"{sys.argv[0]} d uboot_a.img uboot.bin")
    print("   Extract u-boot.bin from u-boot.img for patching")
    print("\nTo Repack:")
    print(f"{sys.argv[0]} p uboot_a.img uboot-patched.bin uboot-patched.img")
    print("   Take in original uboot_a, manually created uboot-patched.bin, then recompute hashes,")
    print("    replace both uboots in uboot_a with patched version while keeping original dtb, and")
    print("    output as uboot-patched.img for flashing")
    sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print_help()

    img_path = Path(sys.argv[2])
    if not img_path.exists():
        print(f".img File not found: {img_path}")
        sys.exit(1)

    if sys.argv[1] == "d":
        check_hash_and_dump(img_path, Path(sys.argv[3]), dump=True)
    elif sys.argv[1] == "p":
        bin_path = Path(sys.argv[3])
        if not bin_path.exists():
            print(f".bin File not found: {img_path}")
            sys.exit(1)

        patch(img_path, bin_path, Path(sys.argv[4]))
    else:
        print_help()
