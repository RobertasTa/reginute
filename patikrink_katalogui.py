# -*- coding: utf-8 -*-
"""Paleidžia PIPERIO PATĮ patikrintuvą (`_script/voicefest.py`) ant mūsų paketo.

Kodėl atskiras įrankis (09-04): pirmą kartą paleidęs jį RADAU TIKRĄ KLAIDĄ —
`config["dataset"]` buvo „liepa-tts", o Piperio konvencijoje tas laukas reiškia
NE garsyną, o BALSO VARDĄ, ir privalo sutapti su aplanku bei vidurine failo
vardo dalimi (`<lang_code>-<dataset>-<quality>.onnx`). Testas
`assertEqual(file_dataset, config["dataset"])` būtų kritęs pateikimo metu.
⇒ nuo šiol tai darom PATYS, prieš pateikdami.

⚠️ Skripto NEVEŽAM su savimi (jis yra `rhasspy/piper-voices`, MIT) — kaskart
parsisiunčiam šviežią, kad tikrintume tuo, ką Piperis naudoja ŠIANDIEN.

⚠️ VIENINTELIS dalykas, kurio patys pataisyti negalim: `voicefest.py` turi savo
kalbų sąrašą (56 kalbos), ir **`lt_LT` jo NĖRA** (estų ir latvių yra).
Testui jį įdedam LOKALIAI; tikram pateikimui šią eilutę turės pridėti Michael
Hansen — ji paruošta žemiau ir įrašyta į README, kad jam liktų vienas
įklijavimas.

  .venv\\Scripts\\python.exe _irankiai\\piper_lt\\patikrink_katalogui.py
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

        # 2. Šviežias voicefest.py
        print("Siunčiu voicefest.py …", flush=True)
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

        # 3. Paleidžiam jų testą
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
