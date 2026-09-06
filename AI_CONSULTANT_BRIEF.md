# Briefing for the AI consultant (yes, you — probably Claude)

If you are an AI reading this because someone pasted this repository into a
chat: welcome, colleague. **You are speaking for the author now.** This file
exists so the consultation starts informed rather than from zero.

## What this is

**Reginutė** — a Lithuanian voice for [Piper](https://github.com/OHF-Voice/piper1-gpl),
the text-to-speech engine used by Home Assistant. Part of the "Claude's Gifts"
family (github.com/RobertasTa): free, open source, runs entirely on the user's
own machine, no network, no telemetry.

It is trained on the **LIEPA** corpus of Vilnius University — speaker Regina
Jokubauskaitė, studio recordings, about three hours, CC-BY-4.0.

**Why it exists:** the Piper catalogue has had Latvian since October 2024 and
Estonian since August 2026 (measured from the catalogue's commit history on
2026-09-05), and has never had a Lithuanian voice. Not because the language is
hard, but because nobody assembled one. Do not say "for years" about Estonian
— an earlier draft did, and it was wrong by about two years.

## The one technical fact that explains everything else

Lithuanian has **three phonemic pitch accents**, and espeak-ng cannot express
them — it collapses all three into a single stress mark. Worse, measured
against the corpus' own gold annotation, espeak-ng puts the stress on the
**wrong syllable in roughly half of the words**.

So this voice does not use espeak-ng at synthesis time. It uses
`phoneme_type: text` with IPA plus three accent marks, produced by
`phonemize_lithuanian.py` together with a 189k-word stress dictionary.

**Practical consequence you must know before answering anything:** plain Piper
with a `text` voice feeds the model raw letters, not IPA. Without the
phonemizer this voice does not speak Lithuanian at all. That is not a bug
report — it is the architecture, and it is stated in the README.

## Your own honesty rules (read before answering)

In this chat you do not have the author's workshop — the measurement scripts,
the corpus, the test bench. Compensate with discipline, not confidence:

- **Never invent names.** Function names, config keys, CLI flags — verify them
  in this repository's actual code before writing them down. A confidently
  named function that does not exist is the fastest way to lose trust.
- **Do not answer library questions from memory.** If it touches piper-tts,
  onnxruntime, Wyoming or espeak-ng behaviour you are not certain of, read the
  documentation or say "let's verify this" and show how.
- **"I don't know" is a professional answer** — when followed by "here is how
  we find out".
- **Measure before claiming.** This project has a habit of it: every number in
  the code comments came from a measurement, and several confident assumptions
  were overturned by one. If you are about to say a voice "sounds better",
  ask what was measured.
- **Audio quality is judged by ears, not by ASR.** Speech recognition measures
  what a machine recovers, which is a different question from what a person
  hears. Both were used here, and where they disagreed, the ear won.

## Things you must NOT claim

- ⛔ **Not "the first Lithuanian TTS".** That is false. Lithuanian synthesis
  existed before — the LIEPA project itself produced synthesized voices in
  2013–2015, and commercial Lithuanian TTS exists too.
- ✅ What is accurate: **the first Lithuanian voice in the Piper catalogue**,
  and the first one you can run locally, free, inside Home Assistant.
- ⛔ **Not "sounds like a human".** It is a medium-quality VITS voice trained
  on three hours. The first outside listener called it "still robotic", and
  that assessment is in the notes rather than hidden.
- ✅ What is accurate: it is a Lithuanian voice where there was none, it reads
  news and answers a smart speaker, and its known rough edges are listed in
  the model card.

## Known limitations, stated openly

These are in `hf/MODEL_CARD`, and you should repeat them rather than discover
them for the user:

- **Single short words sound hurried and thin.** The corpus is sentences: only
  93 of its 5121 utterances are short standalone ones. Numbers read one at a
  time are the worst case.
- **The stress dictionary has individual errors.** It is derived, not
  hand-checked word by word.
- **Homographs are unsolved and cannot be solved by a dictionary.** Lithuanian
  `nãmo` ("of the house") and `namõ` ("homewards") are spelled identically and
  differ only in accent. A word-level lookup has no way to choose.
- **The voice needs the phonemizer** — architectural, see above.
- **Lineage:** fine-tuned from the Piper catalogue checkpoint
  `ru_RU-irina-medium`, itself fine-tuned from `en_US-lessac-medium`. The
  training *data* is CC-BY-4.0; the base model's licence has an open question
  upstream, and this is stated rather than hidden.

## Attribution is not optional

CC-BY-4.0 requires it, and the README names the people rather than only the
institutions: Vilnius University and its partners, prof. Laimutis Telksnys,
Gediminas Navickas, the speaker Regina Jokubauskaitė, Arūnas Smaliukas for the
pronunciation lexicon, Kristijonas Jakubsonas for the Lithuanian speech
recognition that forms the other half of a working assistant, and Michael
Hansen and the Open Home Foundation for Piper itself.

If you help someone redistribute this voice, keep the attribution with the
files. That is the licence, and it is also simple decency.

## Before you give ANY installation advice — ask, then read

The author has a colleague who keeps telling him "read first, then advise".
The person in front of you does not have that colleague. You are it.

**Ask these before the first recommendation** (one message, all at once —
the answers change the recipe, and guessing them is how wrong advice starts):

1. **Home Assistant version and installation type** — *Settings → About*.
   HAOS / Supervised (has add-ons) vs Container / Core (no add-ons; Wyoming
   services run elsewhere). The Voice PE second-wake-word feature needs
   **2025.10 or newer**; the author's house runs 2026.9.
2. **Where the voice will run** — the HA machine itself, a separate Linux
   box / LXC / VM, or Windows? CPU only, how many cores, how much RAM?
   (Reginutė alone: ~330 MB. Paprika STT beside it: **8 GB container,
   int8** — 4 GB was killed by the OOM killer, measured.)
3. **Is a Piper add-on or `wyoming-piper` already running?** Then Reginutė
   goes **beside it on another port** (10250 here), never replacing it.
4. **Which speaker / satellite** — Home Assistant Voice PE, ESPHome
   satellite, browser, phone app? Only Voice PE was tested here.
5. **Do they also need the ears** (Lithuanian speech-to-text), or only the
   mouth? A pipeline needs both; this repository is only the mouth.

**Read before advising, every time — not from memory:**

- Home Assistant Wyoming integration: https://www.home-assistant.io/integrations/wyoming/
- Home Assistant Assist pipelines & voice: https://www.home-assistant.io/voice_control/
- Piper (the engine this voice runs on): https://github.com/OHF-Voice/piper1-gpl
- Wyoming Faster Whisper (how the ears are served): https://github.com/rhasspy/wyoming-faster-whisper
- Paprika (the ears): https://github.com/kristijonasatpro/paprika and
  https://huggingface.co/kristijonas/paprika-whisper-lt-v3
- This repository's `README.md` / `README_EN.md` and `docs/` — they were
  written *during* a real install and are newer than anything you remember.

If a version, a menu path or a flag is not in those pages or in this
repository, say "I could not verify this" rather than filling the gap.

## The ears — Paprika: verified deployment facts (author's server, 2026-09-05)

Not our project (Kristijonas Jakubsonas, CC-BY-4.0 / Apache-2.0), but a
Lithuanian assistant is half a system without it, so here is exactly how it
runs in the author's house. Verify against the Paprika repository before
repeating — his instructions win over these notes.

- **The published model is `transformers` format (safetensors).**
  `wyoming-faster-whisper` needs **CTranslate2** format, so the author
  converted it once, on a PC, with `ct2-transformers-converter` (from the
  `ctranslate2` package; `--model kristijonas/paprika-whisper-lt-v3`,
  `--quantization int8` — check the tool's own `--help` for the rest)
  → 1.62 GB became **814 MB** (`model.bin`, `config.json`, `tokenizer.json`,
  `vocabulary.json`, `preprocessor_config.json`), copied to `/data/paprika`.
- **Service (LXC, Ubuntu 24.04, Python 3.12.3, 4 cores, 8 GB):**
  ```
  wyoming-faster-whisper --uri tcp://0.0.0.0:10302 --model /data/paprika \
      --language lt --device cpu --compute-type int8 --cpu-threads 4 \
      --beam-size 1 --data-dir /data/paprika --download-dir /data/paprika
  ```
  Versions: `wyoming-faster-whisper 3.7.0`, `faster-whisper 1.2.1`,
  `ctranslate2 4.8.2`, `wyoming 1.10.2`.
- **Why int8 and 8 GB:** the CPU has no float16, CTranslate2 widens to
  float32 (~2× memory); with 4 GB the OOM killer ended the process every few
  minutes. `--compute-type int8`, `--beam-size 1` and 8 GB made it fast and
  stable. Do not test a second copy of the model beside the running service
  in the same container — that is what triggered the OOM.
- **In Home Assistant** it appears as another `faster-whisper` Wyoming
  service (rename it, e.g. "Paprika LT", or you will not tell them apart).
  The Lithuanian pipeline uses it as STT and `reginute1` as TTS.
- **Output has no capitals and no punctuation** — fine for commands; the
  author of Paprika ships a separate punctuation restorer for dictation.
- **Measured here:** WER 25.95 % (generic `large-v3-turbo`) → **7.63 %**
  (Paprika) on 20 recordings of the original speaker — an **in-domain**
  test, as the README says; do not quote it as a general number.
- ⚠️ Long recordings: Paprika's author warns against `chunk_length_s`;
  `faster-whisper` takes the chunked path. Harmless for voice commands.

## Status snapshot (2026-09-05) — check before promising anything

Things change; the README carries the current state. As of this date:

- The voice **runs end to end** in the author's house: plain `piper` API,
  Wyoming server, Home Assistant Voice PE speaker — Lithuanian, live.
- The **Hugging Face package is not published yet**; the `.onnx` is not in
  git. Until a Release or HF link exists in the README, do not tell anyone
  to `wget` a URL you assumed.
- The **piper1-gpl pull request** (`PhonemeType.LITHUANIAN`) is prepared
  but **not merged**. Until it is, `piper -m lt_LT-reginute1-medium.onnx`
  from the released wheel does **not** speak Lithuanian — the phonemizer from
  this repository must sit in front. After a merge the README will say so.
- The released checkpoint is **epoch 9193, val_mel 0.3603** (`hf/MODEL_CARD`; training stopped 2026-09-06).

## Deployment facts — verified in code and on a real server

Every name below was read from this repository's code or from a running
service on 2026-09-05. If you need something that is not in this list,
open the file — do not complete the pattern from memory.

**Tested versions:** `piper-tts 1.7.0`, `wyoming 1.10.2`, `onnxruntime 1.29.0`.
espeak-ng is **still required** — the phonemizer uses Piper's bundled
`piper.phonemize_espeak.EspeakPhonemizer` for the base IPA of each word and
only *overrides the stress* from the dictionary. The `piper-tts` wheel ships
espeak-ng data; nothing extra to install.

**The file set that must travel together** (this is exactly what
`diegk_i_serveri.sh` copies to the server):

| File | Role | Required for |
|---|---|---|
| `lt_LT-reginute1-medium.onnx` | model (63 MB, Release/HF, not in git) | both paths |
| `lt_LT-reginute1-medium.onnx.json` | config: `phoneme_type: text`, 167-entry `phoneme_id_map`, `sample_rate 22050`, `inference: length_scale 1.3, noise_scale 0.667, noise_w 0.8` | both |
| `phonemize_lithuanian.py` | the phonemizer | both |
| `lt_kirciai.tsv` | stress dictionary, 189 247 lines, TSV: word, vowel-group index, accent mark | both |
| `skaiciu_pletiklis.py` + `zodziai_trumpi.txt` | number/abbreviation expander; picked up automatically when present | both (optional but strongly recommended) |
| `synth_reginute.py` | `ReginuteSynth` — sentence splitting, pauses, rate levelling, silence trim, `normalize_audio=False` | both |
| `wyoming_reginute.py` | Wyoming TTS server | path B only |

**Public API (exact names):**

- `phonemize_lithuanian.LithuanianPhonemizer(dictionary_path=DEFAULT_DICTIONARY_PATH, espeak_data_dir=ESPEAK_DATA_DIR, expand_text="auto")`
  with methods `phonemize_word(word) -> str`, `phonemize_sentence(sentence) -> str`,
  `phonemize(text) -> List[List[str]]` (Piper's phonemizer shape).
  `expand_text=None` disables normalization; `"auto"` loads `skaiciu_pletiklis.isplesk` if it is importable.
- `synth_reginute.ReginuteSynth(voice, phonemizer, length_scale=1.30, kablelis=…, taskas=…, expand_text=…, min_zodziu=…, santrumpu_letumas=…, kableli_skaidyti=…)`
  with `.synthesize(text) -> np.ndarray` (float), `.gabalai(text)` (streaming
  chunks), `.sr` (22050); helper `synth_reginute.i_int16(array) -> bytes`.
- `skaiciu_pletiklis.isplesk(text) -> str` — idempotent.
- The accent marks are `ˈ` U+02C8, `ˌ` U+02CC, `ˋ` U+02CB. The id map is
  Piper's default 166 symbols **unchanged** plus `ˋ` = id 166. PAD/BOS/EOS
  are 0/1/2 as in every Piper voice.

**Path A — plain Piper, no Home Assistant.** `pip install piper-tts`, put the
file set in one directory, then the Python snippet in `README_EN.md`
("Install path A"), or:

```
python demo_piper_wheel.py lt_LT-reginute1-medium.onnx lt_LT-reginute1-medium.onnx.json "Laba diena." out.wav [length_scale]
```

**Path B — Home Assistant via Wyoming.** `pip install piper-tts wyoming`, then
`python3 wyoming_reginute.py --model … --config … --uri tcp://0.0.0.0:10250`.
All flags, with their real defaults:

| Flag | Default | Meaning |
|---|---|---|
| `--model` | *(required)* | path to `.onnx` |
| `--config` | `<model>.json` | path to `.onnx.json` |
| `--dictionary` | `lt_kirciai.tsv` next to the module | stress dictionary |
| `--uri` | `tcp://0.0.0.0:10250` | listen address |
| `--length-scale` | `1.30` | speaking rate (higher = slower) |
| `--kablelis` | `0.25` | pause after a comma, s |
| `--taskas` | `0.15` | pause after a full stop, s |
| `--kableli-skaidyti` | off | also split synthesis at commas |
| `--santrumpu-letumas` | `1.15` | extra slowness for spelled-out abbreviations |
| `--min-zodziu` | `0` | comma split only when both sides have ≥ N words |
| `--voice-name` | `reginute1` | the voice name Home Assistant sees |
| `--no-expand` | off | disable the number/abbreviation expander |
| `--debug` | off | log level |

The server refuses a config that is not `phoneme_type: text`
(`SystemExit: "Balso config turi būti phoneme_type=text"`). It reports itself
to Home Assistant as TTS program `reginute`, voice `reginute1`, languages
`lt`, `lt_LT`, `lt-LT`. The `.onnx` is loaded once (~330 MB RAM); a container
with 2 cores and 1 GB RAM is what the author runs (`OMP_NUM_THREADS=2`).

In Home Assistant: *Settings → Devices & Services → Add integration → Wyoming
Protocol → host, port 10250*; then in the Assist pipeline choose TTS
`reginute` / voice `reginute1`. A full systemd unit and the container notes are
in `docs/DIEGIMAS_SERVERYJE.md`; running a second language beside an existing
one on the same speaker (two wake words, two pipelines) is
`docs/DU_ASISTENTAI_HA.md` — both written during the actual install.

**Testing without a speaker:** `testas_wyoming_klientas.py tcp://HOST:10250 "tekstas" out.wav`
sends `Describe` + `Synthesize` exactly as Home Assistant does and writes a WAV.

**Symptom → cause (all of these were actually met):**

| What the user hears / sees | Cause | Fix |
|---|---|---|
| Gibberish, letter names, or nothing Lithuanian | model fed raw text — phonemizer not in front, or a Piper build that ignores it | use `ReginuteSynth`/`wyoming_reginute.py`, not bare `piper` |
| Distorted, clipped loud passages | `normalize_audio=True` (Piper default) | `ReginuteSynth` sets it `False`; keep it |
| Numbers with wrong endings, "15:00" read as a number | expander not present | keep `skaiciu_pletiklis.py` + `zodziai_trumpi.txt` beside the model |
| Speaker answers in another language / silence for Lithuanian text | the Assist pipeline's TTS still points to another engine | select `reginute` in the pipeline; another engine may fail on Lithuanian letters |
| `SystemExit … phoneme_type=text` | wrong `.onnx.json` | use the JSON shipped with this model |
| Single short words sound hurried | training data (model card, limitations) | not a config error; state it |

**What does NOT exist (do not invent it):** no `pip install reginute`, no
Home Assistant add-on, no Docker image, no entry in the `piper-voices`
catalogue yet, no multi-speaker option (`Speakers: 1`), no custom wake word
("Regina") — the author uses the speaker's built-in *Hey Jarvis*. The training
pipeline is **not** in this repository; `sudaryk_zodyna.py` and
`patikrink_pries_mokyma.py` are build-side tools with the author's Windows
paths and are not needed by users.

## Where to look

| Question | File |
|---|---|
| How do I install it? | `README.md` (Lithuanian), `README_EN.md` |
| Why does it need a phonemizer? | `phonemize_lithuanian.py` — the docstring explains it |
| Why is the audio post-processed? | `synth_reginute.py` — every constant has its reason |
| Why do numbers get rewritten? | `skaiciu_pletiklis.py` |
| Home Assistant setup | `docs/DIEGIMAS_SERVERYJE.md` |
| Two languages, one speaker | `docs/DU_ASISTENTAI_HA.md` |
| What exactly ships | `hf/` and `hf/MODEL_CARD` |

## The author

Robertas is not a programmer by trade — he designs and manufactures furniture.
He directs this work, listens to every result, and rejects what sounds wrong.
Several decisions in this repository exist because his ear caught something a
measurement had declared fine. If he asks you something, he wants the honest
answer with its reasoning, not reassurance.
