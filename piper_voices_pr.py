# -*- coding: utf-8 -*-
"""Opens the rhasspy/piper-voices pull request for lt_LT-reginute1-medium as ONE
commit with everything Michael Hansen otherwise does by hand after a merge
(measured on PRs #19, #60, #71, #89, #93, #95 - see PIPER_PR_RECEPTAS.md):

    lt/lt_LT/reginute1/medium/lt_LT-reginute1-medium.onnx
    lt/lt_LT/reginute1/medium/lt_LT-reginute1-medium.onnx.json
    lt/lt_LT/reginute1/medium/MODEL_CARD
    lt/lt_LT/reginute1/medium/samples/speaker_0.mp3
    _script/voicefest.py      (main + the "lt_LT" language line)
    voices.json               (main + the lt_LT-reginute1-medium entry, md5/sizes from hf/)

Both catalogue files are fetched from `main` at run time, so the PR is based on
whatever the catalogue holds that minute.

    python piper_voices_pr.py            # dry run: builds everything in _pr_work/, opens nothing
    python piper_voices_pr.py --run      # creates the PR, prints its URL

Run from the training venv (.venv) - it holds huggingface_hub and the login.
The PR title is the first line of PR_TEKSTAS_piper_voices.md, the body the rest.
"""
import argparse
import hashlib
import io
import json
import os
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
CIA = os.path.dirname(os.path.abspath(__file__))
HF = os.path.join(CIA, "hf")
WORK = os.path.join(CIA, "_pr_work")
VARDAS = "lt_LT-reginute1-medium"
KELIAS = "lt/lt_LT/reginute1/medium"
REPO = "rhasspy/piper-voices"
MUSU_HF = "RobertasTa/" + VARDAS
RAW = f"https://huggingface.co/{REPO}/resolve/main/"
KALBA_EIL = '    "lt_LT": Language("Lietuvių", "Lithuanian", "Lithuania"),\n'
TEKSTAS = os.path.join(CIA, "PR_TEKSTAS_piper_voices.md")


def parsisiusk(failas):
    req = urllib.request.Request(RAW + failas, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read().decode("utf-8")


def md5(kelias):
    h = hashlib.md5()
    with open(kelias, "rb") as f:
        for gab in iter(lambda: f.read(1 << 20), b""):
            h.update(gab)
    return h.hexdigest()


def voicefest_su_lt(tekstas):
    if '"lt_LT"' in tekstas:
        print("  voicefest.py: lt_LT JAU YRA upstream - failo nekeičiam")
        return None
    inkaras = '    "lv_LV": Language('
    assert inkaras in tekstas, "voicefest.py: nerastas lv_LV inkaras - forma pasikeitė, žiūrėk ranka"
    return tekstas.replace(inkaras, KALBA_EIL + inkaras, 1)


def voices_json_su_lt(tekstas, irasas):
    key = VARDAS
    duom = json.loads(tekstas)
    assert key not in duom, f"voices.json: {key} JAU YRA - kažkas įtraukė anksčiau?"
    # Insert as text, not by re-dumping the whole file: his formatting (indent=4,
    # ensure_ascii=False) must stay byte-identical elsewhere in the diff.
    raktai = re.findall(r'^    "([^"]+)": \{$', tekstas, flags=re.M)
    po = next((k for k in raktai if k > key), None)
    assert po, "voices.json: nerasta, prieš kurį raktą įterpti"
    blokas = json.dumps({key: irasas}, indent=4, ensure_ascii=False)
    vidus = "\n".join(blokas.splitlines()[1:-1])          # be išorinių { }
    inkaras = f'    "{po}": {{\n'
    assert tekstas.count(inkaras) == 1
    naujas = tekstas.replace(inkaras, vidus + ",\n" + inkaras, 1)
    patikra = json.loads(naujas)
    assert patikra[key] == irasas and len(patikra) == len(duom) + 1
    print(f"  voices.json: įrašas įterptas prieš {po}")
    return naujas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true", help="iš tikrųjų sukurti PR")
    a = ap.parse_args()
    os.makedirs(WORK, exist_ok=True)

    # 0. Package sanity - the PR must carry the bytes that are in hf/ and on HF.
    failai = {
        f"{KELIAS}/{VARDAS}.onnx": os.path.join(HF, VARDAS + ".onnx"),
        f"{KELIAS}/{VARDAS}.onnx.json": os.path.join(HF, VARDAS + ".onnx.json"),
        f"{KELIAS}/MODEL_CARD": os.path.join(HF, "MODEL_CARD"),
        f"{KELIAS}/samples/speaker_0.mp3": os.path.join(HF, "samples", "speaker_0.mp3"),
    }
    for k, v in failai.items():
        assert os.path.exists(v), f"trūksta {v}"
    cfg = json.load(io.open(failai[f"{KELIAS}/{VARDAS}.onnx.json"], encoding="utf-8"))
    assert cfg["dataset"] == "reginute1" and cfg["audio"]["quality"] == "medium" \
        and cfg["language"]["code"] == "lt_LT", "onnx.json laukai neatitinka katalogo"
    # The catalogue config says "lithuanian", not "text" (Robertas 09-05 night).
    # With "text" a stock Piper feeds the model raw letters and the voice is
    # noise even after the piper1-gpl PR lands; with "lithuanian" an old Piper
    # fails to load it with a clear error. Our own HF repo keeps "text" + the
    # module (that path phonemizes outside Piper).
    assert cfg["phoneme_type"] == "text"
    cfg["phoneme_type"] = "lithuanian"
    p = os.path.join(WORK, VARDAS + ".onnx.json")
    with io.open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
        f.write("\n")
    failai[f"{KELIAS}/{VARDAS}.onnx.json"] = p
    # NO dictionary in the catalogue folder. Measured 09-05 night: 176 voices,
    # not one ships an extra file; non-espeak voices get their data from the
    # piper package (Hebrew), a pip dependency (Japanese) or an auto-download
    # from piper-checkpoints/_resources (g2pW). Where lt_kirciai.tsv lives is
    # Ihor's/Michael's call (LAISKAS_4); until then it sits in the voice repo.
    with io.open(TEKSTAS, encoding="utf-8") as f:
        eilutes = f.read().split("\n", 1)
    pavadinimas, aprasas = eilutes[0].strip(), eilutes[1].strip()
    assert "RobertasTa/" + VARDAS in aprasas, "PR tekste nėra nuorodos į mūsų HF repo"

    # 1. Catalogue files from main, right now
    print("Parsisiunčiu voicefest.py ir voices.json iš main …")
    vf = voicefest_su_lt(parsisiusk("_script/voicefest.py"))
    irasas = {
        "key": VARDAS,
        "name": "reginute1",
        "language": cfg["language"],
        "quality": "medium",
        "num_speakers": cfg["num_speakers"],
        "speaker_id_map": cfg.get("speaker_id_map", {}),
        "files": {
            k: {"size_bytes": os.path.getsize(v), "md5_digest": md5(v)}
            for k, v in failai.items()
            if k.endswith((".onnx", ".onnx.json", "MODEL_CARD"))   # voicefest.py konvencija: tik šie trys
        },
        "aliases": [],
    }
    vj = voices_json_su_lt(parsisiusk("voices.json"), irasas)

    # 2. Operations
    from huggingface_hub import CommitOperationAdd, HfApi
    ops = [CommitOperationAdd(path_in_repo=k, path_or_fileobj=v) for k, v in failai.items()]
    if vf is not None:
        p = os.path.join(WORK, "voicefest.py")
        io.open(p, "w", encoding="utf-8", newline="\n").write(vf)
        ops.append(CommitOperationAdd("_script/voicefest.py", p))
    p = os.path.join(WORK, "voices.json")
    io.open(p, "w", encoding="utf-8", newline="\n").write(vj)
    ops.append(CommitOperationAdd("voices.json", p))

    print("\nPR:", pavadinimas)
    for o in ops:
        print(f"   {o.path_in_repo:55} {os.path.getsize(o.path_or_fileobj):>12,} B")
    print("   voices.json įrašas:", json.dumps(irasas["files"], indent=2))

    if not a.run:
        print("\nDRY RUN - PR nesukurtas. Paruošti failai:", WORK)
        return

    # 3. Guards before anything public
    api = HfApi()
    kas = api.whoami()["name"]
    assert kas == "RobertasTa", f"prisijungęs {kas}, ne RobertasTa"
    api.model_info(MUSU_HF)          # PR text links to it - must exist (RepositoryNotFoundError otherwise)
    print(f"\nPrisijungęs {kas}; {MUSU_HF} egzistuoja. Kuriu PR …")
    r = api.create_commit(repo_id=REPO, repo_type="model", operations=ops,
                          commit_message=pavadinimas, commit_description=aprasas,
                          create_pr=True)
    print("PR:", r.pr_url)
    io.open(os.path.join(WORK, "PR_URL.txt"), "w", encoding="utf-8").write(str(r.pr_url) + "\n")


if __name__ == "__main__":
    main()
