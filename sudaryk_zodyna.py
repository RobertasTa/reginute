# Builds the stress dictionary used by the phonemizer.
#
# It merges three sources into one file (word <TAB> vowel group index <TAB>
# pitch accent mark), in the same order of precedence the synthesis uses:
#   1. manual corrections - words fixed after listening
#   2. the liepa-tts corpus annotation (12 604 words, CC-BY-4.0)
#   3. svogunas/g2p-lt-lexicon (233 390 words, CC-BY-4.0), read through the
#      same decoder, so that the encoding rules (which capital marks which
#      accent, adjacent vowels counting as one group) live in one place only.
#
# The runtime module then only LOOKS THINGS UP - it contains no g2p logic.
# Run it with the training environment.
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
