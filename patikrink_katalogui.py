# -*- coding: utf-8 -*-
"""Runs PIPER'S OWN catalogue checker (`_script/voicefest.py`) on our package.

Worth having as a tool: the very first run found a real error. `dataset` was
set to the corpus name, but in Piper's convention that field is the VOICE
name and must match both the folder and the middle part of the filename
(`<lang_code>-<dataset>-<quality>.onnx`). Their assertion would have failed
during submission - better to find that here.

The checker is not vendored (it lives in `rhasspy/piper-voices`, MIT); a
fresh copy is fetched each time, so we test against what Piper uses today.

One thing cannot be fixed on our side: `voicefest.py` carries its own list of
56 languages, and `lt_LT` is not in it (Estonian and Latvian are). It is added
LOCALLY for the test; for the real submission that one line has to be added
upstream, and it is prepared below and quoted in the README so that it is a
single paste.

  python patikrink_katalogui.py
"""
from __future__ import annotations

import io
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
CIA = os.path.dirname(os.path.abspath(__file__))
HF = os.path.join(CIA, "hf")
VARDAS = "lt_LT-reginute1-medium"
KALBA_EIL = ('    "lt_LT": Language("Lietuvių", "Lithuanian", "Lithuania"),\n')
URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main/_script/voicefest.py"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="voicefest_") as tmp:
        # 1. Netikras katalogo medis: lt/lt_LT/reginute1/medium/
        balsas = os.path.join(tmp, "lt", "lt_LT", "reginute1", "medium")
        os.makedirs(os.path.join(balsas, "samples"), exist_ok=True)
        os.makedirs(os.path.join(tmp, "_script"), exist_ok=True)
        for f in (VARDAS + ".onnx", VARDAS + ".onnx.json", "MODEL_CARD"):
            shutil.copyfile(os.path.join(HF, f), os.path.join(balsas, f))
        pav = os.path.join(HF, "samples", "speaker_0.mp3")
        if os.path.exists(pav):
            shutil.copyfile(pav, os.path.join(balsas, "samples", "speaker_0.mp3"))

        # 2. A fresh voicefest.py
        print("Downloading voicefest.py ...", flush=True)
        try:
            with urllib.request.urlopen(URL, timeout=60) as r:
                skriptas = r.read().decode("utf-8")
        except Exception as e:                       # noqa: BLE001
            print(f"NEPAVYKO parsisiųsti ({e}). HF kartais riboja (HTTP 429) — "
                  f"pabandyk po kelių minučių.")
            return 2
        if '"lt_LT"' not in skriptas:
            skriptas = skriptas.replace('    "lv_LV": Language(',
                                        KALBA_EIL + '    "lv_LV": Language(')
            print("  ⚠️ lt_LT jų sąraše NĖRA — įdėtas tik šiam testui.")
        kelias = os.path.join(tmp, "_script", "voicefest.py")
        io.open(kelias, "w", encoding="utf-8").write(skriptas)

        # 3. Run their test
        r = subprocess.run([sys.executable, "voicefest.py"],
                           cwd=os.path.dirname(kelias),
                           capture_output=True, text=True, timeout=600)
        isvestis = (r.stdout or "") + (r.stderr or "")
        print(isvestis.strip()[-1500:])
        gerai = "OK" in isvestis and "FAILED" not in isvestis
        print("\n" + ("✅ PIPERIO PATIKRA PRAĖJO" if gerai else "❌ PIPERIO PATIKRA KRITO"))
        return 0 if gerai else 1


if __name__ == "__main__":
    raise SystemExit(main())
