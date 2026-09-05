# Package builder: assembles the `hf/` directory from the best training
# checkpoint - exactly the set of files that goes both to the server and to
# Hugging Face, so that what was tested is what is shipped.
#
# Why a tool rather than doing it by hand:
#   1. the best checkpoint is chosen by val_mel across ALL training runs, not
#      by taking the newest .onnx - those are not the same thing, and picking
#      the newest once sent out a worse model than the one already on disk;
#   2. the `.onnx.json` is built from the training config plus the fields the
#      official catalogue uses (audio.quality, language{...}, dataset,
#      inference), so that nobody downstream has to edit it by hand;
#   3. SHA256SUMS, so the package, the server and Hugging Face are provably
#      the same bytes.
#
# Run it with the TRAINING environment (it needs piper.train for the export):
#   python sudaryk_paketa.py
#   python sudaryk_paketa.py --onnx <path to a specific .onnx>
#   python sudaryk_paketa.py --length-scale 1.30
#
# The default length_scale used to be 1.25 while the agreed speed was 1.30,
# so running this without arguments would have quietly produced a package at
# the old speed.
import argparse
import glob
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
BAZE = r"D:\_Balsas Lietuviksas"
SRC = os.path.join(BAZE, "_irankiai", "piper1-gpl", "src")
PY = os.path.join(BAZE, ".venv", "Scripts", "python.exe")
KONFIG = os.path.join(BAZE, "_duomenys", "regina", "regina_priegaides.json")
CIA = os.path.dirname(os.path.abspath(__file__))
HF = os.path.join(CIA, "hf")
VARDAS = "lt_LT-reginute1-medium"

LANGUAGE = {
    "code": "lt_LT",
    "family": "lt",
    "region": "LT",
    "name_native": "Lietuvių",
    "name_english": "Lithuanian",
    "country_english": "Lithuania",
}


def geriausias_ckpt():
    k = []
    for kelias in glob.glob(os.path.join(BAZE, "lightning_logs", "version_*",
                                         "checkpoints", "epoch=*val_mel=*.ckpt")):
        m = re.search(r"epoch=(\d+)-val_mel=(\d+\.\d+)\.ckpt$", os.path.basename(kelias))
        if m:
            k.append((float(m.group(2)), int(m.group(1)), kelias))
    if not k:
        raise SystemExit("Pjūvių nerasta.")
    return sorted(k)[0]


def eksportuok(ckpt, onnx):
    aplinka = dict(os.environ, PYTHONPATH=SRC, PYTHONIOENCODING="utf-8")
    r = subprocess.run([PY, "-m", "piper.train.export_onnx",
                        "--checkpoint", ckpt, "--output-file", onnx],
                       env=aplinka, capture_output=True, text=True, cwd=BAZE, timeout=900)
    if r.returncode != 0 or not os.path.exists(onnx):
        raise SystemExit(f"Eksportas nepavyko:\n{r.stderr[-800:]}")


def sha256(kelias):
    h = hashlib.sha256()
    with open(kelias, "rb") as f:
        for gab in iter(lambda: f.read(1 << 20), b""):
            h.update(gab)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--onnx", help="konkretus .onnx; be jo — geriausias pjūvis pagal val_mel")
    p.add_argument("--length-scale", type=float, default=1.30,
                   help="numatytasis tempas .onnx.json (09-04 sprendimas: 1.30 VISUR)")
    p.add_argument("--noise-scale", type=float, default=0.667)
    p.add_argument("--noise-w", type=float, default=0.8)
    args = p.parse_args()

    os.makedirs(os.path.join(HF, "samples"), exist_ok=True)

    # 1. Modelis
    e = None
    if args.onnx:
        onnx, kilme = os.path.abspath(args.onnx), "nurodytas ranka"
        m = re.search(r"e(\d+)", os.path.basename(onnx))
        e = int(m.group(1)) if m else None
    else:
        val, e, ck = geriausias_ckpt()
        onnx = os.path.join(BAZE, "_darbal", f"regina_e{e}.onnx")
        kilme = f"geriausias pjūvis e{e}, val_mel {val:.4f}"
        if not os.path.exists(onnx):
            print(f"Eksportuoju {os.path.basename(ck)} …")
            eksportuok(ck, onnx)
    tikslas = os.path.join(HF, VARDAS + ".onnx")
    shutil.copyfile(onnx, tikslas)
    print(f"1) {VARDAS}.onnx  <- {os.path.basename(onnx)}  ({kilme}; {os.path.getsize(tikslas)/1e6:.1f} MB)")

    # 2. Config: training fields plus the ones the catalogue expects
    k = json.load(io.open(KONFIG, encoding="utf-8"))
    cfg = {
        "audio": {"sample_rate": k["audio"]["sample_rate"], "quality": "medium"},
        "espeak": {"voice": "lt"},           # informacinis: sintezėje espeak NENAUDOJAMAS
        "inference": {"noise_scale": args.noise_scale,
                      "length_scale": args.length_scale,
                      "noise_w": args.noise_w},
        "phoneme_type": "text",
        "phoneme_map": {},
        "phoneme_id_map": k["phoneme_id_map"],
        "num_symbols": k["num_symbols"],
        "num_speakers": k["num_speakers"],
        "speaker_id_map": {},
        "piper_version": k.get("piper_version", "1.5.0"),
        "language": LANGUAGE,
        # Caught by Piper's own catalogue checker: in Piper's convention
        # `dataset` is NOT the corpus name but the VOICE name, and it has to
        # match both the catalogue folder and the middle part of the filename
        # (`<lang_code>-<dataset>-<quality>.onnx`). Putting the corpus name
        # here would fail their assertion. The Latvian voice confirms the
        # convention: lv_LV-aivars-medium has dataset "aivars".
        # The corpus is credited where it belongs - MODEL_CARD and README.
        "dataset": VARDAS.split("-")[1],
    }
    js = os.path.join(HF, VARDAS + ".onnx.json")
    with io.open(js, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"2) {VARDAS}.onnx.json  ({len(cfg['phoneme_id_map'])} simboliai, "
          f"length_scale {args.length_scale})")

    # 3. SHA256SUMS for everything in hf/ except the list itself.
    # Found while rehearsing the submission: a backup copy of the config had
    # ended up in the directory and would have gone to Hugging Face with the
    # rest. The directory must hold ONLY what ships, so a leftover file stops
    # the build instead of being skipped quietly - a file that is silently
    # ignored is a file that will still be there next time.
    liekanos = [fn for _, _, ff in os.walk(HF) for fn in ff
                if ".pries_" in fn or fn.endswith((".bak", ".tmp", ".orig"))]
    if liekanos:
        raise SystemExit("⛔ hf/ guli darbinės liekanos — išnešk jas prieš "
                         "sudarant paketą:\n   " + "\n   ".join(liekanos))
    # If a checkpoint is already here, it must come from the SAME run as the
    # model - otherwise someone would grow a voice from something nobody has
    # listened to.
    if e is not None:
        for _, _, ff in os.walk(HF):
            for fn in ff:
                if fn.endswith(".ckpt") and f"-e{e}." not in fn:
                    raise SystemExit(f"⛔ hf/{fn} yra iš kito pjūvio nei modelis "
                                     f"(e{e}). Perdaryk: svarus_checkpoint.py")
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
    print("3) SHA256SUMS:")
    for e in eilutes:
        print("   ", e[:16] + "…", e.split("  ", 1)[1])
    print(f"\nPaketas: {HF}")


if __name__ == "__main__":
    main()
