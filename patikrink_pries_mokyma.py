# PATIKRA: ar naujas Piperio modulis phonemize_lithuanian atkuria MOKYMO
# fonemas (su kirčiais!) — t. y. ar modelis per Piperį gaus tą pačią įvestį,
# kokią matė mokydamasis. Skirtumai = žodyno (runtime) ir anotacijos (auksas,
# per sakinį) neatitikimai: homografai, žodžiai, kurių anotacija turėjo, o
# žodynas išsprendė kitaip.
# Leisti su piper-tts ratu:  _darbal\pw_venv\Scripts\python.exe _irankiai\piper_lt\patikrink_pries_mokyma.py [N]
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
