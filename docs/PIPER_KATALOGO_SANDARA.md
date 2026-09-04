# Piper balsų katalogo sandara — IŠMATUOTA, ne perpasakota

> Surinkta 2026-09-04 tiesiai iš `rhasspy/piper-voices` per HF API
> (3292 failai, 175 balsai, 35 kalbos). Kad nereikėtų kasti iš naujo ir
> kad prieš pateikimą būtų su kuo palyginti.
>
> ⚠️ Šis failas yra **matavimų santrauka**. Kai kas nors keisis Piperio
> pusėje — permatuoti, ne spėti.

## 1. Ką turi balsas OFICIALIAME kataloge

Kelias: `<kalba>/<kalba_ŠALIS>/<vardas>/<kokybė>/`

Tikri pavyzdžiai (visi failai, be išimčių):

```
lv/lv_LV/aivars/medium/          it/it_IT/serena/medium/       et/et_EE/news/medium/
├── MODEL_CARD                   ├── MODEL_CARD                ├── MODEL_CARD
├── lv_LV-aivars-medium.onnx     ├── it_IT-serena-medium.onnx  ├── et_EE-news-medium.onnx
├── lv_LV-aivars-medium.onnx.json│   …-medium.onnx.json        │   …-medium.onnx.json
└── samples/speaker_0.mp3        └── samples/speaker_0.mp3     └── samples/speaker_0…3.mp3
```

⇒ **KETURI daiktai, ne daugiau:** `MODEL_CARD`, `.onnx`, `.onnx.json`,
`samples/speaker_N.mp3` (po vieną kiekvienam kalbėtojui).
**README.md kataloge NĖRA** — kortelė vadinasi `MODEL_CARD` ir yra grynas
tekstas.

Papildomai: **`ALIASES`** turi 50 balsų iš 175 — tai seni pavadinimai
(pervadintiems balsams). Naujam balsui nereikia.

**Mūsų atitikmuo:** `lt/lt_LT/reginute1/medium/` su
`lt_LT-reginute1-medium.onnx` + `.onnx.json` + `MODEL_CARD` + `samples/`.

## 2. Ką turi ASMENINIS repo (iš kurio Hansenas persikelia)

`committa/it_IT-serena-medium` — balsas, priimtas per 3 dienas:

```
.gitattributes
README.md                       ← model card SU YAML antrašte (licencija!)
it_IT-serena-medium.onnx
it_IT-serena-medium.onnx.json
samples/speaker_0.mp3
```

Jo HF žymės (iš `tags`): `piper`, `onnx`, `text-to-speech`, `tts`, `italian`,
`it`, `dataset:committa/serena-synthetic-it-28h`, `license:cc-by-4.0`.
Visos jos ateina **iš README antraštės**, ne iš atskiro failo.

⚠️ **MŪSŲ REPO TURI TURĖTI DAUGIAU.** Serena kalba per espeak, tad jai užtenka
dviejų failų. Reginutė be `phonemize_lithuanian.py` + `lt_kirciai.tsv`
**netaria nieko** (`phoneme_type: text` ⇒ modelis gauna raides, ne IPA).
Todėl mūsų repo šalia balso turi vežti ir juos, ir tai pasakyti README
pirmame trečdalyje.

## 3. `voices.json` — ką Hansenas sugeneruoja PATS

175 įrašai; vieno pavidalas (`lv_LV-aivars-medium`):

```json
{
  "key": "lv_LV-aivars-medium",
  "name": "aivars",
  "language": {"code": "lv_LV", "family": "lv", "region": "LV",
               "name_native": "Latviešu", "name_english": "Latvian",
               "country_english": "Latvia"},
  "quality": "medium",
  "num_speakers": 1,
  "speaker_id_map": {},
  "files": {"<kelias>": {"size_bytes": 63511038, "md5_digest": "5b48c6…"}},
  "aliases": []
}
```

⚠️⚠️ **MD5, ne SHA256.** Mūsų `SHA256SUMS` yra MŪSŲ vidaus reikalas (paketas ↔
serveris). Katalogui reikia MD5, bet jį skaičiuoja `voicefest.py`, ne mes.

**Mūsų failų MD5 (e7098 pjūvis, 09-04):**

| Failas | Dydis | MD5 |
|---|---|---|
| `lt_LT-reginute1-medium.onnx` | 63 516 051 | `37968da042d6d8bd1d2f355fa670dc01` |
| `lt_LT-reginute1-medium.onnx.json` | 5 801 | `a74db63d011158c55e9f4cab5b29a3d6` |
| `MODEL_CARD` | 1 815 | `26dfec8be951897c20030ad8dd2735b7` |

(Pjūvį keisim po aklo testo — tada permatuoti.)

## 4. `.onnx.json` laukai — MŪSŲ SUTAMPA SU KATALOGU

Palyginta su `lv_LV-aivars-medium.onnx.json` (kaimynas latvis):

```
aivars: audio dataset espeak inference language num_speakers num_symbols
        phoneme_id_map phoneme_map phoneme_type piper_version speaker_id_map
mūsų:   TAS PATS SĄRAŠAS — trūkstamų 0, perteklinių 0
```

Skiriasi tik turinys, ir sąmoningai:

| Laukas | aivars | mūsų | kodėl |
|---|---|---|---|
| `espeak.voice` | `lv` | `lt` | kalba (mums informacinis — espeak sintezėje nenaudojamas) |
| `phoneme_type` | `espeak` | **`text`** | mūsų fonemizatorius, 167 simboliai su priegaidėmis |
| `inference.length_scale` | `1` | **`1.25`** | ⚠️ ATVIRA: serveryje 1.30, kadruose 1.25; fiksuoti kopetėlių testu prieš pateikimą |

## 5. `voicefest.py` — kur jis iš tikrųjų

⚠️ **`_script/voicefest.py`, pačiame `piper-voices` repo** (šalia
`_script/voice_names.sh` ir `_script/old_names.txt`).
Buvau įrašęs klausimą Hansenui „kur jis gyvena" — **nuimtas**, nes atsakymas
gulėjo repo failų sąraše.
⇒ **PAMOKA: prieš klausiant žmogaus — peržiūrėti VISĄ repo failų sąrašą**
(`GET https://huggingface.co/api/models/<repo>` → `siblings`).
📌 Parsisiųsti 09-04 neleido HF ribojimas (HTTP 429). **LIKO: parsisiųsti ir
PALEISTI ant mūsų paketo prieš pateikimą.**

## 6. Kalbos: 35, lietuvių nėra

README antraštėje išvardytos: `ar ca cs cy da de el en es fa fi fr hu is it ka
kk lb lv ne nl no pl pt ro ru sk sl sr sv sw tr uk vi zh` — **35, be `lt`**.
`lt/` katalogo taip pat nėra.
⇒ Reginutė būtų ne šiaip naujas įrašas, o **nauja eilutė kalbų sąraše**.
(Įdomu: `eu` — baskų — failuose YRA, o sąraše nėra; sąrašas atsilieka.)

## 7. Ko iš to seka mūsų paketui

| Reikia | Turim | Pastaba |
|---|---|---|
| `MODEL_CARD` | ✅ | Hanseno formatu, su gimine ir atribucija |
| `.onnx` + `.onnx.json` | ✅ | laukai sutampa su kaimynu |
| `samples/speaker_0.mp3` | ✅ | trijų ausų 4 sakiniai |
| `README.md` su YAML antrašte | ✅ | tik MŪSŲ repo; kataloge jo nereikia |
| fonemizatorius + žodynas repo šalia balso | ✅ | be jų balsas netaria |
| `voicefest.py` paleistas | ⏳ | HF ribojimas, bandyti vėliau |
| `length_scale` galutinis | ⏳ | 1.25 vs 1.30 — kopetėlių testas |
