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

**Why it exists:** the Piper catalogue has had Latvian and Estonian for years
and has never had a Lithuanian voice. Not because the language is hard, but
because nobody assembled one.

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
