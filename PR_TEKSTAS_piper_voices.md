Contribution: Lithuanian voice lt_LT-reginute1-medium (LIEPA corpus, CC-BY-4.0)

Hello! I've trained a Lithuanian voice and put it up here:

**https://huggingface.co/RobertasTa/lt_LT-reginute1-medium**

The training data is the LIEPA corpus from Vilnius University, published on
the Hub as `meldynamics/liepa-tts` under **CC-BY-4.0** — a professional
actress, studio recordings, 5121 utterances, about 3 hours. Attribution is in
the model card. The voice files are CC-BY-4.0 as well.

Lineage, so it is on the record rather than discovered later: it is
fine-tuned from the catalogue checkpoint `ru_RU-irina-medium`, which is
itself fine-tuned from `en_US-lessac-medium`. I saw your note in #94 that the
Lessac base has not been tested legally and that you are moving to the
LibriTTS-R base — re-basing on that is on my list for the next version. The
training *data* licence above is unaffected either way.

The catalogue currently has Latvian and Estonian, but there has never been a
Lithuanian voice in it. There was one request in piper1-gpl#726 in early
2025; the person closed it themselves the next day, and the licence question
in that thread was never answered. That is the gap this fills.

**The one thing that is different about this voice.** Lithuanian has three
phonemic pitch accents, and espeak-ng puts the stress on the wrong syllable
in roughly half of the words when checked against the corpus' own gold
annotation. So the voice is trained on IPA plus three accent marks, and the
text is phonemized by a small module (`phonemize_lithuanian.py`, ~250 lines,
plus a stress dictionary of 189k word forms derived from the corpus
annotations and `svogunas/g2p-lt-lexicon`, both CC-BY-4.0). It follows the
shape of `phonemize_japanese.py`. Ihor said a PR would be welcome, so the
module is submitted to piper1-gpl as `PhonemeType.LITHUANIAN`:
**<piper1-gpl PR URL>** — dictionary resolved through `--data-dir` the way
g2pw data is, phoneme_id_map = the default one plus a single symbol appended
at the end (`ˋ` = 166) for the third accent, PAD/BOS/EOS unchanged.

The `.onnx.json` in this PR therefore says `"phoneme_type": "lithuanian"`.

## Notes for whoever merges this

Written down here so nothing depends on an email thread.

1. **This PR depends on piper1-gpl PR <N>.** A Piper without it refuses to
   load the voice with `'lithuanian' is not a valid PhonemeType` — a clean
   failure. With `"text"` instead, Piper would feed the model raw letters and
   the voice would come out as noise; I tested that by accident, which is why
   the config says `lithuanian`. If you prefer to hold this until the code PR
   is released, that is entirely reasonable.
2. **Please keep `samples/speaker_0.mp3`.** It was generated the way
   `generate-samples.sh` does it, from the first line of a
   `test_sentences/lt.txt` (Lithuanian Wikipedia's rainbow sentence, same
   source as `lv.txt` / `et.txt`; sent to piper-samples as a separate small
   PR), through the module. Regenerating it with a Piper that lacks the
   phonemizer will fail (or, with a `text` config, produce noise).
3. **The stress dictionary (`lt_kirciai.tsv`, 3 MB) is not in this folder** —
   no catalogue voice ships extra files, and I did not want to start. It
   lives in the voice repo; the phonemizer resolves it through `--data-dir`
   (or next to the model) and fails with a clear message if it is missing.
   For making that automatic there are two precedents in Piper — bundling
   in the package the way the Hebrew models are (they are 25 MB, this is 3),
   or a `_resources` archive in `piper-checkpoints` that Piper downloads on
   first use the way g2pW is. I've asked Ihor which he prefers; if you have a
   preference for the catalogue side, say so and I'll do it that way.
4. `_script/voicefest.py` has the `lt_LT` language line and `voices.json`
   has the entry with md5/sizes from the shipped files, so nothing needs
   regenerating.
5. Questions: here, or robertast@inbox.eu.

The voice has been running in a real Home Assistant setup (Wyoming TTS) for a
few days, answering a smart speaker in Lithuanian. Known rough edges are
listed openly in the model card rather than left for people to find.
