# KIRČIŲ ŽODYNO SUDARYMAS Piperio fonemizatoriui (09-03, Roberto „rašyk").
# Sujungia į VIENĄ failą lt_kirciai.tsv (žodis <TAB> balsių grupės nr <TAB>
# priegaidės ženklas) tris šaltinius ta pačia pirmumo tvarka, kaip sintezėje:
#   1. RANKINIAI (fonemizuok_teisingai.py) — Roberto ausies pataisymai
#   2. liepa-tts anotacija (liepa_kirciu_zodynas.json, 12 604 ž., CC-BY-4.0)
#   3. svogunas/g2p-lt-lexicon (233 390 ž., CC-BY-4.0) — per tą patį
#      skaitytuvą kircio_grupe_is_zodyno(), kad kodavimo taisyklės
#      (Aa→ˈ, aA→ˌ, „A J"→ˌ, gretimi balsiai = viena grupė) būtų vienoje vietoje.
# Runtime modulis (phonemize_lithuanian.py) tada tik IEŠKO — jokios g2p logikos.
# Leisti su mokymo venv:  .venv\Scripts\python.exe _irankiai\piper_lt\sudaryk_zodyna.py
import io
import os
import sys
from collections import Counter

sys.path.insert(0, r"D:\_Balsas Lietuviksas\_irankiai")
sys.stdout.reconfigure(encoding="utf-8")
from fonemizuok_teisingai import RANKINIAI, liepa_zodynas, zodynas, kircio_grupe_is_zodyno

ISVESTIS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lt_kirciai.tsv")


def main():
    irasai = {}
    saltinis = Counter()
    for z, (nr, zenklas) in RANKINIAI.items():
        irasai[z] = (nr, zenklas)
        saltinis["rankiniai"] += 1
    for z, (nr, zenklas) in liepa_zodynas().items():
        if z not in irasai:
            irasai[z] = (nr, zenklas)
            saltinis["liepa"] += 1
    be_kircio = 0
    for z in zodynas():
        if z in irasai:
            continue
        nr, zenklas = kircio_grupe_is_zodyno(z)
        if nr is None:
            be_kircio += 1
            continue
        irasai[z] = (nr, zenklas)
        saltinis["g2p"] += 1

    with io.open(ISVESTIS, "w", encoding="utf-8", newline="\n") as f:
        for z in sorted(irasai):
            nr, zenklas = irasai[z]
            f.write(f"{z}\t{nr}\t{zenklas}\n")

    print(f"Įrašyta: {len(irasai)} žodžių -> {ISVESTIS}")
    for k, v in saltinis.items():
        print(f"  {k:<10} {v}")
    print(f"  g2p be kirčio ženklo (praleista): {be_kircio}")
    print(f"  dydis: {os.path.getsize(ISVESTIS)/1e6:.2f} MB")
    zenklai = Counter(v[1] for v in irasai.values())
    print("  priegaidės:", dict(zenklai))


if __name__ == "__main__":
    main()
