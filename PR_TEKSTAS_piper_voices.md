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

**One thing needs your opinion.** Lithuanian has three phonemic pitch
accents, and espeak-ng puts the stress on the wrong syllable in roughly half
of the words when checked against the corpus' own gold annotation. So the
voice is trained with `phoneme_type: text` on IPA plus three accent marks,
and the text has to be phonemized by a small module I wrote
(`phonemize_lithuanian.py`, ~250 lines, plus a stress dictionary of 189k word
forms derived from the corpus annotations and `svogunas/g2p-lt-lexicon`,
both CC-BY-4.0). It follows the shape of `phonemize_japanese.py`. Without it,
a `text` voice receives raw letters, so the model is only useful with the
module beside it.

I asked Ihor about the code side and he said a PR would be welcome, so I'm
preparing one for piper1-gpl adding `PhonemeType.LITHUANIAN` in the same shape
as the Japanese and Chinese paths, with the dictionary resolved through
`--data-dir` the way g2pw data is. The phoneme_id_map is the default one with
a single symbol appended at the end (`ˋ` = 166) for the third accent; ˈ and ˌ
are the existing ones, and PAD/BOS/EOS are unchanged.

So nothing is needed from you on that front - but if you would rather the
phonemizer stayed in the voice repo instead of in piper1-gpl, say so and I
will keep it there. Happy to do the packaging whichever way suits the
catalogue; the files are ready either way, with SHA256SUMS.

Two practical notes for the catalogue side. `samples/speaker_0.mp3` was
generated the way `generate-samples.sh` does it, from the first sentence of a
`test_sentences/lt.txt` (the Lithuanian Wikipedia rainbow sentence, same as
the other languages) - I'm sending that file to piper-samples as a separate
small PR. Because of the `text` phoneme type, running `python3 -m piper` on
this voice without the module produces raw letters, so if you regenerate the
sample, please run it through the phonemizer or keep the shipped one. And I
added the `lt_LT` line to `_script/voicefest.py` and the `voices.json` entry
(md5 and sizes from the shipped files) so nothing needs regenerating.

The voice has been running in a real Home Assistant setup (Wyoming TTS) for a
few days, answering a smart speaker in Lithuanian. Known rough edges are
listed openly in the model card rather than left for people to find.
