"""Pre-link gate: every symbol the SUSFS kernel patch declares `extern` must be DEFINED somewhere
that will be linked (fs/susfs.c, the files the patch touches, or KernelSU-Next/kernel).
Catches the 'ld.lld: undefined symbol: susfs_*' class *before* a 6-25 minute compile.
Dipanggil dari workflow (Apply SUSFS Patches), setelah patch diterapkan:
    python3 scripts/check_susfs_externs.py <patch-file> <KernelSU-Next/kernel>   (cwd = tree kernel ter-patch)
Riwayat CI: dua run gagal di link akhir ('undefined symbol: susfs_open_redirect_spoof_*')
setelah ~25 menit; gerbang ini menangkap kelas itu dalam hitungan detik."""
import os, re, sys

patch_path, ksun_dir = sys.argv[1], sys.argv[2]
patch = open(patch_path, encoding="utf-8", errors="replace").read()

touched = sorted(set(re.findall(r"^\+\+\+ b/(\S+)", patch, re.M)))
# extern declarations on ADDED lines (may span lines: join until ';')
added = "\n".join(l[1:] for l in patch.splitlines() if l.startswith("+") and not l.startswith("+++"))
decls = re.findall(r"\bextern\b([^;{}]*?);", added, re.S)
funcs, vars_ = set(), set()
for d in decls:
    d = " ".join(d.split())
    m = re.search(r"\b([A-Za-z_]\w*)\s*\(", d)
    if m and not re.search(r"\(\s*\*", d):          # function prototype (not a function pointer var)
        funcs.add(m.group(1))
    else:
        m = re.search(r"\b([A-Za-z_]\w*)\s*(?:\[[^\]]*\])?\s*(?:__\w+\s*)*$", d)
        if m:
            vars_.add(m.group(1))

# Corpus where definitions may live.
corpus_files = ["fs/susfs.c"] + [f for f in touched if os.path.isfile(f)]
for root, dirs, files in os.walk(ksun_dir):
    # kernel/susfs/ = varian LKM KernelSU-Next; Kbuild tidak mengompilasinya in-tree, jadi
    # definisi di sana TIDAK ikut link dan tidak boleh memuaskan gerbang ini.
    dirs[:] = [d for d in dirs if not (os.path.basename(root.rstrip("/")) == "kernel" and d == "susfs")]
    corpus_files += [os.path.join(root, f) for f in files if f.endswith(".c")]
corpus = []
for f in dict.fromkeys(corpus_files):
    try:
        corpus.append(open(f, encoding="utf-8", errors="replace").read())
    except OSError:
        pass
text = "\n".join(corpus)
# Drop comments so a commented-out definition does not count.
text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
text = re.sub(r"//[^\n]*", "", text)


def func_defined(name):
    # a definition: name( ... ) followed by '{' (possibly after attributes / newline), on a non-extern line
    pat = re.compile(r"^(?!\s*extern\b)[^\n;#]*\b" + re.escape(name) + r"\s*\([^;{]*\)\s*(?:__\w+(?:\([^)]*\))?\s*)*\{", re.M)
    return bool(pat.search(text))


def var_defined(name):
    pats = [
        # DEFINE_SRCU / DEFINE_MUTEX / DEFINE_STATIC_KEY_{TRUE,FALSE} / DEFINE_PER_CPU(type, name) ...
        # ("STATIC" di DEFINE_STATIC_KEY_* = static key, simbolnya tetap global). DEFINE_STATIC_SRCU
        # benar-benar static storage -> tidak terlihat linker, jadi dikecualikan.
        r"\bDEFINE_(?!STATIC_SRCU\b)[A-Z_]+\s*\((?:[^()]*,)?\s*" + re.escape(name) + r"\s*[,)]",
        r"^(?!\s*extern\b)(?!\s*static\b)[^\n;()#]*\b" + re.escape(name) + r"\b\s*(?:\[[^\]]*\])?\s*(?:__\w+\s*)*(?:=|;)",
    ]
    return any(re.search(p, text, re.M) for p in pats)


missing = sorted([f"{n}()" for n in funcs if not func_defined(n)] + [n for n in vars_ if not var_defined(n)])
print(f"[gate] patch declares {len(funcs)} extern functions + {len(vars_)} extern variables; corpus {len(corpus)} files")
if missing:
    for m in missing:
        print(f"::error::Patch SUSFS mendeklarasikan extern {m} tetapi tidak ada definisinya (fs/susfs.c / file ter-patch / KernelSU-Next) -> 'undefined symbol' saat link.")
    sys.exit(1)
print("[gate] OK: semua extern dari patch SUSFS punya definisi.")
