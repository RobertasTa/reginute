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

## 3. Tarnyba (systemd) ⏳

`wyoming-reginute.service`, portas **10250** (ne 10200), `--length-scale`
pagal `.onnx.json` numatytąjį. ⏳ vienetų failas bus įklijuotas iš veikiančio.

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
