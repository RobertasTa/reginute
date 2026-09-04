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
├── lt_LT-reginute-medium.onnx
├── lt_LT-reginute-medium.onnx.json
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
  --model /opt/reginute/lt_LT-reginute-medium.onnx \
  --config /opt/reginute/lt_LT-reginute-medium.onnx.json \
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

## 4. Prijungimas prie Home Assistant ⏳

Настройки → Устройства и службы → Wyoming → host:10250 → balsas atsiranda
kaip `reginute`. Asistentėje „Reginutė": STT = Paprika (10302), TTS = ši.

## 5. Egzaminas — trys keliai, tie patys sakiniai

| Kelias | Ką tikrina | Sakiniai | Rezultatas |
|---|---|---|---|
| A. Grynas Piper (`demo_piper_wheel.py`) | ką gaus žmogus be HA | trijų ausų 4 + žinios | ✅ 09-04 vietoje (Windows, `pw_venv`, piper-tts 1.7.0): e6980, 4 sakiniai po 4,0–5,0 s, RMS −18 dB visi; žinios 34,2 s, pikas −3,4 dBFS, **kirpimo nėra** (0 pavyzdžių ties pilna skale). 👂 Roberto ausis — laukia. ⏳ tas pats ant serverio |
| B. Wyoming (`testas_wyoming_klientas.py`) | ką gaus HA vartotojas | tie patys | ⏳ |
| C. Balsu per kolonėlę | visa grandinė: ausys + smegenys + burna | laisvai | ⏳ |

Papildomai: `ˋ` (U+02CB) išgyvena NFD ir Wyoming kelią; SHA256 sutampa
paketas ↔ serveris.

## 6. Kas nesuveikė ir kaip pataisyta

(pildoma darant)
