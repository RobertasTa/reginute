# PAKETO STATYTOJAS: iš geriausio mokymo pjūvio sudeda `hf/` katalogą — tiksliai
# tą failų rinkinį, kuris keliauja ir į serverį, ir į Hugging Face.
#
# Kodėl atskiras įrankis (09-04, Robertas: „pradėk konstruoti, bo pamirši"):
#   1. geriausias pjūvis renkamas pagal val_mel iš VISŲ lightning_logs/version_*,
#      ne pagal naujausią .onnx (09-03 pamoka: kadre nuėjo e6074 vietoj e5894);
#   2. `.onnx.json` gaminamas iš mokymo konfigūracijos + oficialaus katalogo
#      laukų (nusižiūrėta nuo ru_RU-irina-medium.onnx.json: audio.quality,
#      language{code,family,region,name_native,name_english,country_english},
#      dataset, inference) — kad Hansenui nereikėtų nieko taisyti ranka;
#   3. SHA256SUMS — kad paketas, serveris ir HF būtų baitas į baitą tas pats.
#
# Leisti su MOKYMO venv (jame yra piper.train eksportui):
#   .venv\Scripts\python.exe _irankiai\piper_lt\sudaryk_paketa.py
#   .venv\Scripts\python.exe _irankiai\piper_lt\sudaryk_paketa.py --onnx _darbal\regina_e6885.onnx
#   .venv\Scripts\python.exe _irankiai\piper_lt\sudaryk_paketa.py --length-scale 1.30
#
# ⚠️ 09-05: numatytasis tempas buvo 1.25, nors 09-04 sutarta 1.30 VISUR
# (Robertas vertino vieną greitį, o svetimas būtų gavęs kitą). Paleidus šį
# skriptą be argumento paketas būtų TYLIAI grįžęs prie 1.25 — ištaisyta.
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
    if args.onnx:
        onnx, kilme = os.path.abspath(args.onnx), "nurodytas ranka"
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

    # 2. Konfigūracija — mokymo + katalogo laukai
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
        # ⚠️ 09-04, sugavo PATS Piperio patikrintuvas (`_script/voicefest.py`):
        # `dataset` Piperio konvencijoje reiškia NE garsyną, o BALSO VARDĄ, ir
        # jis privalo sutapti (a) su katalogo aplanku ir (b) su vidurine failo
        # vardo dalimi: `<lang_code>-<dataset>-<quality>.onnx`.
        # Buvau įrašęs „liepa-tts" (garsyno vardą) — testas
        # `assertEqual(file_dataset, config["dataset"])` būtų kritęs.
        # Kaimynas latvis patvirtina: `lv_LV-aivars-medium` → dataset „aivars".
        # Garsynas įvardytas ten, kur jam vieta — MODEL_CARD ir README.
        "dataset": VARDAS.split("-")[1],
    }
    js = os.path.join(HF, VARDAS + ".onnx.json")
    with io.open(js, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"2) {VARDAS}.onnx.json  ({len(cfg['phoneme_id_map'])} simboliai, "
          f"length_scale {args.length_scale})")

    # 3. SHA256SUMS — viskam, kas hf/ kataloge, išskyrus patį sąrašą
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
