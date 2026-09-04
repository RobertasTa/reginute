---
library_name: piper
license: cc-by-4.0
language:
- lt
tags:
- text-to-speech
- tts
- piper
- lithuanian
- onnx
datasets:
- meldynamics/liepa-tts
pipeline_tag: text-to-speech
---

# lt_LT-reginute1-medium — Piper voice (Lithuanian)

The first Lithuanian voice for [Piper](https://github.com/OHF-Voice/piper1-gpl).
Latvian and Estonian have been in the Piper catalogue for a long time;
Lithuanian never has.

- Language: Lithuanian (`lt_LT`)
- Voice: **female** — trained on the **LIEPA** corpus of Vilnius University,
  speaker Regina Jokubauskaitė (professional actress, studio recordings,
  5 121 utterances, ~3 h)
- Sample rate: 22 050 Hz · Quality: medium · Speakers: 1
- Files: `lt_LT-reginute1-medium.onnx` + `lt_LT-reginute1-medium.onnx.json`
  (**must stay together**) + `phonemize_lithuanian.py` + `lt_kirciai.tsv`
  (see below — the voice does not speak without them)

## ⚠️ This voice needs its phonemizer

Lithuanian has three phonemic pitch accents, and espeak-ng places Lithuanian
stress on the **wrong syllable in roughly half of the words** when checked
against the corpus' own gold annotation. So this voice is trained with
`phoneme_type: text` on IPA plus three accent marks (`ˈ ˌ ˋ`), and the text
must be phonemized by `phonemize_lithuanian.py` together with the stress
dictionary `lt_kirciai.tsv` (189 247 word forms, built from the LIEPA
annotations and Arūnas Smaliukas' `g2p-lt-lexicon`).

Plain Piper with a `text` voice feeds the model **raw letters, not IPA**, and
will not produce Lithuanian. A `PhonemeType.LITHUANIAN` contribution to
piper1-gpl (in the shape of `phonemize_japanese`) is being prepared; until it
lands, ship the two files next to the model.

Recommended: **`normalize_audio=False`** — Piper's default (`True`) clips this
voice.

## Licence and lineage

* **Voice files: CC-BY-4.0**, derived from the
  [`meldynamics/liepa-tts`](https://huggingface.co/datasets/meldynamics/liepa-tts)
  corpus (CC-BY-4.0), published by Vilnius University.
* **Lineage, stated openly:** fine-tuned from the Piper catalogue checkpoint
  `ru_RU-irina-medium`, which is itself fine-tuned from `en_US-lessac-medium`.
  The Lessac base has an unresolved licensing question (see piper-voices
  discussion #94); the training *data* here is CC-BY-4.0, and re-basing on the
  LibriTTS-R (CC-BY) base model is planned.
* Code (`phonemize_lithuanian.py` and the tooling around it): GPL-3.0, the same
  licence as piper1-gpl.

## Attribution (required by CC-BY-4.0)

* **LIEPA corpus (2013–2015)** — carried out by **Vilnius University**
  (Institute of Mathematics and Informatics; Faculty of Philology), with the
  **Institute of the Lithuanian Language**, the **Lithuanian University of
  Educational Sciences** (since 2019 the Education Academy of Vytautas Magnus
  University) and **Šiauliai University** (since 2021 the Šiauliai Academy of
  Vilnius University). Project lead **prof. Laimutis Telksnys**; corpus work
  and documentation **Gediminas Navickas**. The speaker is **Regina
  Jokubauskaitė** — everything anyone hears is her.
  Published to Hugging Face as
  [`meldynamics/liepa-tts`](https://huggingface.co/datasets/meldynamics/liepa-tts)
  by **MEL DYNAMICS, MB**.
  (LIEPA-3, led by **dr. Gražina Korvel**, is a different and much larger
  corpus — it is what the ASR model below is trained on, not this voice.)
* **Stress dictionary** — derived from
  [`svogunas/g2p-lt-lexicon`](https://huggingface.co/datasets/svogunas/g2p-lt-lexicon)
  by **Arūnas Smaliukas** (CC BY 4.0), and from the LIEPA annotations.
* **Ears, not ours but indispensable** —
  [`kristijonas/paprika-whisper-lt-v3`](https://huggingface.co/kristijonas/paprika-whisper-lt-v3)
  by **Kristijonas Jakubsonas**
  ([github.com/kristijonasatpro/paprika](https://github.com/kristijonasatpro/paprika)):
  Lithuanian ASR fine-tuned on LIEPA-3. Measured on our bench, it cut word
  error rate from 25.95 % (generic `whisper-large-v3-turbo`) to **7.63 %**.
  This voice is the mouth of a Lithuanian assistant; his model is the ears.
* **Piper** — Michael Hansen and the Open Home Foundation.

## Status

Trained and in daily use in a real Home Assistant installation (Wyoming TTS,
Lithuanian voice assistant beside a Russian one). Not yet submitted to the
official `rhasspy/piper-voices` catalogue.
