# Reginutė — Lithuanian voice for Piper TTS (`lt_LT-reginute1-medium`)

> **Status: private, under test.** Nothing here is final until the voice has
> passed a blind listening test and the full chain has been verified on a real
> Home Assistant installation. Steps marked ⏳ have not been verified yet —
> this README is written *while* doing, not after.

Reginutė is a Lithuanian voice for [Piper](https://github.com/OHF-Voice/piper1-gpl),
trained on the **LIEPA** speech corpus of Vilnius University (speaker Regina
Jokubauskaitė, studio recordings, ~3 h, CC-BY-4.0). There has never been an
`lt_LT` voice in the Piper catalogue — Latvian and Estonian are there,
Lithuanian is not.

Lithuanian has three phonemic pitch accents, and espeak-ng places Lithuanian
stress on the wrong syllable in roughly half of the words when checked against
the corpus' gold annotation. So this voice does **not** use espeak-ng at
synthesis time: it uses `phoneme_type: text` together with an accent-aware
phonemizer (`phonemize_lithuanian.py`) and a 189k-word stress dictionary
(`lt_kirciai.tsv`, built from the LIEPA annotations and Arūnas Smaliukas'
`g2p-lt-lexicon`, both CC-BY-4.0).

**This means the voice needs the phonemizer to speak.** Plain Piper with a
`text` voice feeds the model raw letters, not IPA — it will not produce
Lithuanian. Until `phonemize_lithuanian` is merged into piper1-gpl, the module
in this repository has to sit in front of the model. Both install paths below
include it.

## What's in here

| Path | What it is |
|---|---|
| `phonemize_lithuanian.py` | The phonemizer: espeak-ng IPA per word → dictionary stress → three accent marks (`ˈ ˌ ˋ`). Written in the shape of Piper's `phonemize_japanese.py`, intended as a PR to piper1-gpl. |
| `lt_kirciai.tsv` | Stress dictionary, 189 247 word forms, 3 MB. Column 2 = index of the stressed vowel group, column 3 = accent mark. |
| `zodziai_trumpi.txt` | Short word list used by the number/abbreviation expander. |
| `synth_reginute.py` | Synthesis recipe: splits at sentence punctuation, levels speaking rate per fragment, trims silence, `normalize_audio=False`. |
| `wyoming_reginute.py` | Wyoming TTS server around the voice — what Home Assistant talks to. |
| `demo_piper_wheel.py` | Proof that the released `piper-tts` wheel + this module + the `.onnx` is enough — no fork. |
| `test_phonemize_lithuanian.py` | pytest suite for the phonemizer. |
| `hf/` | The exact package that goes to Hugging Face: `.onnx` (not in git), `.onnx.json`, `MODEL_CARD`, `samples/`, `SHA256SUMS`. |
| `docs/` | Installation and testing notes, written during the server tests. `DU_ASISTENTAI_HA.md` — how one Voice PE speaker runs two languages with two wake words (verified live; LT, EN to follow). |
| `sudaryk_zodyna.py`, `patikrink_pries_mokyma.py` | Build-side tools (dictionary builder, training-parity check). Contain Windows paths; not needed by users. |

## Install path A — plain Piper (no Home Assistant) ⏳

```bash
pip install piper-tts            # 1.7.x
# copy phonemize_lithuanian.py, lt_kirciai.tsv and the two hf/ voice files next to your script
```

```python
from piper import PiperVoice, SynthesisConfig
from phonemize_lithuanian import LithuanianPhonemizer

voice = PiperVoice.load("lt_LT-reginute1-medium.onnx")
ph = LithuanianPhonemizer()
# … see demo_piper_wheel.py for the full call; normalize_audio must be False
```

⏳ To be verified on the server with the released wheel; exact snippet will be
pasted from the working test.

## Install path B — Home Assistant via Wyoming ⏳

Runs beside your existing Piper add-on, on its own port; nothing existing is
touched. Full recipe in `docs/DIEGIMAS_SERVERYJE.md` (Lithuanian, being written
during the live install; English version follows once it has worked once).

## Licence

* **Code** in this repository: GPL-3.0 (same as piper1-gpl, see `LICENSE`).
* **Voice files** (`hf/`): CC-BY-4.0, derived from the LIEPA corpus
  (CC-BY-4.0). Lineage stated honestly in `hf/MODEL_CARD`: fine-tuned from the
  Piper catalogue checkpoint `ru_RU-irina-medium`, which was itself fine-tuned
  from `en_US-lessac`.

## Attribution

* LIEPA corpus — Vilnius University (project lead Gražina Korvel; corpus
  maintainer Gediminas Navickas); dataset published as
  `meldynamics/liepa-tts` on Hugging Face.
* Stress dictionary derived from `svogunas/g2p-lt-lexicon` by **Arūnas
  Smaliukas** (CC BY 4.0).
* Piper — Michael Hansen and the Open Home Foundation.

---

## Lietuviškai, trumpai

Reginutė — lietuviškas balsas Piper sintezatoriui ir Home Assistant, išmokytas
iš Vilniaus universiteto LIEPA garsyno. Kadangi espeak-ng lietuvių kirčius
deda ne ten maždaug pusėje žodžių, balsas kalba per savo fonemizatorių su
kirčių žodynu — be jo gryname Piperyje jis netaria nieko. Diegimo instrukcija
rašoma **darant**, ant tikro serverio: `docs/DIEGIMAS_SERVERYJE.md`.
