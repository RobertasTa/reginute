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

## The other half of the chain — ears

A voice assistant needs two halves. This repository is the **mouth**; the
**ears** are not ours, and we want to say so loudly.

**[`kristijonas/paprika-whisper-lt-v3`](https://huggingface.co/kristijonas/paprika-whisper-lt-v3)**
by **Kristijonas Jakubsonas** — a Lithuanian fine-tune of `whisper-large-v3-turbo`,
trained on ~3 281 h of the LIEPA-3 corpus, CC-BY-4.0. Pipelines and tooling:
**[github.com/kristijonasatpro/paprika](https://github.com/kristijonasatpro/paprika)**
(Apache-2.0).

Why it matters here, measured on our own bench rather than taken on trust:

| Lithuanian speech → text | WER |
|---|---|
| generic `whisper-large-v3-turbo` | 25.95 % |
| **Paprika v3** | **7.63 %** |

On the author's own recording of one of us — a non-professional speaker, in a
normal room — the generic model lost whole sentences, while Paprika made about
two ending errors in a hundred words.

⚠️ **One thing the author warns about, and he is right:** use long-form
decoding, not `chunk_length_s`. We reproduced the failure ourselves before we
understood the warning.

In our house the two halves run side by side as Wyoming services: Paprika as
speech-to-text, Reginutė as text-to-speech, in a Lithuanian Assist pipeline
next to a Russian one. See `docs/DU_ASISTENTAI_HA.md`.

## Install path B — Home Assistant via Wyoming ⏳

Runs beside your existing Piper add-on, on its own port; nothing existing is
touched. Full recipe in `docs/DIEGIMAS_SERVERYJE.md` (Lithuanian, being written
during the live install; English version follows once it has worked once).

## Licence

Copyright © 2026 Robertas Tarasevičius.

Two licences, because this repository holds two different kinds of thing:

| What | Licence | File |
|---|---|---|
| **Code** — phonemizer, expander, Wyoming server, tooling | **GPL-3.0-only** (same as piper1-gpl) | `LICENSE` |
| **Voice** — `.onnx`, `.onnx.json`, samples (shipped via Release / Hugging Face, not in git) | **CC-BY-4.0** | `LICENSE-VOICE` |

The voice inherits CC-BY-4.0 from the LIEPA corpus. Lineage stated openly in
`hf/MODEL_CARD` and `hf/README.md`: fine-tuned from the Piper catalogue
checkpoint `ru_RU-irina-medium`, which was itself fine-tuned from
`en_US-lessac-medium`.

⚠️ CC-BY-4.0 requires attribution — see the section below, and keep it with
the voice files wherever they travel.

## Attribution

* LIEPA corpus — Vilnius University (project lead Gražina Korvel; corpus
  maintainer Gediminas Navickas); dataset published as
  `meldynamics/liepa-tts` on Hugging Face.
* Stress dictionary derived from
  [`svogunas/g2p-lt-lexicon`](https://huggingface.co/datasets/svogunas/g2p-lt-lexicon)
  by **Arūnas Smaliukas** (CC BY 4.0). Nearly every stressed word this voice
  speaks stands on his work — 176 637 of the 189 247 entries.
* **Ears: [`paprika-whisper-lt-v3`](https://huggingface.co/kristijonas/paprika-whisper-lt-v3)
  by [Kristijonas Jakubsonas](https://github.com/kristijonasatpro/paprika)**
  (CC-BY-4.0 / Apache-2.0). This voice would be half a system without it: you
  can speak Lithuanian to a house because he made the listening work first.
* Piper — Michael Hansen and the Open Home Foundation.
* The whole thing exists because Vilnius University published LIEPA openly
  instead of keeping it. Ten years of recordings, given away for the price of
  a citation.

---

## Lietuviškai, trumpai

Reginutė — lietuviškas balsas Piper sintezatoriui ir Home Assistant, išmokytas
iš Vilniaus universiteto LIEPA garsyno. Kadangi espeak-ng lietuvių kirčius
deda ne ten maždaug pusėje žodžių, balsas kalba per savo fonemizatorių su
kirčių žodynu — be jo gryname Piperyje jis netaria nieko. Diegimo instrukcija
rašoma **darant**, ant tikro serverio: `docs/DIEGIMAS_SERVERYJE.md`.
