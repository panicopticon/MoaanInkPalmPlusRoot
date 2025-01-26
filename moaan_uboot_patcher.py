#!/usr/bin/env python3

# quick'n'dirty Rockchip RK3566 uboot patcher to deal with rk uboot 32M i
# security/bug that gives you all 0xCCs

# note that this is designed to only patch a uboot.bin that is identical to mine
# however it should provide some assistance in figuring out how to patch others
# good luck, we're all counting on you

# panicopticon 20240721

import re
import sys
from binascii import a2b_hex, b2a_hex
from hashlib import sha256
from pathlib import Path
from typing import TypedDict


class InkpalmUboot(TypedDict):
    version: str
    sha256: str
    search_hex_bytes: str
    expected_patch_offset: int
    patched_sha256: str


UBOOT_HASHES: list[InkpalmUboot] = [
    InkpalmUboot(
        version="v07",
        sha256="8D4368901B755C4C6E04749D764712CE5718ECEE4E28B504F4054EFEB5EDE70E",
        search_hex_bytes="9F4040F149010054F30302AA81198052",
        expected_patch_offset=0x12B74,
        patched_sha256="90221930681A9AB27F64769DD6658E8E2D9C3A0F8004C8A0C4A5F70C08BFD872",
    ),
    InkpalmUboot(
        version="v09",
        sha256="3EB8E08EBB33D4A040760EF1ADCE0FE329D69B6B1677613C375E80CC3FDF1478",
        search_hex_bytes="9F4040F149010054F30302AA81198052",
        expected_patch_offset=0x12B74,
        patched_sha256="C8FE02361A80A3C8CB1CF6B508179F44C09DB634737CA769A7BA5E2810ACE48B",
    ),
]

UBOOT_HASHES_BY_SHA256 = {u["sha256"]: u for u in UBOOT_HASHES}

BLS = "49010054"
B_PATCH = "0A000014"


def patch(fin: Path, fout: Path) -> None:
    with fin.open("rb") as f:
        uboot_bin = f.read()
    uboot_bin_len = len(uboot_bin)

    actual_uboot_sha256 = sha256(uboot_bin).hexdigest().upper()
    assert actual_uboot_sha256 in UBOOT_HASHES_BY_SHA256, f"Unknown uboot SHA256: {actual_uboot_sha256}"

    detected_uboot = UBOOT_HASHES_BY_SHA256[actual_uboot_sha256]
    print(f"SHA256 recognized as uboot version '{detected_uboot['version']}'")

    # list the match offsets for search_hex_bytes
    print("Searching for all patch candidates:")
    for m in re.finditer(a2b_hex(detected_uboot["search_hex_bytes"]), uboot_bin):
        print(f"   search_hex_bytes match at {hex( m.start() )}")

    expected_patch_offset = detected_uboot["expected_patch_offset"]
    uboot_loc_bytes = b2a_hex(uboot_bin[expected_patch_offset : expected_patch_offset + 4]).decode()
    print(f"\nOk to patch offset {hex(expected_patch_offset)}, target bytes are bytes are {uboot_loc_bytes}")
    assert uboot_loc_bytes == BLS

    img2 = uboot_bin[:expected_patch_offset] + a2b_hex(B_PATCH) + uboot_bin[expected_patch_offset + 4 :]

    # this is not needed, but why not...
    assert len(img2) == uboot_bin_len
    actual_patched_sha256 = sha256(img2).hexdigest().upper()
    expected_patched_sha256 = detected_uboot["patched_sha256"]
    assert (
        expected_patched_sha256 == actual_patched_sha256
    ), f"expected: {actual_patched_sha256}, actual: {actual_patched_sha256}"

    with fout.open("wb") as f:
        f.write(img2)
    print("Successful patch.")
    sys.exit(0)


def print_help() -> None:
    print("To patch uboot.bin: ")
    print(f"{sys.argv[0]} uboot.bin uboot-patched.bin")
    print("\nNote that is is a very basic patcher and does not try particularly")
    print("hard, it may result in bricks, please confirm that it has done")
    print("something sane manually, you have been warned.")
    sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print_help()

    in_path = Path(sys.argv[1])
    if not in_path.exists():
        print(f"File not found: {in_path}")
        sys.exit(1)

    patch(in_path, Path(sys.argv[2]))
