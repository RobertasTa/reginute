# -*- coding: utf-8 -*-
r"""Generates hf/samples/speaker_0.mp3 the same way the catalogue does
(rhasspy/piper-samples/_script/generate-samples.sh):

    head -n1 test_sentences/lt.txt | python3 -m piper --model X --output_raw \
        | ffmpeg -f s16le -ac 1 -sample_rate 22050 -i - -codec:a libmp3lame -qscale:a 2 speaker_0.mp3

The only difference: Piper here is the PR branch (PhonemeType.LITHUANIAN) with
the stress dictionary resolved through --data-dir, because plain Piper feeds a
`text` voice raw letters. After writing the mp3 it rewrites hf/SHA256SUMS, so
the package stays provably identical to what goes to Hugging Face.

Run with the PR venv, AFTER sudaryk_paketa.py:
    _darbal\pr_venv\Scripts\python.exe sample_speaker0.py
"""
import argparse
import hashlib
import io
import os
import shutil
import subprocess
import sys
import wave

sys.stdout.reconfigure(encoding="utf-8")
CIA = os.path.dirname(os.path.abspath(__file__))
HF = os.path.join(CIA, "hf")
VARDAS = "lt_LT-reginute1-medium"
PR_PY = r"D:\_Balsas Lietuviksas\_darbal\pr_venv\Scripts\python.exe"
DATA_DIR = r"D:\_Balsas Lietuviksas\_darbal\pr_testas"          # <data_dir>/lithuanian/lt_kirciai.tsv
PR_CONFIG = os.path.join(DATA_DIR, VARDAS + ".onnx.json")        # phoneme_type: lithuanian
LT_TXT = os.path.join(CIA, "lt.txt")                             # the same file goes to piper-samples
FFMPEG = "ffmpeg"


def sha256(kelias):
    h = hashlib.sha256()
    with open(kelias, "rb") as f:
        for gab in iter(lambda: f.read(1 << 20), b""):
            h.update(gab)
    return h.hexdigest()


def perrasyk_sha256sums():
    eilutes = []
    for saknis, _, failai in os.walk(HF):
        for fn in sorted(failai):
            if fn == "SHA256SUMS":
                continue
            pilnas = os.path.join(saknis, fn)
            sant = os.path.relpath(pilnas, HF).replace("\\", "/")
            eilutes.append(f"{sha256(pilnas)}  {sant}")
    with io.open(os.path.join(HF, "SHA256SUMS"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(eilutes) + "\n")
    print("SHA256SUMS perrašytas:", len(eilutes), "failų")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--onnx", default=os.path.join(HF, VARDAS + ".onnx"))
    ap.add_argument("--out", default=os.path.join(HF, "samples", "speaker_0.mp3"))
    ap.add_argument("--keep-wav", action="store_true")
    ap.add_argument("--no-sums", action="store_true", help="neperrašyti SHA256SUMS (bandymams)")
    a = ap.parse_args()

    # The PR data-dir must carry the SAME dictionary as the package tooling.
    src_tsv = os.path.join(CIA, "lt_kirciai.tsv")
    dst_tsv = os.path.join(DATA_DIR, "lithuanian", "lt_kirciai.tsv")
    if sha256(src_tsv) != sha256(dst_tsv):
        shutil.copyfile(src_tsv, dst_tsv)
        print("lt_kirciai.tsv atnaujintas pr_testas/lithuanian/")

    with io.open(LT_TXT, encoding="utf-8") as f:
        sentence = f.readline().strip()          # head -n1
    print("Sakinys:", sentence)

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    # The wav lives OUTSIDE hf/ - anything inside hf/ ships (and lands in SHA256SUMS).
    wav = os.path.join(r"D:\_Balsas Lietuviksas\_darbal", "speaker_0_sample.wav")
    cmd = [PR_PY, "-m", "piper", "-m", a.onnx, "-c", PR_CONFIG, "--data-dir", DATA_DIR,
           "--output-file", wav]
    r = subprocess.run(cmd, input=sentence.encode("utf-8"), capture_output=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr.decode("utf-8", "replace"))
        sys.exit("piper nepavyko")
    with wave.open(wav) as w:
        dur = w.getnframes() / w.getframerate()
        sr = w.getframerate()
    print(f"wav: {dur:.1f} s, {sr} Hz")

    r = subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "warning", "-y", "-i", wav,
                        "-codec:a", "libmp3lame", "-qscale:a", "2", a.out], capture_output=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr.decode("utf-8", "replace"))
        sys.exit("ffmpeg nepavyko")
    if not a.keep_wav:
        os.remove(wav)
    print(f"mp3: {a.out} ({os.path.getsize(a.out)} B)")
    if not a.no_sums and os.path.abspath(a.out).startswith(os.path.abspath(HF)):
        perrasyk_sha256sums()


if __name__ == "__main__":
    main()
