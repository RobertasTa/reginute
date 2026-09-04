# Reginutės diegimas į savo serverį (Home Assistant + Wyoming)

> Rašoma **darant**, ant Roberto serverio (Proxmox, LXC 214), 2026-09-04→.
> Kiekvienas žingsnis įrašomas tą pačią minutę, kai padarytas, su tuo, kas
> nesuveikė. Kol prie žingsnio ⏳ — jis dar nepatikrintas šiame pakete.
> Kai viskas suveiks vieną kartą nuo pradžios iki galo — bus ir angliška versija.

## 0. Prieš pradedant

- ⚠️ Roberto namuose: pirma PASAI (`\\NAS-Rtrob\Namu_Serv\. . PASAI\`).
- Nauja tarnyba eina **šalia** veikiančių, niekada per jas. Esamas
  `wyoming-piper` (portas 10200) ir Silero/xenia TTS **neliečiami**.
- Reikia: LXC su Python 3.11+, tinklas iki HA, ~200 MB vietos.

## 1. Paketo įkėlimas ⏳

Paketas = `hf/` katalogas iš šio repo + modulis. Į serverį keliauja TIK jis,
ne pavieniai failai iš darbinių katalogų. Prieš kėlimą — `SHA256SUMS` sutampa.

```
/opt/reginute/
├── lt_LT-reginute1-medium.onnx
├── lt_LT-reginute1-medium.onnx.json
├── phonemize_lithuanian.py
├── lt_kirciai.tsv
├── zodziai_trumpi.txt
├── synth_reginute.py
├── wyoming_reginute.py
└── venv/            (piper-tts, wyoming)
```

## 2. Aplinka ⏳

```bash
python3 -m venv /opt/reginute/venv
/opt/reginute/venv/bin/pip install piper-tts wyoming
```

## 3. Tarnyba (systemd) — tikras failas iš LXC 214 (09-04)

`/etc/systemd/system/wyoming-reginute.service`, portas **10250** (esamas
`wyoming-piper` lieka ant 10200):

```ini
[Unit]
Description=Wyoming Reginute (lietuviskas Piper balsas)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=/opt/reginute
Environment=PYTHONPATH=/opt/reginute
Environment=OMP_NUM_THREADS=2
ExecStart=/opt/reginute/venv/bin/python3 /opt/reginute/wyoming_reginute.py \
  --model /opt/reginute/lt_LT-reginute1-medium.onnx \
  --config /opt/reginute/lt_LT-reginute1-medium.onnx.json \
  --dictionary /opt/reginute/lt_kirciai.tsv \
  --uri tcp://0.0.0.0:10250 \
  --length-scale 1.30
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Konteineris: unprivileged, 2 branduoliai, 1 GB RAM (balsas ima ~330 MB),
4 GB diskas. `OMP_NUM_THREADS=2` — kad nesigrumtų su kitais LXC.

⚠️ **Atviras klausimas:** tarnyba tempą ima iš `--length-scale 1.30` (Roberto
ausis serveriui 09-03), o paketo `.onnx.json` sako 1.25 (kadrų receptas).
Vieną iš jų fiksuoti kopetėlių testu prieš HF (PIPER plano 9.1).
Balso vardas paliktas `reginute1` — HA asistentė „Reginutė" jį jau naudoja;
pervadinimas atjungtų TTS.

Diegimas iš paketo vienu skriptu: `bash diegk_i_serveri.sh` (keičia tik
`--model`/`--config` eilutes, senų failų netrina, SHA256 tikrina konteineryje).

## 4. Prijungimas prie Home Assistant ✅ (09-04, HA Core 2026.9.0, HAOS)

**4.1 Wyoming tarnyba:** Настройки → Устройства и службы → Wyoming Protocol →
„Добавить службу" → `192.168.0.220 : 10250` → sąraše atsiranda TTS `reginute`.

**4.2 Asistentė:** Настройки → Голосовые ассистенты → „Добавить ассистента":
Название `Reginutė`, Язык литовский; Диалоговая система `Home Assistant`
(komandoms — vykdo tiesiai, be LLM; laisvam pokalbiui vėliau — Gemma);
Распознавание речи `Paprika LT` (10302); Синтез речи `reginute`, Голос
`Reginutė (medium, 22050…)`. Esamos rusiškos asistentės NELIEČIAMOS.

**4.3 Antras žadinimo žodis kolonėlei (HA 2025.10+ funkcija: iki dviejų
žodžių ir dviejų asistentų per palydovą; Voice PE turi `hey_jarvis` pačiame
įrenginyje, fw 26.6.0):** Настройки → Голосовые ассистенты → apačioje
„N устройства Assist" → kolonėlė (**tik SVETAINE**, MIEGAMAS nepaliesta) →
kortelė **„Настройки"** — laukai, kaip HA ESPHome kodas juos vadina:

| Laukas | Reikšmė | Liesti? |
|---|---|---|
| Ассистент | Home Assistant (rusiška) | ne |
| Фраза активации | Okay Nabu | ne |
| **Assistant 2** | **Reginutė** | ✅ pakeista |
| **Wake word 2** | **Hey Jarvis** | ✅ pakeista |
| Wake word sensitivity | Moderately sensitive | ne |

Įsigalioja iš karto, kolonėlės perkrauti nereikia. ⇒ „Okay Nabu" = rusiškas
kelias kaip buvo; „Hey Jarvis" = Paprika → HA lt intentai → Reginutė.

⚠️ Kodėl NE trigeris sakinyje („Ok Nabu, Регина, įjunk…"): kolonėlė visą
sakinį atiduoda ausims VIENU gabalu, viena kalba — rusiškas Whisper
lietuvišką dalį užrašytų nesąmonėmis. Kalbą renka žadinimo žodis, ne žodis
sakinyje. (Alternatyva be antro žodžio — dviem įkvėpimais per automatizaciją,
kuri perjungia „Ассистент" lauką; nepanaudota, nes antras žodis paprastesnis.)

## 5. Egzaminas — trys keliai, tie patys sakiniai

| Kelias | Ką tikrina | Sakiniai | Rezultatas |
|---|---|---|---|
| A. Grynas Piper (`demo_piper_wheel.py`) | ką gaus žmogus be HA | trijų ausų 4 + žinios | ✅ 09-04 vietoje (Windows, `pw_venv`, piper-tts 1.7.0): e6980, 4 sakiniai po 4,0–5,0 s, RMS −18 dB visi; žinios 34,2 s, pikas −3,4 dBFS, **kirpimo nėra** (0 pavyzdžių ties pilna skale). 👂 Roberto ausis — laukia. ⏳ tas pats ant serverio |
| B. Wyoming (`testas_wyoming_klientas.py`) | ką gaus HA vartotojas | tie patys | ✅ 09-04 09:27, LXC 214 iš paketo (`diegk_i_serveri.sh`): Info grąžina `reginute1` (lt/lt_LT/lt-LT); 4 sakiniai 20,3 s, pikas −2,9 dBFS; žinios 31,7 s, pikas −3,5 dBFS; **kirpimo nėra**, tyla ~25 %. 👂 Roberto ausis — laukia (Telegrame šalia A) |
| C. Balsu per kolonėlę | visa grandinė: ausys + smegenys + burna | laisvai | ✅ **09-04 ~10:00 — PIRMĄ KARTĄ BALSU.** Robertas svetainės Voice PE: „Hey Jarvis, įjunk šviesą vonioje" → lempa įsijungė, Reginutė atsakė lietuviškai „šviesos įjungtos"; išjungimas — „šviesos išjungtos". Paprika Roberto tarimą užrašė teisingai (be nosinių taisymo). Modelis e6980 (dar ne galutinis — sukeičiamas tuo pačiu `diegk_i_serveri.sh`). |

Papildomai (09-04): ✅ `ˋ` U+02CB → id 166, `̩` U+0329 → id 144; sakinys
„…savu noru, ne viską" fonemizuojasi su `ˋ`, po NFD ženklas lieka, visi
simboliai žemėlapyje. ✅ SHA256 sutampa paketas ↔ konteineris (tikrinta
`sha256sum -c` konteineryje prieš perjungiant tarnybą).
ℹ️ A ir B trukmės skiriasi (21,1 s / 20,3 s; žinios 34,2 / 31,7 s) dėl
skirtingų pauzių nustatymų (demo: `min_zodziu=0` skaido ties kableliu;
serveris: `--taskas 0.15`, kablelio neskaido) ir tempo 1,25/1,30 — tas pats
atviras klausimas, kaip 3 skyriuje; vieną receptą fiksuoti prieš HF.

## 6. Kas nesuveikė ir kaip pataisyta

(pildoma darant)
