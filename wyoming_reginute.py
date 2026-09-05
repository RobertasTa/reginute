# WYOMING TTS SERVERIS REGINUTEI — „savasis" kelias (Roberto: „jei nepriims,
# į savąjį tupdyti turėsim"). Tas pats, ką daro wyoming-piper, tik prieš
# balsą įjungtas mūsų fonemizatorius; balso config phoneme_type = "text".
# Home Assistant jį mato kaip bet kurį Wyoming TTS (Settings → Integrations →
# Wyoming → host:port). Skirta LXC 214 (šalia esamo wyoming-piper, KITAS portas).
#
# Paleidimas:
#   python3 wyoming_reginute.py --model lt_LT-reginute1-medium.onnx \
#       --config lt_LT-reginute1-medium.onnx.json --uri tcp://0.0.0.0:10250 \
#       [--dictionary lt_kirciai.tsv] [--length-scale 1.30]
# Priklausomybės: pip install piper-tts wyoming
import argparse
import asyncio
import logging
import os
import sys
from functools import partial

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from phonemize_lithuanian import DEFAULT_DICTIONARY_PATH, LithuanianPhonemizer
from synth_reginute import ReginuteSynth, i_int16
from piper import PiperVoice
from wyoming.audio import AudioChunk, AudioStart, AudioStop
from wyoming.event import Event
from wyoming.info import Attribution, Describe, Info, TtsProgram, TtsVoice
from wyoming.server import AsyncEventHandler, AsyncServer
from wyoming.tts import Synthesize

_LOGGER = logging.getLogger("wyoming_reginute")

try:  # skaičių/santrumpų plėtiklis — jei yra šalia, naudojam
    from skaiciu_pletiklis import isplesk as _isplesk
except Exception:  # pragma: no cover
    _isplesk = None


class ReginuteHandler(AsyncEventHandler):
    def __init__(self, info: Info, synth: ReginuteSynth, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.info = info
        self.synth = synth

    async def handle_event(self, event: Event) -> bool:
        if Describe.is_type(event.type):
            await self.write_event(self.info.event())
            return True
        if not Synthesize.is_type(event.type):
            return True

        synth = Synthesize.from_event(event)
        text = " ".join(synth.text.split())
        _LOGGER.debug("Tekstas: %s", text)

        sr = self.synth.sr
        await self.write_event(AudioStart(rate=sr, width=2, channels=1).event())
        for gabalas in self.synth.gabalai(text):
            await self.write_event(AudioChunk(
                audio=i_int16(gabalas), rate=sr, width=2, channels=1).event())
        await self.write_event(AudioStop().event())
        return True


async def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("--config", default=None, help="numatyta: MODEL + .json")
    p.add_argument("--dictionary", default=str(DEFAULT_DICTIONARY_PATH))
    p.add_argument("--uri", default="tcp://0.0.0.0:10250")
    # 09-05: buvo 1.25, nors 09-04 sutarta 1.30 VISUR. Roberto serverio tarnyba
    # tempą nurodo aiškiai, tad ten nieko nekeičia — bet svetimas žmogus,
    # paleidęs be argumento, būtų gavęs kitą balsą nei tas, kurį vertinom.
    p.add_argument("--length-scale", type=float, default=1.30)
    p.add_argument("--kablelis", type=float, default=0.25, help="pauzė po kablelio, s")
    p.add_argument("--taskas", type=float, default=0.15, help="pauzė po taško, s")
    p.add_argument("--kableli-skaidyti", action="store_true",
                   help="skaidyti ir ties kableliu (numatyta: kablelį tvarko pats modelis)")
    p.add_argument("--santrumpu-letumas", type=float, default=1.15,
                   help="kiek lėčiau tarti raidines santrumpas (1.0 = kaip kalbą)")
    p.add_argument("--min-zodziu", type=int, default=0,
                   help="ties kableliu skaidyti tik kai abi pusės >= N žodžių (0 = visada)")
    p.add_argument("--voice-name", default="reginute1")
    p.add_argument("--no-expand", action="store_true",
                   help="neplėsti skaičių/santrumpų (palikti espeak'ui)")
    p.add_argument("--debug", action="store_true")
    args = p.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    voice = PiperVoice.load(args.model, config_path=args.config)
    if voice.config.phoneme_type.value != "text":
        raise SystemExit("Balso config turi būti phoneme_type=text (fonemas duodam mes)")
    expand = None if (args.no_expand or _isplesk is None) else _isplesk
    phonemizer = LithuanianPhonemizer(dictionary_path=args.dictionary)
    synth = ReginuteSynth(voice, phonemizer, length_scale=args.length_scale,
                          kablelis=args.kablelis, taskas=args.taskas, expand_text=expand,
                          min_zodziu=args.min_zodziu,
                          santrumpu_letumas=args.santrumpu_letumas,
                          kableli_skaidyti=args.kableli_skaidyti)

    info = Info(tts=[TtsProgram(
        name="reginute", description="Reginutė — lietuviškas Piper balsas su priegaidėmis",
        attribution=Attribution(name="liepa-tts / Regina Jokubauskaitė (CC-BY-4.0)",
                                url="https://huggingface.co/meldynamics/liepa-tts"),
        installed=True, version="0.1",
        voices=[TtsVoice(
            name=args.voice_name, description="Reginutė (medium, 22050 Hz)",
            attribution=Attribution(name="liepa-tts", url="https://huggingface.co/meldynamics/liepa-tts"),
            installed=True, version="0.1", languages=["lt", "lt_LT", "lt-LT"])])])

    server = AsyncServer.from_uri(args.uri)
    _LOGGER.info("Reginutė klauso %s (plėtiklis: %s)", args.uri, "taip" if expand else "ne")
    await server.run(partial(ReginuteHandler, info, synth))


if __name__ == "__main__":
    asyncio.run(main())
