# -*- coding: utf-8 -*-
"""Puts the hf/ package on Hugging Face as RobertasTa/lt_LT-reginute1-medium.

    python hf_ikelk_repo.py             # dry run: lists what would go up, checks the login
    python hf_ikelk_repo.py --run       # creates the repo PRIVATE (if missing) and uploads hf/
    python hf_ikelk_repo.py --public    # flips the repo to public (after Robertas' word)

Run from the training venv (.venv). hf/ must contain ONLY what ships - it is
uploaded whole (README.md becomes the model card).
"""
import argparse
import io
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
CIA = os.path.dirname(os.path.abspath(__file__))
HF = os.path.join(CIA, "hf")
VARDAS = "lt_LT-reginute1-medium"
REPO = "RobertasTa/" + VARDAS
BUTINI = (VARDAS + ".onnx", VARDAS + ".onnx.json", "MODEL_CARD", "README.md", "SHA256SUMS",
          "phonemize_lithuanian.py", "lt_kirciai.tsv", "skaiciu_pletiklis.py",
          "zodziai_trumpi.txt", "synth_reginute.py",
          os.path.join("samples", "speaker_0.mp3"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--public", action="store_true")
    a = ap.parse_args()

    truksta = [f for f in BUTINI if not os.path.exists(os.path.join(HF, f))]
    if truksta:
        raise SystemExit("⛔ hf/ trūksta: " + ", ".join(truksta) + "  (sudaryk_paketa.py, sample_speaker0.py)")
    sums = io.open(os.path.join(HF, "SHA256SUMS"), encoding="utf-8").read()
    for f in BUTINI:
        if f != "SHA256SUMS" and f.replace("\\", "/") not in sums:
            raise SystemExit(f"⛔ SHA256SUMS pasenęs - nėra {f}. Perleisk sample_speaker0.py arba sudaryk_paketa.py")
    print("Keliauja:")
    for saknis, _, failai in os.walk(HF):
        for fn in sorted(failai):
            p = os.path.join(saknis, fn)
            print(f"   {os.path.relpath(p, HF):45} {os.path.getsize(p):>12,} B")

    from huggingface_hub import HfApi
    api = HfApi()
    kas = api.whoami()["name"]
    assert kas == "RobertasTa", f"prisijungęs {kas}"
    try:
        info = api.model_info(REPO)
        print(f"\nRepo {REPO} YRA, private={info.private}, failų {len(info.siblings or [])}")
        yra = True
    except Exception:
        print(f"\nRepo {REPO} dar nėra.")
        yra = False

    if a.public:
        assert yra, "nėra ko viešinti"
        api.update_repo_settings(REPO, private=False)
        print("✅ Repo VIEŠAS:", "https://huggingface.co/" + REPO)
        return
    if not a.run:
        print("\nDRY RUN - niekas neįkelta.")
        return
    if not yra:
        api.create_repo(REPO, repo_type="model", private=True, exist_ok=True)
        print("Sukurtas PRIVATUS repo.")
    r = api.upload_folder(repo_id=REPO, repo_type="model", folder_path=HF,
                          commit_message=f"{VARDAS}: model, config, phonemizer, dictionary, card, sample")
    print("✅ Įkelta:", r)
    print("Viešinti: python hf_ikelk_repo.py --public")


if __name__ == "__main__":
    main()
