"""Tests for the Lithuanian phonemizer (piper-style, pytest).

Run:  _darbal\\pw_venv\\Scripts\\python.exe -m pytest _irankiai\\piper_lt -q
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from phonemize_lithuanian import (  # noqa: E402
    ACUTE,
    CIRCUMFLEX,
    GRAVE,
    LithuanianPhonemizer,
    ipa_vowel_groups,
    place_accent,
)


@pytest.fixture(scope="module")
def phonemizer() -> LithuanianPhonemizer:
    return LithuanianPhonemizer()


def joined(phonemes):
    return ["".join(s) for s in phonemes]


# --- pure functions ---------------------------------------------------------

def test_vowel_groups_merge_adjacent_vowels_and_length():
    assert ipa_vowel_groups("kaɭbʲeedamas") == [1, 5, 8, 10]
    assert ipa_vowel_groups("vaːjɪkai") == [1, 4, 6]   # espeak splits "ai"


def test_place_accent_syllable_boundaries():
    # V-CV: mark goes before the consonant of the accented syllable
    assert place_accent("kaɭˈbʲeedamas", 1, ACUTE) == "kaɭˈbʲeedamas"
    # word-initial cluster belongs to the first syllable
    assert place_accent("tʲrʲˈisdʲeɕimt", 0, GRAVE) == "ˋtʲrʲisdʲeɕimt"
    # syllabic l̩ (l + U+0329) stays together
    assert place_accent("poːtʲenʲtsʲijal̩u", 4, GRAVE) == "poːtʲenʲtsʲijaˋl̩u"
    # unknown group index: unchanged
    assert place_accent("ˈir", 5, GRAVE) == "ˈir"


# --- words --------------------------------------------------------------------

@pytest.mark.parametrize(
    "word, expected",
    [
        ("kalbėdamas", "kaɭˈbʲeedamas"),   # tvirtapradė from liepa
        ("kur", "ˌkur"),                    # tvirtagalė on a mixed diphthong
        ("dabar", "daˌbar"),
        ("trisdešimt", "ˋtʲrʲisdʲeɕimt"),  # trumpinė, word-initial cluster
        ("maistas", "ˌmaistas"),            # a diphthong never takes trumpinė
    ],
)
def test_dictionary_accents(phonemizer, word, expected):
    assert phonemizer.phonemize_word(word) == expected


@pytest.mark.parametrize(
    "word, expected",
    [
        ("vaikai", "vaːjɪˌkai"),            # espeak splits ai -> aːjɪ
        ("taika", "taːjɪˋka"),
        ("palaikai", "pal̩aːjɪˌkai"),
        ("potencialu", "poːtʲenʲtsʲijaˋl̩u"),
    ],
)
def test_ipa_group_overrides(phonemizer, word, expected):
    assert phonemizer.phonemize_word(word) == expected


@pytest.mark.parametrize(
    "word, expected",
    [
        ("ir", "ˈir"),        # in-process espeak leaves monosyllables bare;
        ("bet", "bʲˈet"),     # the CLI (training data) marks before the vowel
        ("jau", "jˈau"),
        ("o", "ˈoː"),
    ],
)
def test_monosyllables_get_espeak_style_stress(phonemizer, word, expected):
    assert phonemizer.phonemize_word(word) == expected


def test_letter_names_match_the_training_data(phonemizer):
    # The model learned letter names from Regina's own recordings, where LIEPA
    # writes them as plain words inside a sentence:
    #   "Rusijos ir Europos Sajungos E ES."  ->  ... ˌea ˈes
    #   "Kurio kodas isiterpe i musu DE EN ER."  ->  ... dʲˈee ˈen ˈer
    # So the phonemizer must reproduce espeak's own rendering, not a
    # hand-written "nicer" one.
    assert phonemizer.phonemize_sentence("e es").startswith("ˌea ")
    assert "dʲee" in phonemizer.phonemize_sentence("dė en er")


def test_letter_l_is_not_read_as_elektroninis(phonemizer):
    # espeak expands "el" to "elektroninis" (the e-mail abbreviation), which
    # turned "MTL" into "em te elektroninis".
    assert "eɭektron" not in phonemizer.phonemize_sentence("em tė el")
    assert phonemizer.phonemize_sentence("em tė el").endswith("ˈel̩")
    # the real abbreviation keeps its expansion
    assert "eɭektron" in phonemizer.phonemize_sentence("el. paštas")


def test_no_retroflex(phonemizer):
    for word in ["visi", "senatvės", "rasti", "asmenines"]:
        assert "ʂ" not in phonemizer.phonemize_word(word)


def test_case_insensitive_lookup(phonemizer):
    assert phonemizer.phonemize_word("Dabar") == phonemizer.phonemize_word("dabar")


def test_every_word_has_exactly_one_accent(phonemizer):
    for word in ["kalbėdamas", "kur", "vaikai", "ir", "Reginutė", "nežinomasžodis"]:
        ipa = phonemizer.phonemize_word(word)
        assert sum(ipa.count(m) for m in (ACUTE, CIRCUMFLEX, GRAVE)) == 1, (word, ipa)


# --- sentences ----------------------------------------------------------------

def test_sentences_and_punctuation(phonemizer):
    out = joined(phonemizer.phonemize("Labas rytas, Robertai! Ar kalbėsim lietuviškai?"))
    assert len(out) == 2
    assert out[0].endswith("!") and "," in out[0]
    assert out[1].endswith("?")
    assert out[0].split()[0] == "ˌl̩abas"


def test_output_is_single_codepoints(phonemizer):
    for sentence in phonemizer.phonemize("Šiandien trisdešimt laipsnių."):
        assert all(len(p) == 1 for p in sentence)


def test_empty_text(phonemizer):
    assert phonemizer.phonemize("") == []
    assert phonemizer.phonemize("   ") == []


def test_expand_text_hook():
    calls = []

    def expand(text):
        calls.append(text)
        return text.replace("3", "trys")

    ph = LithuanianPhonemizer(expand_text=expand)
    out = joined(ph.phonemize("3 vaikai."))
    assert calls == ["3 vaikai."]
    assert out[0].startswith("ˌtʲrʲiːs")     # trỹs: tvirtagalė from the dictionary
