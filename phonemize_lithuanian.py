"""Lithuanian phonemization: espeak-ng IPA + dictionary-based pitch accent.

espeak-ng's Lithuanian voice produces good phonemes but places stress
incorrectly in roughly half of the words, and it cannot express the three
Lithuanian pitch accents (tvirtapradė / tvirtagalė / trumpinė) at all - it
collapses all of them into a single primary-stress mark. Pitch accent changes
both meaning and pronunciation in Lithuanian (kártas "time" vs kar̃tas
"bitter"), and it is the main lever for natural-sounding Lithuanian speech.

This phonemizer keeps espeak-ng as the phoneme source (each word is phonemized
separately, so the output is deterministic per word) and then:

1. replaces the retroflex ʂ that espeak-ng emits for plain "s" in some
   contexts (Lithuanian has no retroflex consonants) with s;
2. looks the word up in a stress dictionary (word -> vowel group index and
   pitch accent mark) built from the liepa-tts annotated corpus and the
   svogunas/g2p-lt-lexicon pronunciation lexicon, both CC-BY-4.0;
3. moves the stress mark to the syllable that carries the accent, using one
   of three marks: ˈ (tvirtapradė, acute), ˌ (tvirtagalė, circumflex) and
   ˋ (trumpinė, grave; U+02CB, added to the voice's phoneme id map).

Words missing from the dictionary keep espeak-ng's own stress placement.
The output uses single-codepoint phonemes (NFD), matching how espeak
phonemes are keyed in the voice's phoneme_id_map.
"""

import logging
import re
import unicodedata
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple, Union  # noqa: F401

try:  # inside the piper package
    from .phonemize_espeak import ESPEAK_DATA_DIR, EspeakPhonemizer
except ImportError:  # standalone use next to an installed piper-tts
    from piper.phonemize_espeak import ESPEAK_DATA_DIR, EspeakPhonemizer

_LOGGER = logging.getLogger(__name__)

_DIR = Path(__file__).parent
DEFAULT_DICTIONARY_PATH = _DIR / "lt_kirciai.tsv"

ESPEAK_VOICE = "lt"

# Pitch accent marks (must exist in the voice's phoneme_id_map).
ACUTE = "ˈ"        # tvirtapradė (falling), U+02C8 - espeak primary stress
CIRCUMFLEX = "ˌ"   # tvirtagalė (rising), U+02CC - espeak secondary stress
GRAVE = "ˋ"        # trumpinė (short), U+02CB - new symbol
STRESS_MARKS = ACUTE + CIRCUMFLEX + GRAVE

IPA_VOWELS = "aeiouɑɐɔɛɪʊæøɘəɜ"
LENGTH = "ː"
# Symbols that attach to the preceding consonant (palatalization, syllabic l̩).
CONSONANT_MODIFIERS = "ʲʷʰ̩"

# espeak-ng splits some Lithuanian diphthongs into three sounds
# ("vaikai" -> vaːjɪkai, "asociacijos" -> asoːtsʲijatsʲɪjoːs), so the vowel
# group index from the dictionary (counted on letters) points one group too
# early. A pattern fix is unsafe (the same shape is legitimate in
# "apdorojimo", "atnaujintas"), so these are the measured exceptions:
# word -> IPA vowel group index that actually carries the accent.
IPA_GROUP_OVERRIDES: Dict[str, int] = {
    "vaikai": 2, "vaikų": 2, "taika": 2, "taikos": 2, "paieška": 2,
    "palaikai": 3, "palaikų": 3,
    "asociacijos": 2, "asociacijų": 2, "oficialų": 2, "potencialu": 4,
}

# espeak-ng's Lithuanian dictionary expands "el" to "elektroninis", because
# "el." is the common abbreviation for "el. paštas" (e-mail). That is correct
# for the abbreviation but wrong for the letter name of L, which appears in
# every spelled-out abbreviation containing it (LRT, MTL, LT). The letter form
# below matches the speaker's own phoneme inventory: espeak renders a final
# Lithuanian "l" as the syllabic l̩ used throughout the training data.
# Only this one letter needs an override; every other letter name comes out of
# espeak exactly as the training data recorded it (verified against 5121
# annotated sentences: vė vʲˈee, bė bʲˈee, em ˈem, es ˈes, e ˌea, ...).
# A trailing period is not enough to tell them apart: at the end of a sentence
# ("skambinkite į MTL.") the letter also carries one. The abbreviation is
# recognized by what follows it instead.
LETTER_IPA: Dict[str, str] = {
    "el": "ˈel̩",
    # 09-03 Roberto ausis: „VMI — VM gerai pasakė, bet I raidę turėtų tarti
    # kaip ILGĄ". Trumpas „i" trumpinio gale tiesiog nebegirdimas. LIEPA
    # anotacijoje raidės vardas buvo trumpas (ˋi, 6 kartai), bet ten jis
    # skambėjo sakinio viduryje, o ne kaip paskutinė trumpinio raidė.
    # Ilgas „iː" modeliui gerai pažįstamas iš tūkstančių žodžių.
    "i": "ˈiː",
}
ABBREVIATION_FOLLOWERS: Dict[str, Tuple[str, ...]] = {"el": ("pašt",)}


def letter_ipa(word: str, next_word: str = "") -> Optional[str]:
    """IPA for a letter name, or None when it is a genuine abbreviation."""
    w = word.lower()
    ipa = LETTER_IPA.get(w)
    if ipa is None:
        return None
    for prefix in ABBREVIATION_FOLLOWERS.get(w, ()):
        if next_word.lower().startswith(prefix):
            return None
    return ipa

_LT_LETTERS = "a-zA-Ząčęėįšųūž" \
              "ĄČĘĖĮŠŲŪŽ"
_WORD_CLEAN = re.compile(f"[^{_LT_LETTERS}0-9]")
_KEEP_PUNCT = ".,!?:;"
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?…])\s+")


def ipa_vowel_groups(ipa: str) -> List[int]:
    """Start index of every vowel group (adjacent vowels + ː form one group)."""
    groups, i = [], 0
    while i < len(ipa):
        if ipa[i] in IPA_VOWELS:
            start = i
            while i + 1 < len(ipa) and (ipa[i + 1] in IPA_VOWELS or ipa[i + 1] == LENGTH):
                i += 1
            groups.append(start)
        i += 1
    return groups


def place_accent(ipa: str, group_index: Optional[int], mark: str) -> str:
    """Remove espeak stress and put `mark` before the syllable of vowel group
    `group_index`. Syllable boundary follows Lithuanian phonotactics:
    V-CV, VC-CV; a word-initial consonant cluster belongs to the first syllable."""
    clean = "".join(c for c in ipa if c not in STRESS_MARKS)
    groups = ipa_vowel_groups(clean)
    if group_index is None or group_index >= len(groups):
        return ipa
    p = groups[group_index]
    i = p - 1
    while i >= 0 and clean[i] in CONSONANT_MODIFIERS:
        i -= 1
    if i >= 0 and clean[i] not in IPA_VOWELS and clean[i] not in " " + LENGTH:
        i -= 1                                   # one consonant
    boundary = i + 1
    j = i
    while j >= 0 and clean[j] not in IPA_VOWELS and clean[j] != " ":
        j -= 1
    if j < 0 or clean[j] == " ":                 # word start
        boundary = j + 1
    return clean[:boundary] + mark + clean[boundary:]


def load_dictionary(path: Union[str, Path]) -> Dict[str, Tuple[int, str]]:
    """word<TAB>vowel group index<TAB>mark  ->  {word: (index, mark)}"""
    entries: Dict[str, Tuple[int, str]] = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) != 3 or parts[2] not in STRESS_MARKS:
                continue
            entries[parts[0]] = (int(parts[1]), parts[2])
    return entries


class LithuanianPhonemizer:
    """espeak-ng IPA per word + dictionary pitch accent."""

    def __init__(
        self,
        dictionary_path: Union[str, Path] = DEFAULT_DICTIONARY_PATH,
        espeak_data_dir: Union[str, Path] = ESPEAK_DATA_DIR,
        expand_text: Optional[Callable[[str], str]] = None,
    ) -> None:
        """
        :param dictionary_path: stress dictionary (TSV, see load_dictionary).
        :param espeak_data_dir: espeak-ng data directory.
        :param expand_text: optional text normalizer run first (numbers,
            abbreviations); espeak-ng handles digits itself when None.
        """
        self.dictionary = load_dictionary(dictionary_path)
        self.espeak = EspeakPhonemizer(espeak_data_dir)
        self.expand_text = expand_text
        self._cache: Dict[str, str] = {}

    def _espeak_word(self, word: str) -> str:
        ipa = self._cache.get(word)
        if ipa is None:
            sentences = self.espeak.phonemize(ESPEAK_VOICE, word)
            ipa = "".join("".join(s) for s in sentences).strip()
            ipa = ipa.replace("ʂ", "s")   # Lithuanian has no retroflex s
            self._cache[word] = ipa
        return ipa

    def phonemize_word(self, word: str) -> str:
        """One word (letters only) -> IPA with the correct pitch accent."""
        ipa = self._espeak_word(word)
        entry = self.dictionary.get(word.lower())
        if entry is None:
            # Keep espeak's own stress. The in-process espeak leaves
            # monosyllables unstressed; the espeak-ng CLI (used to build the
            # training data) marks them before the vowel - do the same.
            if not any(c in STRESS_MARKS for c in ipa):
                groups = ipa_vowel_groups(ipa)
                if groups:
                    p = groups[0]
                    ipa = ipa[:p] + ACUTE + ipa[p:]
            return ipa
        group_index, mark = entry
        group_index = IPA_GROUP_OVERRIDES.get(word.lower(), group_index)
        return place_accent(ipa, group_index, mark)

    def phonemize_sentence(self, sentence: str) -> str:
        pieces: List[str] = []
        tokens = sentence.split()
        words = [_WORD_CLEAN.sub("", t) for t in tokens]
        for i, token in enumerate(tokens):
            word = words[i]
            punct = "".join(c for c in token if c in _KEEP_PUNCT)
            if not word:
                if punct and pieces:
                    pieces[-1] += punct
                continue
            override = letter_ipa(word, words[i + 1] if i + 1 < len(words) else "")
            pieces.append((override or self.phonemize_word(word)) + punct)
        return " ".join(pieces)

    def phonemize(self, text: str) -> List[List[str]]:
        """Text -> phonemes (single codepoints, NFD) grouped by sentence."""
        if self.expand_text is not None:
            text = self.expand_text(text)
        result: List[List[str]] = []
        for sentence in _SENTENCE_SPLIT.split(text.strip()):
            if not sentence:
                continue
            ipa = self.phonemize_sentence(sentence)
            if ipa:
                result.append(list(unicodedata.normalize("NFD", ipa)))
        return result
