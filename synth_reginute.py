# BENDRA SINTEZĖS VIRTUVĖ Reginutei per piper-tts ratą — lygiai tas pats
# receptas, kaip kadrų `sintezuok_zinias.py` (Roberto ausis 09-03: per
# Wyoming „žiauru", per demo „skuba" — išmatuota: be pauzių tylos 11 % vietoj
# 32 %, ir piper-tts `normalize_audio=True` kėlė piką iki 1,0 / kirpo):
#   1. tekstas -> valymas (kabutės, skliaustai, daugtaškiai) -> plėtiklis;
#   2. skaidymas ties KIEKVIENU skyrybos ženklu į fragmentus;
#   3. fragmentas -> fonemos (phonemize_lithuanian) -> modelis, BE normalizacijos;
#   4. modelio uodegos tyla nukerpama (-45 dB), įdedamos MŪSŲ pauzės:
#      kablelis 0,25 s, taškas/!/? 0,45 s, dvitaškis 0,20 s, eilutė 0,15 s,
#      pabaiga 0,7 s (pauzės iš SING anotacijų matavimo 09-02).
# Naudoja demo_piper_wheel.py ir wyoming_reginute.py.
import re
import unicodedata
from dataclasses import replace
from typing import Iterable, Optional

import numpy as np
from piper import PiperVoice, SynthesisConfig

_KABUTES = re.compile(r'[„“”"«»]')
# 09-03 vakare (Roberto ausis, 2 ratai): (1) „Labas" ištemptas — vieno žodžio
# gabalus VITS tempia (0,72 s), todėl ties kableliu skaidom TIK kai abi pusės
# turi bent MIN_ZODZIU žodžių; trumpos dalys lieka su kableliu viduje (modelis
# kablelį turi žemėlapyje ir jo pauzę išmoko iš gyvos Reginos). (2) Visai
# nebeskaidant ties kableliu „visas tekstas pagreitėjo" — pauzė 0,25 s
# grąžinta ten, kur skaidom. Brūkšnelis = santrumpos šonai (0,10 s).
_ZENKLAI = re.compile(r"([.,!?:;–-])")
_ZENKLAI_BE_KABLELIO = re.compile(r"([.!?:;–-])")
SILPNI = ","            # skaidom tik jei abi pusės pakankamai ilgos
MIN_ZODZIU = 0          # 0 = skaidyti ties kiekvienu kableliu (kaip kadruose):
                        # 09-03 pamatuota, kad jungiant tekstas pagreitėja
                        # 159 -> 178 žodžių/min (gyva Regina kalba 149)
TRUMPAS = 20            # fonemų ženklų: žemiau šios ribos modelis tempia
ILGAS = 30              # nuo šios ribos gabalo greitis laikomas etalonu
TIKSLINIS_MS = 41.0     # ms vienai fonemai (išmatuota e6188 ilguose gabaluose)

# ⭐⭐ 09-03 VĖLAI — „KALBA BANGOM" (Roberto ausis). Pamatuota to paties teksto
# gabaluose: trumpi sakiniai eina 50 ms/fonemą, ilgi 38. Skirtumas trečdalis,
# ir kryptis PRIEŠINGA žmogui — žmogus trumpą frazę meta greičiau, o modelis
# ją tęsia. Tai ir girdima kaip bangavimas.
# Sprendimas: KIEKVIENAS gabalas persintezuojamas (iki 2 kartų), kol pataiko
# į vieną greitį. Po to svyravimas 38–50 -> 45–51 ms/fonemą.
# Tikslas siejamas su tempu, kad `length_scale` liktų prasmingas vairas:
# Roberto priimta nuostata buvo 1,30 -> 48 ms/fonemą.
MS_UZ_TEMPO_VIENETA = 36.9
LYGINIMO_PAKLAIDA = 0.06    # arčiau nei 6 % — nebetaisom
LYGINIMO_BANDYMAI = 2

# ⭐⭐⭐ 09-04 (Roberto ausis: „2 tyliai, 16 greit, 6 kliūva") — TIKSLAS BUVO
# VIENAS VISIEMS, o turi būti du. Pamatuota TIKROS Reginos 5121 įraše
# (`kaip_taria_regina.py`), ms vienai fonemai:
#     ilgi (30+ fonemų)  37,8 · vidutiniai (15–29) 46,3 · trumpi (<15) 63,6
# Ji trumpą gabalą taria 68 % LĖČIAU už ilgą. ⚠️ 09-03 komentaras aukščiau
# teigia priešingai („žmogus trumpą frazę meta greičiau") — ta prielaida buvo
# iš galvos, o ne iš duomenų, ir šitiems duomenims ji NETEISINGA.
# Dabartinis 36,9 × 1,25 = 46,1 sutampa su VIDUTINIŲ etalonu (46,3) iki
# dešimtosios — tad jis buvo teisingas, tik taikomas ir trumpiems. Iš to:
# „du" gaudavo 47,4 ms (0,75× jos), „šeši" 54,9 (0,86×), o `length_scale`
# atsimušdavo į apatinę ribą 0,60. Todėl ir „tyliai" — per tiek laiko balsas
# nespėja išsiskleisti.
# ⛔ Lyginimo IŠJUNGTI negalima: be jo (grynas ls=1,25) „šeši" eina 1,80×
# lėčiau už ją, nes modelis trumpų gabalų beveik nematė (93 prieš 4963).
# Vidutinių ir ilgų NELIEČIAM — jie patikrinti Roberto ausimi (trijų ausų
# testas 09-03). Keičiasi TIK trumpieji.
TRUMPI_FON = 15             # fonemų: žemiau šios ribos galioja kitas tikslas
MS_TRUMPIEMS_UZ_VIENETA = 50.9
# ⚠️ 50,9 gautas dalijant tikros Reginos 63,6 iš 1,25 — TUO METU toks buvo
# numatytasis `length_scale`. Nuo 09-04 numatytasis suvienodintas su tarnyba
# (1,30; anksčiau .onnx.json sakė 1,25, o tarnyba dirbo su 1,30, tad Robertas
# vertino vieną tempą, o svetimas gautų kitą). Vadinasi tikrasis tikslas
# trumpiems dabar yra 50,9 × 1,30 = 66,2 ms, o ne 63,6.
# ⛔ Konstantos NEPERSKAIČIUOJU į 48,9: būtent 66,2 ms rezultatą Robertas
# išklausė per kolonėlę ir patvirtino („visur kitur gerai išilgėjo, viskas
# normoj"). Skaičius, kurį patvirtino ausis, nekeičiamas dėl gražesnės
# aritmetikos.

# ⭐ 09-03 PAMATUOTA IR ATMESTA: raidines santrumpas buvau iškėlęs į atskirus
# gabalus su pauzėmis ir lėtinimu. `trumpiniu_matavimas.py` (Paprika klauso
# 24 failų) parodė, kad tai KENKIA:
#     raidės sakinio viduje (kaip mokyme) 8/11   <- paliekam
#     pauzės tarp raidžių                 6/11
#     lėčiau + pauzės                     7/11
# Lėtinimas be pauzių nekeičia nieko (8/11), tad ir jo nebelieka. Raidės eina
# paprastais žodžiais sakinio viduje — lygiai taip, kaip jas įrašė Regina.
SANTRUMPOS_LETUMAS = 1.0


def valyk_teksta(t: str) -> str:
    t = _KABUTES.sub(" ", t)
    t = re.sub(r"\(\s*\.\.\.\s*\)", " ", t)
    t = re.sub(r"[()\[\]]", " ", t)
    t = t.replace("…", ".")
    t = re.sub(r"\.{2,}", ".", t)
    t = re.sub(r"([.,:;!?])\s*(?=[.,:;!?])", "", t)
    t = re.sub(r"[ \t]+", " ", t)
    return t


def nukirpk_tyla(a: np.ndarray, sr: int, slenkstis_db: float = -45.0,
                 pradzios_db: float = -70.0, pradzios_atsarga: int = 3) -> np.ndarray:
    """Nukerpa gabalo tylą. ⭐ 09-03: PRIEKIUI slenkstis ŽEMESNIS.

    Robertas perklausė Reginutę dviem atpažintuvais ir abu iš „Rašykite"
    padarė „Ašykite". Priežastis pamatuota: modelis kiekvieną gabalą pradeda
    120–200 ms beveik tylos, o po to garsas KYLA palaipsniui — „R" pradžia
    eina per −83, −76, −73, −71, −65, −58 dB. Kirpimas ties −45 dB tą kilimą
    nurėždavo, ir pirmasis priebalsis dingdavo. Todėl priekiui imam −70 dB su
    3 langų (30 ms) atsarga, o galui paliekam −45 dB (uodegos tyla nereikalinga).
    """
    lango = int(sr * 0.01)
    n = len(a) // lango
    if n == 0:
        return a
    rms = 20 * np.log10(np.sqrt(np.mean(a[:n * lango].reshape(n, lango) ** 2, axis=1)) + 1e-12)
    garsus = np.where(rms > slenkstis_db)[0]
    if len(garsus) == 0:
        return a
    tylus = np.where(rms > pradzios_db)[0]
    if not len(tylus):
        tylus = garsus
    pradzia = max(0, tylus[0] - pradzios_atsarga)
    # ⛔ 09-03 IŠBANDYTA IR ATMESTA: tą patį žemą slenkstį buvau pritaikęs ir
    # GALUI (nes atpažintuvas girdėjo „trisdesim", „kieną"). Matavimas
    # pablogėjo 9/11 -> 7/11, MTL virto „jiem tėl", o Roberto ausis patvirtino,
    # kad „kieme" ir „trisdešimt" garse buvo GERAI — klydo atpažintuvas, ne
    # sintezė. Gale lieka −45 dB: ten tikrai tik uodegos tyla.
    return a[pradzia * lango: min(n, garsus[-1] + 2) * lango]


class ReginuteSynth:
    def __init__(self, voice: PiperVoice, phonemizer, length_scale: float = 1.30,
                 kablelis: float = 0.25, taskas: float = 0.45,
                 expand_text=None, min_zodziu: int = MIN_ZODZIU,
                 santrumpu_letumas: float = SANTRUMPOS_LETUMAS,
                 kableli_skaidyti: bool = False, lyginti_greiti: bool = True) -> None:
        # ⭐ 09-03 vėlai (Roberto sprendimas po palyginimo): MODELIO RITMAS.
        # Su mūsų pauzėmis tas pats tekstas truko 22,6 s, be jų 7,9 s — tris
        # kartus trumpiau. Didžiąją dalį laiko valgė ne kalba, o mūsų 0,45 s
        # po taško ir 0,25 s po kablelio. Kablelį nuo šiol tvarko PATS MODELIS
        # (jis jį turi fonemų žemėlapyje ir išmoko iš gyvos Reginos), o mes
        # dedam tik tai, ko modelis padaryti negali: pauzeles tarp trumpinio
        # raidžių ir trumpą tarpą tarp sakinių.
        self.voice = voice
        self.kableli_skaidyti = kableli_skaidyti
        self.min_zodziu = min_zodziu
        self.santrumpu_letumas = santrumpu_letumas
        self.length_scale = length_scale
        self.lyginti_greiti = lyginti_greiti
        self.tikslinis_ms = (MS_UZ_TEMPO_VIENETA * length_scale
                             if lyginti_greiti else TIKSLINIS_MS)
        self._etalonas = []
        self.phonemizer = phonemizer
        self.expand_text = expand_text
        self.sr = voice.config.sample_rate
        self.syn = SynthesisConfig(length_scale=length_scale, noise_scale=0.667,
                                   noise_w_scale=0.8, normalize_audio=False)
        self.pauze = {".": taskas, "!": taskas, "?": taskas, ":": 0.20, ";": 0.20,
                      ",": kablelis, "–": kablelis,
                      # brūkšnelis = pauzelė tarp trumpinio raidžių (Roberto
                      # ausis 09-03: „su mažom pauzelėm gaunasi geriau")
                      "-": 0.10}
        self.kablelis = kablelis
        self.zurnalas = []   # (fragmentas, trukmė s, RMS dB) — matavimams

    def _tyla(self, s: float) -> np.ndarray:
        return np.zeros(int(self.sr * s), dtype=np.float32)

    def _sintezuok(self, fonemos, length_scale: float) -> np.ndarray:
        ids = self.voice.phonemes_to_ids(fonemos)
        syn = replace(self.syn, length_scale=length_scale)
        a = self.voice.phoneme_ids_to_audio(ids, syn)
        if isinstance(a, tuple):
            a = a[0]
        return nukirpk_tyla(np.asarray(a, dtype=np.float32), self.sr)

    def _fragmentas(self, frag: str, santrumpa: bool = False) -> Optional[np.ndarray]:
        ipa = self.phonemizer.phonemize_sentence(frag)
        if not ipa:
            return None
        fonemos = list(unicodedata.normalize("NFD", ipa))
        if santrumpa:
            # 09-03 Roberto ausis: „VMI ir MTL sunkiai pavyko, bandžiau
            # atspėti". SANTRUMPOS NEGALIMA GREITINTI — ji trumpa (13 ženklų),
            # tad greičio korekcija žemiau ją laikė „ištemptu" gabalu ir
            # spausdavo iki 0,64 s trims raidėms. Raidė nėra žodis: jos
            # nespėji atspėti iš konteksto, todėl ji turi būti LĖTESNĖ už
            # kalbą, ne greitesnė. Korekcija praleidžiama, tempas +15 %.
            a = self._sintezuok(fonemos, self.length_scale * self.santrumpu_letumas)
            if len(a):
                self.zurnalas.append((frag, len(a) / self.sr, 0.0))
            return a
        # ⭐ Greičio išlyginimas: taikom VISIEMS gabalams, kad dingtų bangavimas
        ls = self.length_scale
        a = self._sintezuok(fonemos, ls)
        if self.lyginti_greiti:
            # 09-04: trumpam gabalui — savas tikslas (žr. MS_TRUMPIEMS_UZ_VIENETA)
            tikslas = (MS_TRUMPIEMS_UZ_VIENETA * self.length_scale
                       if len(fonemos) < TRUMPI_FON else self.tikslinis_ms)
            for _ in range(LYGINIMO_BANDYMAI):
                ms = 1000 * len(a) / self.sr / len(fonemos)
                if abs(ms - tikslas) < tikslas * LYGINIMO_PAKLAIDA:
                    break
                ls = max(0.6, min(2.0, ls * tikslas / ms))
                a = self._sintezuok(fonemos, ls)
            if len(a):
                self.zurnalas.append((frag, len(a) / self.sr,
                                      20 * float(np.log10(np.sqrt(np.mean(a ** 2)) + 1e-12))))
            return a

        # 09-03 Roberto ausis: „Labas taip ilgai sakė, vos ne skiemenavimas".
        # IŠMATUOTA (e6188): ilgi gabalai nusistovi ties ~41 ms vienai fonemai,
        # o trumpi tempiami: „Labas" 100 ms, „e es" 87, „Sveiki" 66. Priežastis
        # — mokymo įvestis buvo 47 ženklų mediana (5 % trumpesnių nei 34), tad
        # 7 ženklų gabalas modeliui yra už patirties ribų ir trukmės numatytojas
        # jam duoda per daug laiko. Taisom TIEK, kiek trūksta: persintezuojam
        # su proporcingai mažesniu length_scale (vienas papildomas ėjimas,
        # RTF 0,03 — nieko nekainuoja). Riba 0,6, kad kalba nesugniužtų.
        if len(a) and len(fonemos) < TRUMPAS:
            greitis = 1000 * len(a) / self.sr / len(fonemos)      # ms fonemai
            if greitis > self.tikslinis_ms * 1.15:
                ls = max(self.length_scale * 0.6,
                         self.length_scale * self.tikslinis_ms / greitis)
                a = self._sintezuok(fonemos, ls)
        elif len(fonemos) >= ILGAS and len(a):
            # ilgų gabalų greitis = šio teksto etalonas (slenkantis vidurkis)
            self._etalonas = (self._etalonas +
                              [1000 * len(a) / self.sr / len(fonemos)])[-5:]
            self.tikslinis_ms = float(np.median(self._etalonas))

        if len(a):
            self.zurnalas.append((frag, len(a) / self.sr,
                                  20 * float(np.log10(np.sqrt(np.mean(a ** 2)) + 1e-12))))
        return a

    def fragmentai(self, eil: str):
        """Eilutė -> [(tekstas, skyrybos ženklas po jo)], kableliai sujungti,
        kai bet kuri pusė trumpesnė nei min_zodziu žodžių (0 = skaidyti visada,
        kaip kadrų sintezuok_zinias)."""
        MIN_ZODZIU = self.min_zodziu
        dalys = (_ZENKLAI if self.kableli_skaidyti else _ZENKLAI_BE_KABLELIO).split(eil)
        poros = []
        for i in range(0, len(dalys), 2):
            frag = dalys[i].strip()
            zenklas = dalys[i + 1] if i + 1 < len(dalys) else ""
            if frag or zenklas:
                poros.append((frag, zenklas))
        out, cur = [], ""
        for k, (frag, zenklas) in enumerate(poros):
            cur = (cur + " " + frag).strip()
            if zenklas in SILPNI and zenklas:
                kitas = poros[k + 1][0] if k + 1 < len(poros) else ""
                if len(cur.split()) >= MIN_ZODZIU and len(kitas.split()) >= MIN_ZODZIU:
                    out.append((cur, zenklas))
                    cur = ""
                else:
                    cur += zenklas          # kablelis lieka modeliui
            else:
                out.append((cur, zenklas))
                cur = ""
        if cur:
            out.append((cur, ""))
        return out

    def _balso_lygis(self, a: np.ndarray) -> float:
        """Įgarsintų 10 ms kadrų RMS mediana, dB (tyla neskaičiuojama)."""
        lango = int(self.sr * 0.01)
        n = len(a) // lango
        if n == 0:
            return -99.0
        rms = 20 * np.log10(np.sqrt(np.mean(a[:n * lango].reshape(n, lango) ** 2, axis=1)) + 1e-12)
        garsus = rms[rms > -45]
        return float(np.median(garsus)) if len(garsus) else -99.0

    @staticmethod
    def _pikas_db(a: np.ndarray) -> float:
        return float(20 * np.log10(np.abs(a).max() + 1e-12))

    def _islygink_santrumpa(self, a: np.ndarray, zodziu_pikai) -> np.ndarray:
        """09-03 Roberto ausis: „trumpiniai nutyla, sunkiai įklausomi".
        Išmatuota: raidžių gabalų VIDURKIS toks pat kaip žodžių (−18 dB), bet
        PIKAI 2–4 dB žemesni (−6…−8 prieš −3…−4) — raidės tariamos plokščiau,
        o ausis girdi pikus. Keliam santrumpos piką iki gretimų ŽODŽIŲ gabalų
        pikų medianos, ne daugiau +4 dB, pikas ne aukščiau −1 dB."""
        if not zodziu_pikai:
            return a
        skirtumas = float(np.median(zodziu_pikai)) - self._pikas_db(a)
        if skirtumas <= 0.3:
            return a
        gain = 10 ** (min(skirtumas, 4.0) / 20)
        pikas = float(np.abs(a).max()) or 1.0
        gain = min(gain, 0.89 / pikas)
        return (a * gain).astype(np.float32)

    def gabalai(self, tekstas: str) -> Iterable[np.ndarray]:
        """Garso gabalai eilės tvarka (kalba ir pauzės) — srautui."""
        t = valyk_teksta(tekstas)
        if self.expand_text is not None:
            t = self.expand_text(t)
        zodziu_pikai = []           # žodžių gabalų pikai, dB (paskutiniai 6)
        for eil in t.splitlines():
            poros = self.fragmentai(eil)
            for i, (frag, zenklas) in enumerate(poros):
                pries = poros[i - 1][1] if i > 0 else ""
                santrumpa = (pries == "-" or zenklas == "-")
                if frag:
                    a = self._fragmentas(frag, santrumpa=santrumpa)
                    if a is not None and len(a):
                        if santrumpa:
                            a = self._islygink_santrumpa(a, zodziu_pikai)
                        else:
                            zodziu_pikai = (zodziu_pikai + [self._pikas_db(a)])[-6:]
                        yield a
                if zenklas:
                    yield self._tyla(self.pauze.get(zenklas, self.kablelis))
            yield self._tyla(0.15)
        yield self._tyla(0.7)

    def synthesize(self, tekstas: str) -> np.ndarray:
        return np.concatenate(list(self.gabalai(tekstas)) or [self._tyla(0.1)])


def i_int16(a: np.ndarray) -> bytes:
    return (np.clip(a, -1.0, 1.0) * 32767).astype(np.int16).tobytes()
