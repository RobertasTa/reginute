# Du asistentai dviem kalbomis vienoje Home Assistant kolonėlėje

> Pilna instrukcija: kaip tą pačią Voice PE kolonėlę išmokyti dviejų kalbų —
> vienas žadinimo žodis kalba viena kalba ir vienu balsu, kitas — kita.
> Patikrinta gyvai 2026-09-04: rusiškas „Okay Nabu" + lietuviškas „Hey Jarvis"
> su Reginutės balsu, HA Core 2026.9.0 (HAOS), Voice PE fw 26.6.0.
> Meniu vardai duodami **rusiškai** (taip buvo pas mus) ir **angliškai**
> (kaip oficialiuose dokuose) — kitos kalbos GUI atitinka anglišką.

## Kodėl taip, o ne „vienas asistentas, kuris supranta abi kalbas"

Kolonėlė po žadinimo žodžio įrašo **visą sakinį iki tylos** ir atiduoda jį
kalbos atpažinimui **vienu gabalu, viena kalba**. Kalbą atpažinimui HA parenka
**prieš** klausydamas — pagal tai, kuris asistentas pažadintas. Todėl:

- trumpose komandose automatinis kalbos spėjimas nepatikimas;
- „trigerio žodžio" sakinio viduryje („Okay Nabu, *Regina*, įjunk šviesą")
  perjungti ausų **negali** — sakinį jau užrašė pirmos kalbos ausys.

Nuo **HA 2025.10** kiekvienas Assist palydovas gali turėti **iki dviejų
žadinimo žodžių, ir kiekvienas paleidžia savo asistentą** („multilingual
assistants", Voice chapter 11). Kalbą renka žmogus žadindamas. Tai ir yra
teisingas kelias.

## Ko reikia

| | Minimumas | Pas mus |
|---|---|---|
| Home Assistant | 2025.10 ar naujesnis | 2026.9.0 |
| Kolonėlė | Voice PE su programine įranga, mokančia >1 žadinimo žodį (2025.10+) | fw 26.6.0 |
| Antros kalbos **ausys** (STT) | bet kuri Wyoming tarnyba, mokanti tą kalbą | Paprika (Whisper LT) |
| Antros kalbos **burna** (TTS) | Wyoming tarnyba su tos kalbos balsu | Reginutė (Piper) |
| Smegenys | HA vidinės (komandoms) arba LLM (pokalbiui) | HA / Gemma |

Kolonėlės žadinimo žodžiai gyvena **pačiame įrenginyje** (microWakeWord):
Voice PE turi `Okay Nabu`, `Hey Jarvis`, `Hey Mycroft`. Savo žodžiui reikia
mokymo (žr. pabaigoje).

## 1 žingsnis — antros kalbos tarnybos į HA

*Настройки → Устройства и службы → Добавить интеграцию → Wyoming Protocol*
(EN: *Settings → Devices & services → Add integration → Wyoming Protocol*).

Įvesk tarnybos adresą ir portą — atskirai ausims ir burnai. Kiekviena
atsiranda sąraše kaip dar vienas Wyoming įrašas. **Esamų tarnybų neliesk** —
naujos eina šalia.

Patarimas: iš karto pervadink (⋮ → *Переименовать* / *Rename*), pvz.
„faster-whisper LT", kad nesimaišytų su pirmos kalbos ausimis.

## 2 žingsnis — antras asistentas

*Настройки → Голосовые ассистенты → Добавить ассистента*
(EN: *Settings → Voice assistants → Add assistant*).

| Laukas (RU / EN) | Ką rinkti |
|---|---|
| Название / Name | asistento vardas (pas mus „Reginutė") |
| Язык / Language | antra kalba |
| Диалоговая система / Conversation agent | **Home Assistant** — komandos vykdomos tiesiai, be LLM. Laisvam pokalbiui — LLM agentas (pas mus Gemma; jis gali būti tas pats, kurį naudoja pirmas asistentas — daugiakalbiam modeliui perkrauti nieko nereikia) |
| Распознавание речи / Speech-to-text | antros kalbos ausys iš 1 žingsnio; Язык — antra kalba |
| Синтез речи / Text-to-speech | antros kalbos burna; Язык — antra kalba; Голос / Voice — konkretus balsas |

Pirmo asistento nieko nekeisk. Mygtukas *Попробуйте голос* / *Try voice* iš
karto parodo, ar burna kalba.

## 3 žingsnis — antras žadinimo žodis kolonėlei

*Настройки → Голосовые ассистенты* → puslapio apačioje nuoroda
**„N устройства Assist"** (EN: *Assist devices*) → pasirink kolonėlę →
atsidaro jos įrenginio puslapis → kortelė **„Настройки"** (EN: *Settings*).

Ten keturi laukai (vardai — kaip HA ESPHome integracija juos kuria):

| Laukas | Reikšmė |
|---|---|
| Ассистент / Assistant | pirmas asistentas — **nelieti** |
| Фраза активации / Wake word | pirmas žodis (Okay Nabu) — **nelieti** |
| **Assistant 2** | → antras asistentas |
| **Wake word 2** | → antras žodis (Hey Jarvis) |

Įsigalioja iš karto, kolonėlės perkrauti nereikia. Jei turi kelias kolonėles —
kiekvienai atskirai; galima palikti dalį tik vienos kalbos.

Jei lauko **Wake word 2** nėra — kolonėlės programinė įranga senesnė nei
2025.10; atnaujink per *Настройки → Обновления* / *Settings → Updates*.

## 4 žingsnis — kad antra kalba suprastų tavo namus

HA komandas lygina **raidė į raidę** su tos kalbos frazių rinkiniu. Daiktų ir
kambarių vardai pas tave greičiausiai pirma kalba, tad antrai reikia
**alternatyvių pavadinimų (aliasų)** — jie tik pridedami, pirmos kalbos
niekas nekeičia.

Pigiausia — **zonoms** (kambariams), ne kiekvienam daiktui:
*Настройки → Области и зоны → ✏ → „Альтернативные названия" → „Добавить"*
(EN: *Settings → Areas → edit → Aliases*). Pavyzdys: zonai „Ванная" pridėti
`vonioje`, `vonia`, `tualete`. Tada „įjunk šviesą vonioje" veikia be jokių
lempų vardų.

Kalbose su linksniais dėk **kelis aliasus su skirtingom galūnėm** — HA
neskaito gramatikos. Ir dėk taip, kaip **realiai sakai** ir kaip ausys **realiai
užrašo** (pasitikrink 5 žingsnyje).

## 5 žingsnis — bandymas ir kur žiūrėti, kai neveikia

Pasakyk: „**Hey Jarvis**" — palauk pyptelėjimo — komanda antra kalba.

Kai kas nors ne taip, atidaryk *Настройки → Голосовые ассистенты → asistentas
→ ⋮ → Отладка* (EN: *Debug*). Ten kiekvienas paleidimas išskleistas
etapais: ką **ausys užrašė**, ką **smegenys suprato**, ką **burna pasakė**.
Beveik visada bėda matosi viename iš trijų:

| Ką matai | Priežastis | Ką daryti |
|---|---|---|
| Kolonėlė nepypteli | žodžio neatpažino | tarti lėčiau, „Jarvis" su angl. „r"; jautrumas *Wake word sensitivity* |
| Užrašyta kirilica / kita kalba | pažadinta ne tuo žodžiu | patikrinti, kuris žodis kuriam asistentui (3 žingsnis) |
| Užrašyta teisingai, „nesuprasta" | trūksta aliaso arba frazė ne iš HA rinkinio | 4 žingsnis; HA palaikomos frazės — `github.com/OHF-voice/intents/sentences/<kalba>` |
| Suprasta, bet tyli | burna negrąžino garso | *Попробуйте голос*; tarnybos žurnalas |

## Ko čia NĖRA (sąmoningai)

- **Savo žadinimo žodis** („Regina" vietoj „Jarvis"): reikia išmokyti
  microWakeWord/openWakeWord modelį (~1 val., mokoma sintetiniais balsais) ir
  įkelti į kolonėlę. Nepatikrinta mūsų rankomis — čia neaprašom.
- **Vienas žadinimo žodis, perjungimas automatizacija** (senesnėms
  kolonėlėms): sakinio trigeris pirma kalba („Регина") → automatizacija keičia
  kolonėlės lauką *Ассистент* → kita komanda jau antra kalba → po minutės
  grąžina. Veikia dviem įkvėpimais. Nenaudojom, nes antras žodis paprastesnis.

## Kas buvo pas mus

Rusiška: „Okay Nabu" → Whisper ru → HA / sekretorė Alisa → Silero.
Lietuviška: „Hey Jarvis" → Paprika (Whisper LT) → HA lt frazės → Reginutė
(Piper). Pirma komanda balsu: „Hey Jarvis, įjunk šviesą vonioje" — lempa
įsijungė, atsakymas „šviesos įjungtos" lietuviškai. Nė vienas rusiško kelio
nustatymas nepaliestas; antra kolonėlė miegamajame liko kaip buvo.
