"""Tests for the number and abbreviation expander (pytest).

Each case is what a person would say. Most come from Home Assistant's own
Lithuanian answers (sensor states "21.5 °C", "45 %", timers "2 minutės", the
date "2026 m. spalio 24 d.") and from Lithuanian news ("250.000 žmonių",
"22.30 val.", "1,3 mln. eurų") - the two sources that broke it in 2026-10.
A unit agrees with the last number actually spoken ("100,5 km" -> "... penki
kilometrai"), as the module documents.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skaiciu_pletiklis import isplesk  # noqa: E402

CASES = [
    ("21.5 laipsnių", "dvidešimt vienas kablelis penki laipsnių"),
    ("22 laipsnių", "dvidešimt du laipsnių"),
    ("12.3 °C ir debesuota", "dvylika kablelis trys laipsniai ir debesuota"),
    ("-3.5 °C ir sninga", "minus trys kablelis penki laipsniai ir sninga"),
    ("−7 °C ir giedra", "minus septyni laipsniai ir giedra"),
    ("1 °C ir lyja", "vienas laipsnis ir lyja"),
    ("Svetainės temperatūra yra 21.5 °C", "Svetainės temperatūra yra dvidešimt vienas kablelis penki laipsniai"),
    ("Svetainės temperatūra yra 21.50 °C", "Svetainės temperatūra yra dvidešimt vienas kablelis penkiasdešimt laipsnių"),
    ("Drėgmė yra 45 %", "Drėgmė yra keturiasdešimt penki procentai"),
    ("Drėgmė yra 45.5 %", "Drėgmė yra keturiasdešimt penki kablelis penki procentai"),
    ("Baterija yra 1 %", "Baterija yra vienas procentas"),
    ("Baterija yra 100 %", "Baterija yra šimtas procentų"),
    ("Slėgis yra 1013.2 hPa", "Slėgis yra tūkstantis trylika kablelis du hektopaskaliai"),
    ("Vėjas yra 3.2 km/h", "Vėjas yra trys kablelis du kilometrai per valandą"),
    ("Vėjas yra 4 m/s", "Vėjas yra keturi metrai per sekundę"),
    ("Galia yra 120 W", "Galia yra šimtas dvidešimt vatų"),
    ("Galia yra 1.5 kW", "Galia yra vienas kablelis penki kilovatai"),
    ("Energija yra 3.25 kWh", "Energija yra trys kablelis dvidešimt penkios kilovatvalandės"),
    ("Energija yra 1.250 kWh", "Energija yra viena kablelis du šimtai penkiasdešimt kilovatvalandžių"),
    ("Apšvietimas yra 350 lx", "Apšvietimas yra trys šimtai penkiasdešimt liuksų"),
    ("CO2 yra 600 ppm", "CO2 yra šeši šimtai milijoninių dalių"),
    ("Triukšmas yra 45 dB", "Triukšmas yra keturiasdešimt penki decibelai"),
    ("14:05", "keturiolika nulis penki"),
    ("2026 m. spalio 24 d.", "du tūkstančiai dvidešimt šeštų metų spalio dvidešimt ketvirtoji diena."),
    ("Laikmatis nustatytas 2 minutės", "Laikmatis nustatytas dvi minutės"),
    ("Laikmatis nustatytas 5 minutės", "Laikmatis nustatytas penkios minutės"),
    ("Laikmatis nustatytas 1 valanda ir 30 minutės", "Laikmatis nustatytas viena valanda ir trisdešimt minutės"),
    ("2 veikiantys laikmačiai.", "du veikiantys laikmačiai."),
    ("1 pristabdytas laikmatis.", "vienas pristabdytas laikmatis."),
    ("Įjungta 2 lemputės", "Įjungta dvi lemputės"),
    ("Liko 21 minutė", "Liko dvidešimt viena minutė"),
    ("Liko 4 sekundės", "Liko keturios sekundės"),
    ("Laikmačių yra 2", "Laikmačių yra du"),
    ("Skaičius 5 yra nelyginis", "Skaičius penki yra nelyginis"),
    ("0.05 mm", "nulis kablelis nulis penki milimetrai"),
    ("0,05 mm", "nulis kablelis nulis penki milimetrai"),
    ("21,25 °C", "dvidešimt vienas kablelis dvidešimt penki laipsniai"),
    ("2,5 km", "du kablelis penki kilometrai"),
    ("Kaina 9.99 €", "Kaina devyni eurai devyniasdešimt devyni centai"),
    ("Pi lygus 3.14159", "Pi lygus trys kablelis vienas keturi vienas penki devyni"),
    ("versija 1.8.0", "versija vienas.aštuoni.nulis"),
    ("2026.10.24", "du tūkstančiai dvidešimt šeši.dešimt.dvidešimt keturi"),
    ("Renginys prasidės 15.30", "Renginys prasidės penkiolika trisdešimt"),
    ("Policijos duomenimis, 22.30 val.", "Policijos duomenimis, dvidešimt du trisdešimt valandos"),
    ("Atidaryta nuo 8.00 iki 17.00", "Atidaryta nuo aštuntos valandos iki septynioliktos valandos"),
    ("Fondas siekia 90.000 Eur.", "Fondas siekia devyniasdešimt tūkstančių eurų."),
    ("žygiavo 250.000 žmonių", "žygiavo du šimtai penkiasdešimt tūkstančių žmonių"),
    ("atleis 2.500 darbuotojų", "atleis du tūkstančiai penki šimtai darbuotojų"),
    ("spalio 23 d. apie 7.50 val. įvyko", "spalio dvidešimt trečiąją dieną apie septyni penkiasdešimt valandos įvyko"),
    ("nuo spalio 23 d. iki lapkričio 5 d.", "nuo spalio dvidešimt trečiosios dienos iki lapkričio penktosios dienos."),
    ("Rungtynės baigėsi 85:79", "Rungtynės baigėsi aštuoniasdešimt penki septyniasdešimt devyni"),
    ("5-7 dienos", "penki-septynios dienos"),
    ("COVID-19 atvejai", "COVID-devyniolika atvejai"),
    ("5 A klasė", "penki A klasė"),
    ("W. Shakespeare", "W. Shakespeare"),
    ("žala – 1,3 mln. eurų", "žala – vienas kablelis trys milijonai eurų"),
    ("bauda – 405,4 tūkst. eurų", "bauda – keturi šimtai penki kablelis keturi tūkstančiai eurų"),
    ("per 0,5 mln. eurų", "per nulis kablelis penki milijonai eurų"),
    ("paskolinti 1,06 mlrd. eurų", "paskolinti vienas kablelis nulis šeši mlrd. eurų"),
    ("Lietuvoje knygą pristatysiu lapkričio 29 d.", "Lietuvoje knygą pristatysiu lapkričio dvidešimt devintąją dieną."),
    ("Apie tai spalio 20 d.", "Apie tai spalio dvidešimtąją dieną."),
    ("vyras nušovė žmogų, dar 5 sužeidė", "vyras nušovė žmogų, dar penki sužeidė"),
    ("dėl 850 naikintuvų F-35 gamybos", "dėl aštuonių šimtų penkiasdešimties naikintuvų F-trisdešimt penki gamybos"),
    ("gautos 829 paraiškos", "gautos aštuoni šimtai dvidešimt devynios paraiškos"),
    ("Nuo 2027 m. sausio 1 d.", "Nuo du tūkstančiai dvidešimt septintų metų sausio pirmosios dienos."),
]


@pytest.mark.parametrize("text,expected", CASES)
def test_isplesk(text, expected):
    assert isplesk(text) == expected
