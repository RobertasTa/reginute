# Parity check: does phonemize_lithuanian reproduce the phonemes the model
# was TRAINED on, accents included? In other words, will the model receive
# through Piper the same input it saw while learning?
#
# Differences are disagreements between the runtime dictionary (one entry per
# spelling) and the corpus annotation (per sentence, in context): homographs,
# and words the annotation resolved one way and the dictionary another.
#
# Run it with the piper-tts wheel:  python patikrink_pries_mokyma.py [N]
import csv
import io
import os
import re
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from phonemize_lithuanian import LithuanianPhonemizer

BAZE = r"D:\_Balsas Lietuviksas"
TEKSTAI = BAZE + r"\_duomenys\regina\metadata_skyryba.csv"
FONEMOS = BAZE + r"\_duomenys\regina\metadata_phonemes_kirciai.csv"
N = int(sys.argv[1]) if len(sys.argv) > 1 else 800


def main():
    ph = LithuanianPhonemizer()
    tekstai = {}
    for r in csv.reader(io.open(TEKSTAI, encoding="utf-8-sig")):
        if len(r) >= 3 and r[0] != "id":
            tekstai[r[0]] = r[2]
    musu = {}
    for r in csv.reader(io.open(FONEMOS, encoding="utf-8"), delimiter="|"):
        if len(r) >= 2:
            musu[r[0].replace(".wav", "")] = r[-1]
    bendri = [k for k in musu if k in tekstai][:N]

    sak = zod = zod_ok = 0
    skirt = Counter()
    pvz = []
    for k in bendri:
        gauta = "".join("".join(s) for s in ph.phonemize(tekstai[k]))
        laukta = musu[k]
        if gauta == laukta:
            sak += 1
        a, b = gauta.split(), laukta.split()
        for x, y in zip(a, b):
            zod += 1
            if x == y:
                zod_ok += 1
            else:
                skirt[(x, y)] += 1
                if len(pvz) < 15:
                    pvz.append((tekstai[k][:50], x, y))
        if len(a) != len(b):
            skirt[("ILGIS", f"{len(a)}!={len(b)}")] += 1

    print(f"Sakinių: {len(bendri)}; identiški SU KIRČIAIS: {sak} ({100*sak/max(1,len(bendri)):.1f} %)")
    print(f"Žodžių: {zod}; identiški: {zod_ok} ({100*zod_ok/max(1,zod):.2f} %)")
    print("\nDažniausi skirtumai (modulis -> mokymas):")
    for (x, y), n in skirt.most_common(20):
        print(f"  {n:4d}  {x}  ->  {y}")
    print("\nPavyzdžiai:")
    for t, x, y in pvz:
        print(f"  [{t}]  modulis={x}  mokymas={y}")


if __name__ == "__main__":
    main()
