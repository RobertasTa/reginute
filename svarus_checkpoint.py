# ŠVARUS CHECKPOINT PAKETUI — kad kiti galėtų auginti savo balsą iš Reginutės.
#
# Kilmė: PIPER_PATEIKIMO_PLANAS 9.1 (Roberto radinys HF #62): Hansenas prie
# balso laiko ir PyTorch pjūvį (`piper-checkpoints`), o bacca87 skelbė atskirą
# `-checkpoint` repo. Be jo mūsų balsą galima tik NAUDOTI, o su juo — tęsti:
# kito diktoriaus balsą treniruoti nuo Reginutės, o ne nuo rusiškos Irinos.
#
# Ką nuima ir kodėl:
#   optimizer_states  537 MB — Adam momentai; reikalingi TIK tam pačiam
#                     mokymui tęsti tuo pačiu kompiuteriu, kitam žmogui bevertis
#   loops/callbacks/lr_schedulers — Lightning vidinė būsena (epochų skaitliukai)
# Ką PALIEKA:
#   state_dict (model_g 90 MB + model_d 178 MB) — ir generatorių, IR
#     diskriminatorių: be `model_d` tolesnis mokymas prastesnis (GAN reikia
#     abiejų), o kaip tik tam šis failas ir skirtas
#   hyper_parameters — be jų Piperis nežino, kokia architektūra buvo mokyta
#
#   .venv\Scripts\python.exe _irankiai\piper_lt\svarus_checkpoint.py
#   ... --ckpt <kelias>   (be argumento — geriausias pjūvis pagal val_mel)
import argparse
import glob
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

BAZE = r"D:\_Balsas Lietuviksas"
VARDAS = "lt_LT-reginute1-medium"
NUIMAM = ("optimizer_states", "loops", "callbacks", "lr_schedulers")


def geriausias_ckpt():
    k = []
    for kelias in glob.glob(os.path.join(BAZE, "lightning_logs", "version_*",
                                         "checkpoints", "epoch=*val_mel=*.ckpt")):
        m = re.search(r"epoch=(\d+)-val_mel=(\d+\.\d+)\.ckpt$", os.path.basename(kelias))
        if m:
            k.append((float(m.group(2)), int(m.group(1)), kelias))
    return sorted(k)[0] if k else None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ckpt", help="konkretus pjūvis (be jo — geriausias pagal val_mel)")
    p.add_argument("--isvestis", default=os.path.join(BAZE, "_irankiai", "piper_lt", "hf"))
    args = p.parse_args()

    import torch

    if args.ckpt:
        kelias, aprasas = os.path.abspath(args.ckpt), "nurodytas ranka"
        e = int(re.search(r"epoch=(\d+)", os.path.basename(kelias)).group(1))
        val = float(re.search(r"val_mel=(\d+\.\d+)", os.path.basename(kelias)).group(1))
    else:
        g = geriausias_ckpt()
        if not g:
            raise SystemExit("Nerasta nė vieno pjūvio")
        val, e, kelias = g
        aprasas = "geriausias pagal val_mel"

    print(f"Imam: {os.path.basename(kelias)} ({aprasas})")
    ck = torch.load(kelias, map_location="cpu", weights_only=False)

    svarus = {k: v for k, v in ck.items() if k not in NUIMAM}
    isv = os.path.join(args.isvestis, f"{VARDAS}-e{e}.ckpt")
    os.makedirs(args.isvestis, exist_ok=True)
    torch.save(svarus, isv)

    buvo = os.path.getsize(kelias) / 1048576
    liko = os.path.getsize(isv) / 1048576
    print(f"Nuimta: {', '.join(NUIMAM)}")
    print(f"{buvo:.0f} MB -> {liko:.0f} MB   ({isv})")

    # patikra: ar tikrai atsidaro ir ar svoriai vietoje
    t = torch.load(isv, map_location="cpu", weights_only=False)
    sd = t.get("state_dict", {})
    g_yra = sum(1 for k in sd if k.startswith("model_g"))
    d_yra = sum(1 for k in sd if k.startswith("model_d"))
    print(f"Patikra: state_dict {len(sd)} tenzorių (model_g {g_yra}, model_d {d_yra}), "
          f"hyper_parameters {'YRA' if 'hyper_parameters' in t else 'NĖRA'}, "
          f"epocha {t.get('epoch')}")
    if not g_yra or "hyper_parameters" not in t:
        raise SystemExit("⛔ Patikra nepavyko — failo NENAUDOTI")
    print(f"val_mel {val:.4f} — įrašyti į MODEL_CARD kartu su epocha {e}")


if __name__ == "__main__":
    main()
