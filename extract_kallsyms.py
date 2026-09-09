#!/usr/bin/env python3
import sys, os

def extract_offsets(img_path, map_path):
    if not os.path.exists(img_path):
        print(f"# Image not found: {img_path}", file=sys.stderr)
        return
    if not os.path.exists(map_path):
        print(f"# System.map not found: {map_path}", file=sys.stderr)
        return

    with open(img_path, "rb") as f:
        img_bytes = f.read()

    # Detect EFI MZ header and fix if needed
    if len(img_bytes) >= 8 and img_bytes[0:4] == b'\x1f\x20\x03\xd5' and (img_bytes[7] & 0xfc) == 0x14:
        print("[+] Terdeteksi Image ARM64 non-EFI, menyesuaikan header dengan EFI MZ...", file=sys.stderr)
        with open(img_path, "r+b") as f:
            f.seek(0)
            f.write(b'\x4d\x5a\x40\xfa')
            f.flush()

    banner_pos = img_bytes.find(b"Linux version ")
    if banner_pos == -1:
        print("# linux_banner not found in Image", file=sys.stderr)
        return

    syms = {}
    with open(map_path, "r", errors="ignore") as mf:
        for line in mf:
            parts = line.strip().split()
            if len(parts) >= 3 and parts[2] in (
                "linux_banner",
                "kallsyms_token_table",
                "kallsyms_token_index",
                "kallsyms_markers",
                "kallsyms_names",
                "kallsyms_num_syms",
                "kallsyms_offsets",
                "kallsyms_addresses"
            ):
                syms[parts[2]] = int(parts[0], 16)

    if "linux_banner" not in syms:
        print("# linux_banner not found in System.map", file=sys.stderr)
        return

    va_offset = syms["linux_banner"] - banner_pos
    print(f"# Kernel VA offset: 0x{va_offset:016x} (banner VA 0x{syms['linux_banner']:016x}, file offset 0x{banner_pos:08x})", file=sys.stderr)

    for k in (
        "kallsyms_token_table",
        "kallsyms_token_index",
        "kallsyms_markers",
        "kallsyms_names",
        "kallsyms_num_syms",
        "kallsyms_offsets",
        "kallsyms_addresses"
    ):
        if k in syms:
            fo = syms[k] - va_offset
            env_name = k.upper() + "_OFFSET"
            print(f"export {env_name}=0x{fo:08x}")
            print(f"# {k} file offset: 0x{fo:08x}", file=sys.stderr)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: extract_kallsyms.py <Image> <System.map>", file=sys.stderr)
        sys.exit(1)
    extract_offsets(sys.argv[1], sys.argv[2])
