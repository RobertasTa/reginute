# Reginutė — lietuviškas balsas Piper sintezatoriui (`lt_LT-reginute1-medium`)

![Reginutė — lietuviškas balsas Piper sintezatoriui](docs/baneris.png)

*In English: [README_EN.md](README_EN.md)*

> **Būsena.** Grandinė patikrinta gyvai: balsas kalba per gryną `piper`
> komandą, per Wyoming serverį ir per Home Assistant kolonėlę, lietuviškai,
> šalia rusiško asistento. Paketas praeina **Piperio paties katalogo patikrą**
> (`_script/voicefest.py`). Kas dar nefiksuota — galutinis mokymo pjūvis:
> modelis vis dar mokosi, ir į Hugging Face keliaus tas, kurį patvirtins ausis.
> Šis aprašas rašytas **darant**, ne po to.

Reginutė — lietuviškas balsas [Piper](https://github.com/OHF-Voice/piper1-gpl)
sintezatoriui, išmokytas iš Vilniaus universiteto **LIEPA** garsyno (diktorė
Regina Jokubauskaitė, studijos įrašai, ~3 val., CC-BY-4.0). Piper kataloge
`lt_LT` balso nebuvo niekada — latvių ir estų yra, lietuvių nėra.

Lietuvių kalba turi tris priegaides, o espeak-ng kirtį deda ne tame
skiemenyje maždaug **pusėje žodžių** (patikrinta prieš paties garsyno
anotaciją). Todėl
šis balsas sintezės metu espeak-ng **nenaudoja**: jis dirba su
`phoneme_type: text` ir savo kirčiuojančiu fonemizatoriumi
(`phonemize_lithuanian.py`) bei 189 tūkst. žodžių kirčių žodynu
(`lt_kirciai.tsv`, sudarytu iš LIEPOS anotacijų ir Arūno Smaliuko
`g2p-lt-lexicon`, abu CC-BY-4.0).

**Vadinasi balsui reikia fonemizatoriaus, kad prakalbėtų.** Grynas Piperis su
`text` tipo balsu modeliui paduoda plikas raides, ne IPA — lietuviškai jis
nekalbės. Kol `phonemize_lithuanian` nėra įlietas į piper1-gpl, šio katalogo
modulis turi stovėti prieš modelį. Abu diegimo keliai žemiau jį įtraukia.

## Kas čia guli

| Kelias | Kas tai |
|---|---|
| `phonemize_lithuanian.py` | Fonemizatorius: espeak-ng IPA po žodį → kirtis iš žodyno → trys priegaidės ženklai (`ˈ ˌ ˋ`). Parašytas Piperio `phonemize_japanese.py` pavidalu, skirtas pateikti kaip PR. |
| `lt_kirciai.tsv` | Kirčių žodynas, 189 247 žodžių formos, 3 MB. Antras stulpelis — kelinta balsių grupė kirčiuota, trečias — priegaidės ženklas. |
| `zodziai_trumpi.txt` | Trumpų žodžių sąrašas skaičių ir santrumpų plėtikliui. |
| `skaiciu_pletiklis.py` | Skaičiai, laikas, mato vienetai ir santrumpos — teisingais linksniais, prieš fonemizaciją. Be jo espeak „5000 eurų" perskaito su ne tais galūnėmis. |
| `synth_reginute.py` | Sintezės receptas: skaido ties sakinio skyryba, lygina kalbėjimo greitį gabaluose, kerpa tylą, `normalize_audio=False`. |
| `wyoming_reginute.py` | Wyoming TTS serveris aplink balsą — su juo kalbasi Home Assistant. |
| `demo_piper_wheel.py` | Įrodymas, kad užtenka išleisto `piper-tts` rato + šio modulio + `.onnx` — jokio forko. |
| `test_phonemize_lithuanian.py` | pytest rinkinys fonemizatoriui. |
| `svarus_checkpoint.py` | Mokymo pjūvis be optimizatoriaus (807 → 269 MB), kad kitas galėtų auginti savo balsą nuo šito, o ne nuo rusiško. |
| `hf/` | Tikslus paketas, keliaujantis į Hugging Face: `.onnx` (git'e nėra), `.onnx.json`, `MODEL_CARD`, `samples/`, `SHA256SUMS`. |
| `docs/` | Diegimo ir testavimo užrašai, rašyti serverio testų metu. `DU_ASISTENTAI_HA.md` — kaip viena Voice PE kolonėlė kalba dviem kalbomis su dviem žadinimo žodžiais (patikrinta gyvai). |
| `AI_CONSULTANT_BRIEF.md` | Jei ką nors klausit dirbtinio intelekto apie šitą balsą — duokit jam pirma šitą failą. Ten surašyta, ko negalima teigti (pvz. „pirmas lietuviškas TTS" — netiesa) ir kokios yra žinomos ribos. |
| `sudaryk_zodyna.py`, `patikrink_pries_mokyma.py` | Statybos įrankiai (žodyno sudarymas, mokymo atitikties patikra). Turi Windows kelius; vartotojui nereikalingi. |

## Diegimas A — grynas Piper (be Home Assistant)

Reikia išleisto `piper-tts` rato — jokio forko, jokių pataisų.

```bash
pip install piper-tts             # 1.7.x
```

Vienam katalogui reikia penkių failų: `lt_LT-reginute1-medium.onnx` ir
`.onnx.json` (iš Release arba Hugging Face), o šalia jų —
`phonemize_lithuanian.py`, `lt_kirciai.tsv` ir `skaiciu_pletiklis.py`
(kartu su `zodziai_trumpi.txt`).

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

garsas = synth.synthesize("Laba diena. Kompensacija nuo 2000 eurų.")
with wave.open("isvestis.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(synth.sr)
    w.writeframes(i_int16(garsas))
```

Tą patį vienu paleidimu daro `demo_piper_wheel.py`:

```bash
python demo_piper_wheel.py lt_LT-reginute1-medium.onnx \
    lt_LT-reginute1-medium.onnx.json "Laba diena." isvestis.wav
```

⚠️ **`normalize_audio` privalo likti `False`** (`ReginuteSynth` tai daro už
jus). Piperio numatytasis `True` šitam balsui pakelia piką iki 1,0 ir kerpa.

⚠️ **Be `skaiciu_pletiklis` skaičiai skambės blogai** — espeak-ng lietuviškus
skaitmenis skaito ne tais linksniais, o laiką kaip paprastą skaičių.
`ReginuteSynth` jį iškviečia pats, jei paduodate `expand_text=isplesk`.

## Kita grandinės pusė — ausys

Balso asistentui reikia dviejų pusių. Šis katalogas yra **burna**; **ausys** ne
mūsų, ir tai norim pasakyti garsiai.

**[`kristijonas/paprika-whisper-lt-v3`](https://huggingface.co/kristijonas/paprika-whisper-lt-v3)**,
**Kristijono Jakubsono** darbas — lietuviškas `whisper-large-v3-turbo`
pritaikymas, mokytas iš ~3 281 val. LIEPA-3 garsyno, CC-BY-4.0. Įrankiai:
**[github.com/kristijonasatpro/paprika](https://github.com/kristijonasatpro/paprika)**
(Apache-2.0).

Kodėl tai svarbu čia — pamatuota mūsų pačių stende, ne paimta ant tikėjimo:

| Lietuviška šneka → tekstas | WER |
|---|---|
| bendrasis `whisper-large-v3-turbo` | 25,95 % |
| **Paprika v3** | **7,63 %** |

⚠️ **Ta pati išlyga, kurią apie savo skaičius sako pats autorius, galioja ir
mūsiškiams:** mūsų testo aibė kilusi iš LIEPOS, t. y. **savoje srityje** šiam
modeliui. Jo kortelėje parašyta atvirai: *„nėra teisingo skaičiaus svetimai
sričiai"*. 7,63 % laikykite savos srities įrodymu, ne bendru teiginiu. Įraše,
kur neprofesionalus žmogus kalba paprastame kambaryje, bendrasis modelis
prarasdavo ištisus sakinius, o Paprika suklysdavo maždaug dviem galūnėm iš
šimto žodžių — tai anekdotas, sąžiningai taip ir pavadintas.

⚠️ **Naudokite ilgo teksto dekodavimą, ne `chunk_length_s`** — tai autoriaus
įspėjimas, ir jis teisus; mes tą gedimą atkūrėm anksčiau, nei supratom.
Atkreipkit dėmesį: `faster-whisper` (o kartu ir `wyoming-faster-whisper`, per
kurį Home Assistant paprastai jį leidžia) eina gabalų keliu. Trumpoms
komandoms tai nekenkia — jos telpa į vieną langą, — bet gabalų dekoderis
dokumentuotai prasimano tekstą ant tylos, tad ilgam įrašui verčiau jo repo
`transcribe_file.py`.

Mūsų namuose abi pusės sukasi greta kaip Wyoming tarnybos: Paprika — šneka į
tekstą, Reginutė — tekstas į šneką, lietuviškame Assist konvejeryje šalia
rusiško. Žr. `docs/DU_ASISTENTAI_HA.md`.

## Diegimas B — Home Assistant per Wyoming

Sukasi šalia jūsų esamo Piper priedo, savo porte; nieko esamo neliečia.

```bash
pip install piper-tts wyoming
python3 wyoming_reginute.py \
    --model lt_LT-reginute1-medium.onnx \
    --config lt_LT-reginute1-medium.onnx.json \
    --dictionary lt_kirciai.tsv \
    --uri tcp://0.0.0.0:10250 \
    --length-scale 1.30
```

Home Assistant: **Settings → Devices & Services → Add integration → Wyoming
Protocol**, įrašykite serverio adresą ir portą 10250. Balsas atsiras kaip
`reginute1`.

Pilnas receptas su systemd tarnyba ir LXC konteinerio parametrais —
`docs/DIEGIMAS_SERVERYJE.md`, rašytas gyvo diegimo metu.
Kaip viena kolonėlė kalba dviem kalbomis (du žadinimo žodžiai, du asistentai)
— `docs/DU_ASISTENTAI_HA.md`.

## Licencija

Autorių teisės © 2026 Robertas Tarasevičius.

Dvi licencijos, nes kataloge guli du skirtingi dalykai:

| Kas | Licencija | Failas |
|---|---|---|
| **Kodas** — fonemizatorius, plėtiklis, Wyoming serveris, įrankiai | **GPL-3.0-only** (kaip ir piper1-gpl) | `LICENSE` |
| **Balsas** — `.onnx`, `.onnx.json`, pavyzdžiai (platinami per Release / Hugging Face, git'e jų nėra) | **CC-BY-4.0** | `LICENSE-VOICE` |

Balsas CC-BY-4.0 paveldi iš LIEPOS garsyno. Kilmė atvirai pasakyta
`hf/MODEL_CARD` ir `hf/README.md`: mokytas nuo Piper katalogo pjūvio
`ru_RU-irina-medium`, kuris pats mokytas nuo `en_US-lessac-medium`.

⚠️ CC-BY-4.0 reikalauja nurodyti autorystę — žr. skyrių žemiau ir laikykite jį
kartu su balso failais, kur jie bekeliautų.

## Padėkos

CC-BY-4.0 prašo paminėti garsyną. Garsyną daro žmonės, tad čia įvardyti ir
jie. Nė vienas jų šio projekto nematė; nė viena įstaiga jo neremia. Įstaigų
ženklai baneryje puslapio viršuje sako *ačiū*, ir nieko daugiau.

### Įrašai — LIEPA (2013–2015)

Balsas išmokytas iš **LIEPOS** garsyno sintezės dalies (*LIEtuvių šneka
valdomos PAslaugos*), kurioje diktoriai įskaitė keturis balsus. Šis — vienas
iš tų keturių.

* Vykdė **Vilniaus universitetas** (Matematikos ir informatikos institutas;
  Filologijos fakultetas).
* Partneriai: **Lietuvių kalbos institutas**, **Lietuvos edukologijos
  universitetas** (nuo 2019 m. **Vytauto Didžiojo universiteto** Švietimo
  akademija), **Šiaulių universitetas** (nuo 2021 m. Vilniaus universiteto
  Šiaulių akademija).
* Vadovas — **prof. Laimutis Telksnys**, pradėjęs klausti, ar mašina gali
  kalbėtis su žmogumi, dar 1967 metais; LIEPOS pristatymai iki šiol prasideda
  ta data. Šis balsas — vėlyva išnaša prie prieš 58 metus užduoto klausimo.
* Garsyno darbai ir dokumentacija — **Gediminas Navickas** (VU MIF), kurio
  2025 m. seminaro skaidrės yra viso to, kas parašyta aukščiau, šaltinis.
* Diktorė — **Regina Jokubauskaitė**. Viskas, ką kas nors išgirs, yra jos:
  jos tembras, jos tempas, jos būdas užbaigti sakinį. Modelis tik išmoko tai
  perdėlioti.
* Į Hugging Face įkėlė **MEL DYNAMICS, MB** kaip
  [`meldynamics/liepa-tts`](https://huggingface.co/datasets/meldynamics/liepa-tts),
  CC-BY-4.0. Be to įkėlimo garsynas vis tiek egzistuotų — ir vis tiek būtų
  nepanaudojamas.

Šeima tęsėsi: **LIEPA-2** (1 000 val.) ir **LIEPA-3** (10 000 val., vadovė
**dr. Gražina Korvel**) — būtent iš LIEPA-3 išmokyta žemiau minima Paprika.
Kitas garsynas, tas pats sprendimas: paskelbti, o ne pasilikti.

### Žodynas

Kirčių žodynas sudarytas iš
[`svogunas/g2p-lt-lexicon`](https://huggingface.co/datasets/svogunas/g2p-lt-lexicon),
**Arūno Smaliuko** darbo (CC BY 4.0). Beveik kiekvienas kirčiuotas šio balso
žodis stovi ant jo darbo — 176 637 iš 189 247 įrašų.

### Ausys

**[`paprika-whisper-lt-v3`](https://huggingface.co/kristijonas/paprika-whisper-lt-v3)**,
**[Kristijono Jakubsono](https://github.com/kristijonasatpro/paprika)**
(CC-BY-4.0 / Apache-2.0). Be jo šis balsas būtų pusė sistemos: lietuviškai su
namais kalbėtis galima todėl, kad jis pirmas padarė klausymą.

### Rodyklė

**Linas Petkevičius, PhD** — AI Lietuva prezidentas ir Vilniaus universiteto
Informatikos instituto direktorius. Viešoje LinkedIn gijoje apie tai, kaip
platinami LIEPA-3 įrašai, jis parašė komentarą, išdėsčiusį, kas įkėlė duomenis
į Hugging Face ir kas jais išmokė lietuvišką modelį. Nuo to komentaro šis
projektas ir prasidėjo: be jo nebūtume radę Paprikos ir nebūtume ėję ieškoti
garsyno, iš kurio padarytas šis balsas. Jis mums nieko neskolingas ir apie mus
nieko nežinojo — kaip tik tai ir yra esmė. **Vienas tikslus viešas komentaras
gali būti vertingesnis už projekto planą.**

### Piper

**Michael Hansen** ir **Open Home Foundation** — už sintezatorių, pakankamai
mažą, kad suktųsi namų serveryje, ir pakankamai atvirą, kad trijų milijonų
žmonių kalba galėtų prisidėti savęs neprašydama leidimo.

---

Visa tai egzistuoja todėl, kad Vilniaus universitetas LIEPĄ paskelbė, o ne
pasiliko. Dešimt metų įrašų, atiduoti už citatos kainą.
