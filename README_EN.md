# Reginutė — Lithuanian voice for Piper TTS (`lt_LT-reginute1-medium`)

*Lietuviškai: [README.md](README.md) — the main page, because the voice is for
Lithuanians. This English version exists so that nobody has to read it through
a translator.*

> **Status.** The chain has been verified end to end: the voice speaks through
> the plain `piper` command, through a Wyoming server and through a Home
> Assistant smart speaker, in Lithuanian, beside a Russian assistant. The
> package passes **Piper's own catalogue check** (`_script/voicefest.py`).
> What is not fixed yet is the final training checkpoint: the model is still
> training, and the one that goes to Hugging Face will be the one a listener
> picks. This README is written *while* doing, not after.

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
| `AI_CONSULTANT_BRIEF.md` | If you ask an AI about this voice, give it this file first. It lists what must not be claimed (e.g. "the first Lithuanian TTS" — untrue) and the known limitations. |
| `sudaryk_zodyna.py`, `patikrink_pries_mokyma.py` | Build-side tools (dictionary builder, training-parity check). Contain Windows paths; not needed by users. |

## Install path A — plain Piper (no Home Assistant)

The released `piper-tts` wheel is enough — no fork, no patches.

```bash
pip install piper-tts             # 1.7.x
```

One directory needs five files: `lt_LT-reginute1-medium.onnx` and its
`.onnx.json` (from the Release or Hugging Face), and beside them
`phonemize_lithuanian.py`, `lt_kirciai.tsv` and `skaiciu_pletiklis.py`
(together with `zodziai_trumpi.txt`).

```python
from piper import PiperVoice
from phonemize_lithuanian import LithuanianPhonemizer
from skaiciu_pletiklis import isplesk
from synth_reginute import ReginuteSynth, i_int16
import wave

voice = PiperVoice.load("lt_LT-reginute1-medium.onnx",
                        config_path="lt_LT-reginute1-medium.onnx.json")
synth = ReginuteSynth(voice, LithuanianPhonemizer(),
                      length_scale=1.30, expand_text=isplesk)

audio = synth.synthesize("Laba diena. Kompensacija nuo 2000 eurų.")
with wave.open("out.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(synth.sr)
    w.writeframes(i_int16(audio))
```

The same in one command, via `demo_piper_wheel.py`:

```bash
python demo_piper_wheel.py lt_LT-reginute1-medium.onnx \
    lt_LT-reginute1-medium.onnx.json "Laba diena." out.wav
```

⚠️ **`normalize_audio` must stay `False`** (`ReginuteSynth` does that for
you). Piper's default of `True` raises the peak to 1.0 and clips this voice.

⚠️ **Without `skaiciu_pletiklis` the numbers come out wrong** — espeak-ng
reads Lithuanian digits with the wrong case endings and clock times as plain
numbers. `ReginuteSynth` calls it for you when given `expand_text=isplesk`.

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

⚠️ **Same caveat the author states about his own numbers, and it applies to
ours:** our test set is LIEPA-derived, i.e. **in-domain** for this model. His
card says plainly *„there is no valid out-of-domain number"*. Treat 7.63 % as
in-domain evidence, not as a general claim. On a recording of a
non-professional speaker in an ordinary room, the generic model lost whole
sentences while Paprika made about two ending errors in a hundred words — that
is anecdote, honestly labelled as such.

⚠️ **Use long-form decoding, not `chunk_length_s`** — the author's warning, and
he is right; we reproduced the failure before we understood it. Note that
`faster-whisper` (and therefore `wyoming-faster-whisper`, which is how a Home
Assistant setup usually runs it) takes the chunked path. For short voice
commands that is harmless — they fit in a single window — but the chunked
decoder is documented to invent text on silence, so a long recording deserves
`transcribe_file.py` from his repo instead.

In our house the two halves run side by side as Wyoming services: Paprika as
speech-to-text, Reginutė as text-to-speech, in a Lithuanian Assist pipeline
next to a Russian one. See `docs/DU_ASISTENTAI_HA.md`.

## Install path B — Home Assistant via Wyoming

Runs beside your existing Piper add-on, on its own port; nothing existing is
touched.

```bash
pip install piper-tts wyoming
python3 wyoming_reginute.py \
    --model lt_LT-reginute1-medium.onnx \
    --config lt_LT-reginute1-medium.onnx.json \
    --dictionary lt_kirciai.tsv \
    --uri tcp://0.0.0.0:10250 \
    --length-scale 1.30
```

In Home Assistant: **Settings → Devices & Services → Add integration →
Wyoming Protocol**, then the host and port 10250. The voice appears as
`reginute1`.

Full recipe with a systemd unit and container settings in
`docs/DIEGIMAS_SERVERYJE.md` (Lithuanian, written during the live install).
How one speaker runs two languages with two wake words:
`docs/DU_ASISTENTAI_HA.md`.

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

![Reginutė — lt_LT-reginute1-medium](docs/baneris.png)

CC-BY-4.0 asks for a corpus to be credited. A corpus is made by people, so
they are named here too. None of them has seen this project; none of the
institutions below endorses it. The logos above say *thank you*, nothing more.

### The recordings — LIEPA (2013–2015)

The voice is trained on the synthesis part of the **LIEPA** corpus
(*LIEtuvių šneka valdomos PAslaugos* — "Lithuanian speech-controlled
services"), which produced a reader speaking in four voices. This is one of
those four.

* Carried out by **Vilnius University** (Institute of Mathematics and
  Informatics; Faculty of Philology).
* Partners: **Institute of the Lithuanian Language**, **Lithuanian University
  of Educational Sciences** (since 2019 the Education Academy of **Vytautas
  Magnus University**), **Šiauliai University** (since 2021 the Šiauliai
  Academy of Vilnius University).
* Led by **prof. Laimutis Telksnys**, who started asking whether a machine
  could talk with a person in 1967 — the LIEPA presentations still open with
  that date. This voice is a late footnote to a question asked 58 years ago.
* Corpus work and documentation — **Gediminas Navickas** (VU MIF), whose 2025
  seminar slides are the source for everything stated above.
* The speaker: **Regina Jokubauskaitė**. Everything anyone hears is her —
  her timbre, her pace, her way of ending a sentence. The model only learned
  to rearrange it.
* Published to Hugging Face as
  [`meldynamics/liepa-tts`](https://huggingface.co/datasets/meldynamics/liepa-tts)
  by **MEL DYNAMICS, MB**, under CC-BY-4.0. Without that upload the corpus
  would still exist and still be unusable.

The family continued: **LIEPA-2** (1 000 h) and **LIEPA-3** (10 000 h, led by
**dr. Gražina Korvel**), and it is LIEPA-3 that Paprika below is trained on.
Different corpus, same decision — publish it rather than keep it.

### The dictionary

Stress dictionary derived from
[`svogunas/g2p-lt-lexicon`](https://huggingface.co/datasets/svogunas/g2p-lt-lexicon)
by **Arūnas Smaliukas** (CC BY 4.0). Nearly every stressed word this voice
speaks stands on his work — 176 637 of the 189 247 entries.

### The ears

**[`paprika-whisper-lt-v3`](https://huggingface.co/kristijonas/paprika-whisper-lt-v3)
by [Kristijonas Jakubsonas](https://github.com/kristijonasatpro/paprika)**
(CC-BY-4.0 / Apache-2.0). This voice would be half a system without it: you
can speak Lithuanian to a house because he made the listening work first.

### The pointer

**Linas Petkevičius, PhD** — President of AI Lithuania and Director of the
Institute of Computer Science at Vilnius University. In a public LinkedIn
thread about how the LIEPA-3 recordings were being distributed, he wrote the
comment that laid out who had put the data on Hugging Face and who had
trained a Lithuanian model on it. That comment is where this project started:
without it we would not have found Paprika, and would not have gone looking
for the corpus this voice is made of. He owes us nothing and knew nothing
about us — which is rather the point. **A single accurate public comment can
be worth more than a project plan.**

### Piper

**Michael Hansen** and the **Open Home Foundation** — for a text-to-speech
system small enough to run on a home server and open enough that a language
with three million speakers can add itself without asking permission.

---

The whole thing exists because Vilnius University published LIEPA openly
instead of keeping it. Ten years of recordings, given away for the price of
a citation.

---

## Lietuviškai

Pilnas aprašas lietuvių kalba — **[README.md](README.md)**. Jis yra pagrindinis
šio katalogo puslapis: balsas skirtas lietuviams, tad jų kalba čia pirma.
