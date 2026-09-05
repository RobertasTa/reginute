# SKAIČIŲ PLĖTIKLIS v2 — lietuviškas skaitvardžių žvėrynas Reginai.
# Roberto užsakymas 09-02: „apgalvok ir sutvarkyk iki milijonų, kad mokėtų."
# Verčia skaičius žodžiais SU TEISINGA FORMA pagal kontekstą PRIEŠ
# fonemizaciją. Modelio mokyti nereikia — jis taria fonemas (generatyvus).
#
# Formos žymimos: V vardininkas, G galininkas, K kilmininkas, I įnagininkas;
# _f — moteriška giminė. Kelintiniai: kamienas + galūnė pagal kontekstą;
# sudėtiniuose kelintinis TIK paskutinis dėmuo (du tūkstančiai penktais).
# Ko sąmoningai nedengiam (fallback į V): vietininkas, retos įvardžiuotinių
# formos, dvejetiniai (dveji metai) — pildysim iš Roberto perklausų.
import re

# --- kiekiniai vienetai --------------------------------------------------
VNT = {
    1: {"V": "vienas", "G": "vieną", "K": "vieno", "I": "vienu",
        "V_f": "viena", "G_f": "vieną", "K_f": "vienos", "I_f": "viena"},
    2: {"V": "du", "G": "du", "K": "dviejų", "I": "dviem",
        "V_f": "dvi", "G_f": "dvi", "K_f": "dviejų", "I_f": "dviem"},
    3: {"V": "trys", "G": "tris", "K": "trijų", "I": "trimis",
        "V_f": "trys", "G_f": "tris", "K_f": "trijų", "I_f": "trimis"},
    4: {"V": "keturi", "G": "keturis", "K": "keturių", "I": "keturiais",
        "V_f": "keturios", "G_f": "keturias", "K_f": "keturių", "I_f": "keturiomis"},
    5: {"V": "penki", "G": "penkis", "K": "penkių", "I": "penkiais",
        "V_f": "penkios", "G_f": "penkias", "K_f": "penkių", "I_f": "penkiomis"},
    6: {"V": "šeši", "G": "šešis", "K": "šešių", "I": "šešiais",
        "V_f": "šešios", "G_f": "šešias", "K_f": "šešių", "I_f": "šešiomis"},
    7: {"V": "septyni", "G": "septynis", "K": "septynių", "I": "septyniais",
        "V_f": "septynios", "G_f": "septynias", "K_f": "septynių", "I_f": "septyniomis"},
    8: {"V": "aštuoni", "G": "aštuonis", "K": "aštuonių", "I": "aštuoniais",
        "V_f": "aštuonios", "G_f": "aštuonias", "K_f": "aštuonių", "I_f": "aštuoniomis"},
    9: {"V": "devyni", "G": "devynis", "K": "devynių", "I": "devyniais",
        "V_f": "devynios", "G_f": "devynias", "K_f": "devynių", "I_f": "devyniomis"},
}
# 11–19: linksniuojasi kaip mot. -a (vienuolika/vienuolikos/vienuolika...)
# ⚠️ 09-04 IŠTAISYTA: pirmas dėmuo buvo „vien" → 11 visur skambėjo „VIENLIKA"
# (ir 111 „šimtas vienlika", ir kelintinis „vienliktas"). Rasta atsitiktinai,
# tikrinant kainą „11,15 Eur". Klaida būtų iškeliavusi kartu su dovana.
PALIKT = {n: "vienuo dvy try keturio penkio šešio septynio aštuonio devynio".split()[n - 11] + "lika"
          for n in range(11, 20)}


def _palikt(n, forma):
    z = PALIKT[n]
    if forma == "K":
        return z[:-1] + "os"
    return z  # V/G/I sutampa praktikoje


DESIMT = {10: "dešimt", 20: "dvidešimt", 30: "trisdešimt",
          40: "keturiasdešimt", 50: "penkiasdešimt", 60: "šešiasdešimt",
          70: "septyniasdešimt", 80: "aštuoniasdešimt", 90: "devyniasdešimt"}
DESIMT_K = {10: "dešimties", 20: "dvidešimties", 30: "trisdešimties",
            40: "keturiasdešimties", 50: "penkiasdešimties",
            60: "šešiasdešimties", 70: "septyniasdešimties",
            80: "aštuoniasdešimties", 90: "devyniasdešimties"}


# ⚠️ 09-05: „tūkstantis" yra i-kamienas su t→č kaita, ir bendrinė galūnių
# logika jam netinka — ji davė „tūkstantiį", „tūkstantio", „tūkstantu"
# („kainuoja 1000 eurų" -> „tūkstantiį eurų"). Aiškios formos:
TUKSTANTIS_VNS = {"V": "tūkstantis", "G": "tūkstantį",
                  "K": "tūkstančio", "I": "tūkstančiu"}


def _grupe(zodis_vns, zodis_dgs, zodis_kilm, n, forma):
    """šimtas/tūkstantis/milijonas grupės žodis pagal kiekį ir linksnį."""
    # ⚠️ 09-05: vienaskaitos reikalauja ne tik 1, bet ir 21, 31 … 91
    # („dvidešimt vienas tūkstantis", ne „tūkstančiai"). Ta pati riba buvo
    # žinoma ir milijonuose („skirs 21 mln." davė „dvidešimt vieną milijonUS")
    # — uždarom abu vienoje vietoje. 11 — išimtis (vienuolika tūkstančių).
    vienas = (n % 10 == 1 and n % 100 != 11)
    if vienas and zodis_vns == "tūkstantis":
        return TUKSTANTIS_VNS.get(forma, zodis_vns)
    if forma == "K":
        return zodis_kilm if not vienas else zodis_vns[:-2] + ("o" if zodis_vns.endswith("as") else "io")
    if vienas:
        return {"V": zodis_vns, "G": zodis_vns[:-1] + "į" if zodis_vns.endswith("is")
                else zodis_vns[:-2] + "ą", "I": zodis_vns[:-2] + "u"}.get(forma, zodis_vns)
    # 2-9 -> dgs; 10-19/dešimtys -> kilmininkas
    if n % 10 == 0 or 11 <= n % 100 <= 19:
        return zodis_kilm
    return {"V": zodis_dgs, "G": zodis_dgs[:-2] + "us",
            "I": zodis_dgs[:-2] + "ais"}.get(forma, zodis_dgs)


def kiekinis(n, forma="V", gimine=""):
    """0–999 999 999 kiekinis nurodyta forma (V/G/K/I), gimine ''|'_f'."""
    if n == 0:
        return {"V": "nulis", "G": "nulį", "K": "nulio", "I": "nuliu"}[forma]
    if n < 0:
        return "minus " + kiekinis(-n, forma, gimine)
    dalys = []

    def trejetas(m, f):
        z = []
        if m >= 100:
            s = m // 100
            if s > 1:
                # ⚠️ 09-04, rasta tuo pačiu testu: šimtų DAUGIKLIS derinasi su
                # linksniu („devynIŲ šimtų", ne „devynI šimtų").
                z.append(VNT[s].get(f, VNT[s]["V"]))
            z.append(_grupe("šimtas", "šimtai", "šimtų", s, f))
            m %= 100
        if 11 <= m <= 19:
            z.append(_palikt(m, f))
            m = 0
        elif m >= 10:
            d = m - m % 10
            # ⚠️ 09-04 (Roberto ausis: „skaičius sako blogai"): SUDĖTINIAME
            # skaitvardyje dešimtys NELINKSNIUOJAMOS — linksniuojasi tik
            # PASKUTINIS dėmuo. Buvo „devynių eurų devyniasdešimtIES devynių
            # centų"; taisyklinga — „devyniasdešimt devynių".
            # Kilmininko forma imama TIK kai dešimtys pačios yra paskutinės
            # („iš devyniasdešimties"), t. y. kai vienetų nėra.
            paskutine = (m % 10 == 0)
            z.append(DESIMT_K[d] if (f == "K" and paskutine) else DESIMT[d])
            m %= 10
        if m:
            z.append(VNT[m][f + gimine] if (f + gimine) in VNT[m] else VNT[m][f])
        return z

    if n >= 1_000_000:
        mln = n // 1_000_000
        # ⚠️ 09-04 (rasta Reginos naujienose): daugiklis prieš „milijonus" buvo
        # užrakintas vardininku, tad „skirs 5 mln." duodavo „penkI milijonUS".
        # Ta pati klaida, kaip šįryt su šimtais — daugiklis turi derintis su
        # linksniu. Kilmininke ir toliau lieka „V" (penki milijonai eurų).
        # 09-05: „K" pridėtas kartu su tūkstančiais — „nuo 5 mln. eurų" davė
        # „nuo penki milijonų". 09-04 komentaras apie kilmininką galiojo, kol
        # tikro kilmininko kelio nebuvo.
        mln_f = forma if forma in ("G", "I", "K") else "V"
        if mln > 1:
            dalys += trejetas(mln, mln_f)
        dalys.append(_grupe("milijonas", "milijonai", "milijonų", mln, forma))
        n %= 1_000_000
    if n >= 1000:
        t = n // 1000
        # ⚠️ 09-05 (plano punktas „tūkstančių daugiklis"): ta pati klaida, kaip
        # šįryt su šimtais ir vakar su milijonais — daugiklis prieš
        # „tūkstančius" buvo užrakintas vardininku, tad „skirs 5000 eurų"
        # duodavo „penkI tūkstančius", o „gavo 3000" — „trys tūkstančius".
        # Sąlyga ta pati, kaip milijonuose (žr. žemiau).
        # ⚠️ 09-05 antras ratas: „K" į sąlygą įrašytas TIK dabar, kai atsirado
        # 6b punktas (kilmininkiniai prielinksniai). Iki tol kilmininkas per
        # `isplesk` buvo nepasiekiamas, ir riba buvo palikta sąmoningai — o
        # atsiradus keliui ji iškart pasirodė kaip „nuo du tūkstančių eurų".
        # ⚠️ 09-05 trečias ratas: sąlyga buvo `n % 1000 == 0`, t. y. tūkstančiai
        # derinosi TIK kai jie paskutinis dėmuo. Todėl „nuo 3500 eurų" duodavo
        # „nuo trys tūkstančiai penkių šimtų" — lietuviškai skirtingos grupės
        # (tūkstančiai + šimtai) linksniuojamos VISOS. Tai ne tas pats, kas
        # 28a taisyklė: ten dešimtys ir vienetai VIENOJE grupėje („devyniasdešimt
        # devynių"), o čia dvi atskiros grupės.
        tukst_f = forma if forma in ("G", "I", "K") else "V"
        if t > 1:
            dalys += trejetas(t, tukst_f)
        dalys.append(_grupe("tūkstantis", "tūkstančiai", "tūkstančių", t, forma))
        n %= 1000
    if n:
        dalys += trejetas(n, forma)
    return " ".join(dalys)


# --- kelintiniai ---------------------------------------------------------
KELINT_KAM = {1: "pirm", 2: "antr", 3: "treči", 4: "ketvirt", 5: "penkt",
              6: "šešt", 7: "septint", 8: "aštunt", 9: "devint", 10: "dešimt",
              20: "dvidešimt", 30: "trisdešimt", 40: "keturiasdešimt",
              50: "penkiasdešimt", 60: "šešiasdešimt", 70: "septyniasdešimt",
              80: "aštuoniasdešimt", 90: "devyniasdešimt"}
for _n in range(11, 20):
    KELINT_KAM[_n] = PALIKT[_n][:-1] + "t"
# galūnės: (gimine, forma) -> galūnė; ivardž. atskirai
KELINT_GAL = {("m", "V"): "as", ("m", "G"): "ą", ("m", "K"): "o",
              ("m", "Idgs"): "ais", ("m", "Vdgs"): "i",
              ("f", "V"): "a", ("f", "G"): "ą", ("f", "K"): "os", ("m", "Kdgs"): "ų"}
IVARDZ = {("m", "V"): "asis", ("m", "G"): "ąjį", ("f", "V"): "oji",
          ("f", "G"): "ąją", ("m", "Idgs"): "aisiais"}


def kelintinis(n, gimine="m", forma="V", ivardz=False):
    """Sudėtinis kelintinis: kelintinis TIK paskutinis dėmuo."""
    if n <= 0:
        return kiekinis(n)
    lik = n % 100
    if lik == 0:
        lik = n % 1000 if n % 1000 else n  # 1900 -> "šimtųjų"? fallback žemiau
    baze = n - (n % 100)
    pask = n % 100
    priek = ""
    if pask == 0:                     # apvalūs: 2000-aisiais (fallback kiekinis+gal)
        kam = KELINT_KAM.get(n // (10 ** (len(str(n)) - 1)))
        return kiekinis(n) + ("-aisiais" if forma == "Idgs" else "")
    if pask > 20 and pask % 10:
        priek = DESIMT[pask - pask % 10] + " "
        pask = pask % 10
    kam = KELINT_KAM[pask]
    gal = (IVARDZ if ivardz else KELINT_GAL).get((gimine, forma))
    if gal is None:
        gal = KELINT_GAL[("m", "V")]
    zodis = priek + kam + gal
    return (kiekinis(baze) + " " if baze else "") + zodis


# --- santrumpos ----------------------------------------------------------
SANTRUMPOS = [(r"\bproc\.", " procentai"), (r"\bval\.(?=\s|$)", " valandos"),
              (r"\bEur\b", " eurų"), (r"\bmln\.", " milijonai"),
              (r"\bkm\b", " kilometrų"), (r"\bkg\b", " kilogramų"),
              (r"\bLR\b", "Lietuvos Respublikos")]

# --- RAIDINES SANTRUMPOS (Roberto radinys 09-03) -------------------------
# „MTL" Reginute isbardavo kaip vientisa zodi, o Ona kiekviena raide taria
# atskirai su mazute pauze — todel ju girdisi. Perrasom raidziu vardais.
RAIDZIU_VARDAI = {
    "A": "a", "Ą": "a nosinė", "B": "bė", "C": "cė", "Č": "čė", "D": "dė",
    "E": "e", "Ę": "e nosinė", "Ė": "ė", "F": "ef", "G": "gė", "H": "ha",
    "I": "i", "Į": "i nosinė", "Y": "ilgoji i", "J": "jot", "K": "ka",
    "L": "el", "M": "em", "N": "en", "O": "o", "P": "pė", "Q": "kū",
    "R": "er", "S": "es", "Š": "eš", "T": "tė", "U": "u", "Ų": "u nosinė",
    "Ū": "ilgoji u", "V": "vė", "W": "dviguba vė", "X": "iks", "Z": "zė",
    "Ž": "žė",
}
# Skaitomos kaip ZODIS, ne raidemis — neliesti.
# ⭐ JAV ir FIBA irodyti duomenimis (09-03, Roberto pastaba): LIEPA garsyno
# tekstuose „ES" israsyta kaip „E ES", „NMA" kaip „EN EM A", bet „JAV"
# paliktas NEISSKAIDYTAS, o g2p zodynas ji raso j' e v' = „jav" sulietai.
# ⇒ pilni raidziu vardai (em, es, el, te, ve) — norma (patvirtina ir LIEPA,
# ir zodynas: TV -> „te ve", KGB -> „ka ge be", LRT -> „el er te"),
# BET JAV yra tikra isimtis.
SANTRUMPOS_ZODZIU = {
    "NATO", "UNESCO", "UNICEF", "SODRA", "LIEPA", "COVID", "AIDS", "LED",
    "PIN", "WIFI", "USB", "PDF", "GPS", "JAV", "FIBA", "NASA", "DELFI",
    # ⭐ 09-05 Roberto ausis: „girdžiu vė em i, o turėčiau girdėti vmi" ir
    # „VMI taip dėk į išimčių žurnalą". Antra išimtis po JAV, ir abi rastos
    # tuo pačiu būdu — ne taisykle, o klausantis. Skaidymas raidėmis lieka
    # numatytas visiems kitiems (LIEPA tekstuose „E ES", „EN EM A"), o čia
    # trumpinys jau suaugęs į vieną žodį.
    "VMI",
}


_ZODZIU_SARASAS = None


def _yra_tikras_zodis(s):
    """Ar tai NORMALUS lietuviskas zodis, tik parasytas didziosiomis?
    Tikrinam g2p zodyne (232 913 zodziu) — taip apsaugom „ORAI", „KARAS",
    „NAUJA" nuo skaldymo i raides (Roberto ispejimas 09-03: naujienose
    santrumpos daznos, bet ir pabrezimai didziosiomis pasitaiko)."""
    global _ZODZIU_SARASAS
    if _ZODZIU_SARASAS is None:
        import io
        import os
        _ZODZIU_SARASAS = set()
        # 09-03: kelias nebe kietas — serveryje (LXC 214) pilno žodyno nėra,
        # o be jo apsauga nustotų veikti TYLIAI ir „ORAI" virstų „o er a i".
        # Šalia modulio guli `piper_lt\zodziai_trumpi.txt` (33 895 žodžiai po
        # 4–6 raides — tik tiek ir tereikia, nes tikrinam 4–5 didžiąsias).
        cia = os.path.dirname(os.path.abspath(__file__))
        for kelias in (os.path.join(r"D:\_Balsas Lietuviksas", "_modeliai",
                                    "g2p-lt", "lexicon.tsv"),
                       os.path.join(cia, "piper_lt", "zodziai_trumpi.txt"),
                       os.path.join(cia, "zodziai_trumpi.txt")):
            if os.path.exists(kelias):
                for eil in io.open(kelias, encoding="utf-8"):
                    _ZODZIU_SARASAS.add(eil.split("\t", 1)[0].strip())
                break
    return s.lower() in _ZODZIU_SARASAS


def raidem(m):
    """AAA -> „a a a" (kiekviena raide atskiru zodziu; tarpas duoda pauze)."""
    s = m.group(0)
    if s in SANTRUMPOS_ZODZIU:
        return s
    # Zodyno patikra TIK nuo 4 raidziu: trumpesniuose (ES, JAV, VU, DI)
    # sutapimu su tikrais zodziais daug, bet didziosiomis jie praktiskai
    # visada yra santrumpos. Nuo 4 raidziu jau tiketi tikri zodziai
    # („ORAI", „KARAS") — juos saugom.
    if len(s) >= 4 and _yra_tikras_zodis(s):
        return s
    # 09-03 Roberto ausis: „ES ištarė neaiškiai… gal pauzės per trumpos".
    # Ona tarp raidžių daro pauzeles. Brūkšnelis = trumpa pauzė sintezėje
    # (sintezuok_zinias: KABLELIS; synth_reginute: 0,10 s) — raidės tampa
    # atskirais gabalais, o ne suplaktu žodžiu.
    # Brūkšneliai ir IŠ ABIEJŲ PUSIŲ: be jų pirmoji/paskutinė raidė prilimpa
    # prie gretimo žodžio („vė - em - i primena") ir netenka pauzės.
    # Pertekliniai brūkšneliai (sakinio gale, prieš skyrybą) valomi isplesk().
    # ⭐ 09-03 vakare, 4 ratas — GRĮŽTA PRIE MOKYMO DUOMENŲ (Roberto priekaištas
    # „į Piper vėl su kitokiom formulėm"). LIEPA tekstuose raidės rašomos
    # PAPRASTAIS ŽODŽIAIS SAKINIO VIDURYJE, be jokių skyriklių:
    #   „Rusijos ir Europos Sąjungos E ES."  -> mokyme: ˌea ˈes
    #   „Kurio kodas įsiterpė į mūsų DĖ EN ER." -> dʲˈee ˈen ˈer
    #   „U. A. Bė Stragutės mėsa"            -> ˋu. ˌa. bʲˈee
    # Regina jas taip ir įrašė, ir modelis taip jų mokėsi. Buvau įdėjęs
    # brūkšnelius („ - "), kad atsirastų pauzės — bet tai IŠSKIRIA santrumpą į
    # atskirą trumpą gabalą, kokio mokymo duomenyse NIEKADA nebuvo.
    # ⭐ 09-03 VĖLAI — GRĮŽTA PAUZELĖS, bet dabar pagrįstos KITU kriterijumi.
    # Anksčiau jas nuėmiau, nes ASR matavimas rodė, kad su pauzėmis mašina
    # trumpinį atpažįsta blogiau (6/11 prieš 8/11). Bet ASR matuoja MAŠINOS
    # atkūrimą, o kolonėlė kalba ŽMOGUI. Roberto ausis ir radijo diktoriaus
    # maniera: „VMI su mažom pauzelėm tarp raidžių gaunasi geriau".
    # ⇒ žmogaus aiškumas viršesnis; pauzė 0,10 s (`synth_reginute.pauze["-"]`).
    #
    # ⭐⭐ 09-05, PENKTAS RATAS — pauzės NUIMAMOS IŠ VIDAUS, paliekamos IŠ ŠONŲ.
    # Roberto palyginimas: A (pauzelės tarp raidžių) — „taip negerai";
    # B (be pauzelių) — „santrumpa gerai, tik visas tekstas kaip žirniai į
    # sieną". Antroji pastaba buvo apie VISĄ tekstą, ne apie trumpinį: išėmus
    # brūkšnelius sakinys tapdavo VIENU gabalu, o greičio išlyginimas dirba per
    # gabalus — tad skubėjo kalba, ne santrumpa.
    # ⇒ Raidės jungiamos TARPAIS (skamba sulietai, kaip B), o brūkšneliai lieka
    # tik iš šonų: taip santrumpa vis tiek atskiriamas gabalas, `synth_reginute`
    # ją atpažįsta (pries/zenklas == "-") ir taria LĖČIAU
    # (`SANTRUMPOS_LETUMAS` 1.15 — Roberto pasirinktas iš 1.0/1.15/1.30).
    return " - " + " ".join(RAIDZIU_VARDAI.get(c, c) for c in s) + " - "


# Lietuviškas skaitvardžio ir daiktavardžio derinimas (vns. / dgs. / kilm.):
# 21 euRAS · 2–9, 22–29 euRAI · 10, 11–19, 20, 30 euRŲ.
EURAI = ("euras", "eurai", "eurų")
CENTAI = ("centas", "centai", "centų")
# Mato vienetai, kuriems reikia to paties derinimo (žr. `isplesk` 0− punktą).
# Ketvirtas laukas — giminė: "" vyriška, "_f" moteriška („dvi tonos", ne „du").
# ⚠️ 09-04 antras praplėtimas (Roberto ausis: „2 g, 2 t, 2 cm skamba juokingai"
# — iki tol lentelėje buvo TIK km/kg/proc, o visi kiti likdavo raide: „du gė").
VIENETAI = {
    "km":  ("kilometras", "kilometrai", "kilometrų", ""),
    "cm":  ("centimetras", "centimetrai", "centimetrų", ""),
    "mm":  ("milimetras", "milimetrai", "milimetrų", ""),
    "kg":  ("kilogramas", "kilogramai", "kilogramų", ""),
    "ml":  ("mililitras", "mililitrai", "mililitrų", ""),
    "ha":  ("hektaras", "hektarai", "hektarų", ""),
    # elektra (Roberto prašymas — „dažnai pasitaiko"):
    "kW":  ("kilovatas", "kilovatai", "kilovatų", ""),
    "Wh":  ("vatvalandė", "vatvalandės", "vatvalandžių", "_f"),
    "kWh": ("kilovatvalandė", "kilovatvalandės", "kilovatvalandžių", "_f"),
    "proc": ("procentas", "procentai", "procentų", ""),
}
# ⛔ 09-04 SĄMONINGAI NEĮTRAUKTI vienaraidžiai: W, A, V, m, g, t, l.
# Roberto nuostata: „pavojingus aplenk, lai geriau keistai skamba negu
# primeluotų kitose vietose." Kiekvienas jų lietuviškame tekste turi antrą
# reikšmę: `V` — romėniškas penketas, `A.` `V.` `W.` — vardų inicialai,
# `g.` — gatvė, `t.` — iš „t. y.", „t. t.". Skaičiaus reikalavimas PRIEŠ
# vienetą daugumą tų atvejų atmeta, bet ne visus: „5 A klasė" virstų
# „penki amperai klasė", „1 t. y." — „viena tona y". Kaina: „2 m" ir „500 g"
# lieka raidėmis. Grąžinti galima bet kada — eilutė lentelėje ir šablone.
VIENETU_SABLONAS = "kWh|kW|Wh|km|kg|cm|mm|ml|ha|proc\\."


def _skaic_forma(n, formos):
    d10, d100 = n % 10, n % 100
    if d10 == 1 and d100 != 11:
        return formos[0]
    if d10 == 0 or 11 <= d100 <= 19:
        return formos[2]
    return formos[1]


# „el. paštas" linksniai (žr. `isplesk` 0−− punktą). Visos formos, išskyrus
# „elektroniniams", yra kirčių žodyne — kirtis ateina iš jo, ne iš espeak.
EL_PASTAS = {"paštas": "elektroninis", "paštu": "elektroniniu",
             "pašto": "elektroninio", "paštą": "elektroninį",
             "pašte": "elektroniniame", "paštai": "elektroniniai",
             "paštus": "elektroninius", "paštų": "elektroninių",
             "paštais": "elektroniniais", "paštams": "elektroniniams"}

MOT_ZODZIAI = r"(valand|dien|minut|savait|sekund|viet|klas|kart(?!ą))"
GAL_VEIKSMAZODZIAI = r"(kainuoja|kainavo|moka|mokėjo|sumokėjo|gavo|gaus|" \
                     r"turi|turėjo|siekia|siekė|sudaro|sudarė|uždirba|uždirbo|" \
                     r"skyrė|skirs|prarado|laimėjo|surinko)"


def isplesk(t):
    # 0−−. „el. paštu" -> „elektroniniu paštu" (Roberto ausis 09-05: „el kai ji
    # tarė girdisi kaip al"). Pamatuota: espeak „el." išplečia į VARDININKĄ ir
    # dar palieka tašką, tad bet koks linksnis skambėdavo „elektroninIS. paštu"
    # — negramatiškai ir su pauze vidury frazės (`ˋeɭektronʲinʲis. paʃˋtu`).
    # ⭐ Forma paimta ne iš galvos: Regina mokymo įraše pati sako „faksu ar
    # elektroniniu paštu" (`_duomenys\regina\metadata.csv`) — modelis tą junginį
    # girdėjo. Būdvardį deriname pagal paties daiktavardžio galūnę.
    def _el_pastas(m):
        vnt = m.group(2)
        zodis = EL_PASTAS.get(vnt.lower(), "elektroninis")
        return (zodis.capitalize() if m.group(1)[0].isupper() else zodis) + " " + vnt
    t = re.sub(r"\b([Ee]l)\.\s*(pašt[a-ząčęėįšųūž]*)", _el_pastas, t)
    # 0−. MATO VIENETAI SU SKAIČIUMI — derinam su skaičiumi.
    # ⚠️ 09-04 (Roberto ausis: „Jarvis-Reginutė skaičius sako blogai"): lentelėje
    # `km` visada virsdavo „kilometrų", tad „12 km" skambėdavo teisingai, o
    # „5 km" → „penki kilometrŲ" ir „100,5 km" → „šimtas kablelis penki
    # kilometrŲ“. Vienetas privalo derintis su PASKUTINIU ištartu skaičiumi
    # (dešimtainėje — su trupmenine dalimi, kaip ir sakom: „devyni kablelis
    # devyniasdešimt devyni eurAI"). Turi eiti PRIEŠ bendrą santrumpų lentelę.
    def _vienetas(m):
        sk, tr, vnt = m.group(1), m.group(2), m.group(3)
        n = int(tr) if tr else int(sk)
        *formos, gim = VIENETAI[vnt.rstrip(".")]
        skaic = (f"{kiekinis(int(sk), 'V', gim)} kablelis "
                 f"{kiekinis(int(tr), 'V', gim)}" if tr
                 else kiekinis(int(sk), "V", gim))
        # „proc." taškas yra santrumpos, bet sakinio gale jis tarnauja ir kaip
        # sakinio galas — o `synth_reginute` pagal jį skaido frazes. Grąžinam.
        liko = m.string[m.end():]
        galas = "." if (vnt.endswith(".") and
                        (not liko.strip() or re.match(r"\s+[A-ZĄČĘĖĮŠŲŪŽ]", liko))) else ""
        return f"{skaic} {_skaic_forma(n, formos)}{galas}"
    t = re.sub(r"\b(\d{1,9})(?:,(\d{1,2}))?\s*(" + VIENETU_SABLONAS +
               r")(?=\s|$|[.,;:!?])", _vienetas, t)
    # 0−b. „5 mln." yra DAUGIKLIS, ne mato vienetas. Lentelėje jis buvo
    # užrakintas vardininku („milijonai"), tad „skirs 5 mln. eurų" virsdavo
    # „skirs penkIS milijonAI eurų" — skaičius galininku, o milijonai ne.
    # ⚠️ 09-04 rasta per Reginos naujienas („Ministerija skirs 5 mln. eurų" —
    # tipiška naujienų frazė). Pavertus tikru skaičiumi, linksnį parenka ta
    # pati `kiekinis`, kuri jau moka visus atvejus.
    t = re.sub(r"\b(\d{1,3})\s*mln\.", lambda m: str(int(m.group(1)) * 1_000_000), t)
    # 0−c. „tūkst." tuo pačiu principu (09-05): lentelėje jos apskritai NEBUVO,
    # tad „skirs 5 tūkst. eurų" nueidavo į fonemizatorių kaip „penkis tūkst.
    # eurų" — su neišplėsta santrumpa vidury frazės. Naujienose ji dažna.
    t = re.sub(r"\b(\d{1,3})\s*tūkst\.", lambda m: str(int(m.group(1)) * 1000), t)
    # ⛔ `mlrd.` SĄMONINGAI nekeičiamas: 4 mlrd. = 4 000 000 000 peržengia
    # `kiekinis` ribą (999 999 999), tad virstų plikais skaitmenimis — blogiau
    # nei palikta santrumpa. Lieka senajai lentelei („milijardai").
    # ⚠️ Ir dar viena riba, žinoma: „skirs 21 mln." duoda „dvidešimt vieną
    # milijonUS" (turėtų būti vienaskaita). Retas atvejis, paliktas sąmoningai.
    # 0. santrumpos
    for r, z in SANTRUMPOS:
        t = re.sub(r, z, t)
    # 0b. RAIDINES santrumpos: 2-5 didziosios is eiles -> raidziu vardai.
    # Tik VIEN didziosios (kad neliestu „Vilnius"), ir ne is eiles su
    # mazosiomis (kad „ESU" sakinio pradzioje neliktu perkirstas).
    t = re.sub(r"\b[A-ZĄČĘĖĮŠŲŪŽ]{2,5}\b", raidem, t)
    # raidžių brūkšnelių valymas: dvigubi -> vienas; prieš skyrybą ir
    # eilutės galuose -> lauk (kad neliktų „… - ." ar „- em")
    t = re.sub(r"(?:\s*-\s*){2,}", " - ", t)
    t = re.sub(r"\s*-\s*(?=[.,:;!?])", "", t)
    t = re.sub(r"\s*-\s*$", "", t, flags=re.MULTILINE)
    t = re.sub(r"^\s*-\s*", "", t, flags=re.MULTILINE)
    # 0c. KAINA: „9,99 Eur" -> „devyni eurai devyniasdešimt devyni centai".
    # Turi eiti PRIEŠ bendrą kablelio taisyklę, kitaip liktų „kablelis".
    # (0 punkte `Eur` jau paverstas į „ eurų", tad gaudom ir tą formą.)
    def _kaina(m):
        e, c = int(m.group(1)), int(m.group(2))
        pries = (m.string[:m.start()].rstrip().split() or [""])[-1].lower()
        kilm = pries in ("nuo", "iki", "ligi")
        f = "K" if kilm else "V"
        dalys = [kiekinis(e, f), EURAI[2] if kilm else _skaic_forma(e, EURAI)]
        if c:
            dalys += [kiekinis(c, f), CENTAI[2] if kilm else _skaic_forma(c, CENTAI)]
        return " ".join(dalys)
    t = re.sub(r"\b(\d+),(\d{1,2})\s*(?:Eur\b|eurų|eurai|euro|euru|€)", _kaina, t)
    # 0d. Dešimtainis kablelis: „9,99" -> „devyni kablelis devyniasdešimt devyni".
    # ⚠️ 09-04 (Roberto ausis, Reginos paieška): be šito „9,99 Eur" virsdavo
    # „devyni,devyniasdešimt devyni eurų" — kablelis likdavo tarp žodžių ir
    # skambėdavo kaip vienas suklijuotas žodis. Turi eiti PRIEŠ visas skaičių
    # taisykles, kitaip jos abi puses apdoroja atskirai.
    t = re.sub(r"\b(\d+),(\d{1,2})\b",
               lambda m: f"{kiekinis(int(m.group(1)))} kablelis "
                         f"{kiekinis(int(m.group(2)))}", t)
    # 1. HH:MM -> „penkiolika trisdešimt" (0 min -> tik valanda kelintiniu)
    # ⚠️ 09-04 PATAISA (Roberto ausis: „skaičius valandą supasakojo be linksnių"):
    # po „nuo"/„iki"/„ligi" lietuviškai reikia KILMININKO — „nuo aštuntos
    # valandos", ne „nuo aštuntą valandą". Anksčiau visada buvo galininkas,
    # todėl parduotuvės darbo laikas skambėjo negramatiškai.
    NUO_IKI = ("nuo", "iki", "ligi")

    def _laikas(m):
        h, mi = int(m.group(1)), int(m.group(2))
        pries = (m.string[:m.start()].rstrip().split() or [""])[-1].lower()
        kilm = pries in NUO_IKI
        if mi == 0:
            return (kelintinis(h, "f", "K") + " valandos" if kilm
                    else kelintinis(h, "f", "G") + " valandą")
        val = kiekinis(h, "K") if kilm else kiekinis(h)
        return val + " " + (kiekinis(mi) if mi > 9 else "nulis " + kiekinis(mi))
    t = re.sub(r"\b(\d{1,2}):(\d{2})\b", _laikas, t)
    # 2. metai kelintiniu įnag.: 2015 metais / 2015 m.
    t = re.sub(r"\b(1\d{3}|2\d{3})\s*(m\.|metais)\b",
               lambda m: kelintinis(int(m.group(1)), "m", "Idgs") + " metais", t)
    t = re.sub(r"\b(1\d{3}|2\d{3})\s*metų\b",
               lambda m: kelintinis(int(m.group(1)), "m", "Kdgs") + " metų", t)
    t = re.sub(r"\b(1\d{3}|2\d{3})-(ai|ų|į)?[a-zų]*\b",
               lambda m: kelintinis(int(m.group(1)), "m", "Idgs", ivardz=True), t)
    # 3. mot. giminės galininkas: „15 valandą/vietą/klasę" -> kelintinė
    t = re.sub(r"\b(\d{1,3})\s+(" + MOT_ZODZIAI + r"[ąę])",
               lambda m: kelintinis(int(m.group(1)), "f", "G") + " " + m.group(2), t)
    # 3b. vyr. kelintinis G: „23 kartą" -> „dvidešimt trečią kartą"
    t = re.sub(r"\b(\d{1,3})\s+(kartą|numerį|aukštą|etapą|turą|sezoną|puslapį)\b",
               lambda m: kelintinis(int(m.group(1)), "m", "G") + " " + m.group(2), t)
    # 4. mot. kiekiniai: „2 valandas/dienas" -> „dvi valandas"
    t = re.sub(r"\b(\d{1,4})\s+(" + MOT_ZODZIAI + r"(as|os|es|ių|ę))",
               lambda m: kiekinis(int(m.group(1)),
                                  "G" if m.group(2).endswith(("as", "es", "ę")) else "V",
                                  "_f") + " " + m.group(2), t)
    # 5. galininkas po veiksmažodžio: „kainuoja 25 eurus"
    t = re.sub(GAL_VEIKSMAZODZIAI + r"\s+(\d{1,9})\b",
               lambda m: m.group(1) + " " + kiekinis(int(m.group(2)), "G"), t)
    # 6. vyriškas galininkas su daiktavardžiu: „3 mėnesius/eurus/kartus"
    t = re.sub(r"\b(\d{1,9})\s+([a-ząčęėįšųūž]+(?:us|į|ą))\b",
               lambda m: kiekinis(int(m.group(1)), "G") + " " + m.group(2), t)
    # 6b. KILMININKINIAI PRIELINKSNIAI (09-05, RADINIAI 29c): „nuo 2000 eurų"
    # duodavo „nuo du tūkstančiai eurų". Laikui po „nuo/iki" kilmininkas jau
    # buvo daromas (`_laikas`), o bendram skaičiui — ne.
    # ⛔ Sąrašas SĄMONINGAI trumpas — tik tie, po kurių kilmininkas VISADA:
    # „po" dviprasmis („po du" prieš „po dviejų valandų"), o „už, per, prieš,
    # apie" reikalauja galininko. Roberto nuostata ta pati kaip su vienetais:
    # pavojingus aplenk, lai geriau keistai skamba negu primeluotų.
    t = re.sub(r"\b(nuo|iki|ligi|be|dėl|iš|tarp|virš|šalia|arti)\s+(\d{1,9})\b",
               lambda m: m.group(1) + " " + kiekinis(int(m.group(2)), "K"), t)
    # 7. „minus N" temperatūrai jau natūralu; likę skaičiai -> V
    t = re.sub(r"\b\d{1,9}\b", lambda m: kiekinis(int(m.group(0))), t)
    return re.sub(r"\s{2,}", " ", t)


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    testai = [
        "dar 2015 metais priimto sprendimo",
        "1998 metų sausį", "2026-aisiais",
        "ilgiau kaip 3 mėnesius iš eilės",
        "susitiksim 15:00, o vakarienė 19:30",
        "užėmė 3 vietą, o 2 valandas laukė",
        "kainuoja 25 eurus, o bauda siekia 150 Eur",
        "mieste gyvena 2 mln. žmonių, tai 45 proc.",
        "nuvažiavo 12 km ir nešė 80 kg",
        "temperatūra minus 5 laipsniai",
        "gavo 1234567 eurų palikimą",
        "jau 23 kartą laimėjo 7 vietą",
    ]
    for x in testai:
        print(f"{x:44s} -> {isplesk(x)}")
