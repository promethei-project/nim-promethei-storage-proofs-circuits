#!/usr/bin/env python3
"""Build the circuit archive whose sha256 is published as the zkey hash.

Usage: make_archive.py <dir-with-artifacts> <out.tar.gz>

The archive is built deterministically - members sorted, metadata zeroed,
GNU tar format, gzip header without a name and with mtime 0 - so the sha256
depends only on the artifact bytes. The digest is printed; it is the value
recorded in zkey_hash.json and advertised on chain.
"""
import gzip
import hashlib
import io
import os
import sys
import tarfile

MEMBERS = [
    "proof_main.bin",
    "proof_main.r1cs",
    "proof_main.wasm",
    "proof_main.zkey",
    "proof_main_verification_key.json",
]


def build(src: str, out: str) -> str:
    raw = io.BytesIO()
    gz = gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0)
    tf = tarfile.open(fileobj=gz, mode="w", format=tarfile.GNU_FORMAT)
    for name in sorted(MEMBERS):
        ti = tf.gettarinfo(os.path.join(src, name), arcname=name)
        ti.mtime = 0
        ti.uid = 0
        ti.gid = 0
        ti.uname = ""
        ti.gname = ""
        ti.mode = 0o644
        with open(os.path.join(src, name), "rb") as fh:
            tf.addfile(ti, fh)
    tf.close()
    gz.close()

    data = raw.getvalue()
    with open(out, "wb") as fh:
        fh.write(data)
    return hashlib.sha256(data).hexdigest()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    print(build(sys.argv[1], sys.argv[2]))
