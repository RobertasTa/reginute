# Wyoming TTS server for Reginutė and Ingutė - the self-hosted path, for
# running the voices without waiting for anything to be merged upstream. It
# does what wyoming-piper does, with the Lithuanian phonemizer in front of the
# model; the voice config uses phoneme_type = "text" (the config from the
# voice's GitHub repo, not the one from the Piper catalogue).
#
# Home Assistant sees it as any other Wyoming TTS service (Settings →
# Integrations → Wyoming → host:port). It runs beside an existing
# wyoming-piper on a DIFFERENT port, so nothing already working is touched.
# Synthesis runs on the CPU (onnxruntime); a 2-core container on a Ryzen mini
# PC makes 16 s of speech in 1.8 s.
#
# Usage (speed and voice name come from the model and its config):
#   python3 wyoming_reginute.py --model lt_LT-ingute-medium.onnx --uri tcp://0.0.0.0:10250
#   python3 wyoming_reginute.py --model lt_LT-reginute1-medium.onnx --uri tcp://0.0.0.0:10251
#   [--config X.onnx.json] [--dictionary lt_kirciai.tsv] [--length-scale N] [--voice-name N]
# Requires: pip install piper-tts wyoming
import argparse
import asyncio
import json
import logging
import os
import re
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
    # The speed each voice was listened to and approved at lives in its own
    # config (inference.length_scale): Reginutė 1.30, Ingutė 1.15. This used to
    # default to 1.30 for every voice, so Ingutė run without the flag spoke at
    # her sister's slower pace - stretched, and more robotic than she is.
    p.add_argument("--length-scale", type=float, default=None,
                   help="tempas; numatyta: iš balso konfigo (Reginutė 1.30, Ingutė 1.15)")
    p.add_argument("--kablelis", type=float, default=0.25, help="pauzė po kablelio, s")
    p.add_argument("--taskas", type=float, default=0.15, help="pauzė po taško, s")
    p.add_argument("--kableli-skaidyti", action="store_true",
                   help="skaidyti ir ties kableliu (numatyta: kablelį tvarko pats modelis)")
    p.add_argument("--santrumpu-letumas", type=float, default=1.15,
                   help="kiek lėčiau tarti raidines santrumpas (1.0 = kaip kalbą)")
    p.add_argument("--min-zodziu", type=int, default=0,
                   help="ties kableliu skaidyti tik kai abi pusės >= N žodžių (0 = visada)")
    p.add_argument("--voice-name", default=None,
                   help="balso vardas Home Assistant'e; numatyta: iš modelio failo (reginute1, ingute)")
    p.add_argument("--no-expand", action="store_true",
                   help="neplėsti skaičių/santrumpų (palikti espeak'ui)")
    p.add_argument("--debug", action="store_true")
    args = p.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    config_path = args.config or args.model + ".json"
    with open(config_path, encoding="utf-8") as f:
        phoneme_type = json.load(f).get("phoneme_type")
    if phoneme_type != "text":
        # The official Piper catalogue ships these voices with
        # phoneme_type "lithuanian" (for Piper >= 1.9.0, which phonemizes
        # itself); piper-tts 1.8.0 cannot even parse that, and fails cryptically.
        raise SystemExit(
            f"{config_path}: phoneme_type={phoneme_type!r}, šiam serveriui reikia \"text\" "
            "(fonemas duodam mes). Imkite .onnx.json iš balso GitHub repo "
            "(github.com/RobertasTa/ingute arba /reginute), ne iš Piper katalogo.")
    voice = PiperVoice.load(args.model, config_path=config_path)
    length_scale = args.length_scale if args.length_scale is not None else voice.config.length_scale
    voice_name = args.voice_name or re.sub(
        r"-(x_low|low|medium|high)$", "", re.sub(r"^[a-z]{2,3}_[A-Z]{2}-", "", os.path.basename(args.model)[:-5]))
    expand = None if (args.no_expand or _isplesk is None) else _isplesk
    phonemizer = LithuanianPhonemizer(dictionary_path=args.dictionary)
    synth = ReginuteSynth(voice, phonemizer, length_scale=length_scale,
                          kablelis=args.kablelis, taskas=args.taskas, expand_text=expand,
                          min_zodziu=args.min_zodziu,
                          santrumpu_letumas=args.santrumpu_letumas,
                          kableli_skaidyti=args.kableli_skaidyti)

    info = Info(tts=[TtsProgram(
        name="reginute", description="Lietuviškas Piper balsas su priegaidėmis (Reginutė / Ingutė)",
        attribution=Attribution(name="liepa-tts / Vilnius University (CC-BY-4.0)",
                                url="https://huggingface.co/meldynamics/liepa-tts"),
        installed=True, version="0.1",
        voices=[TtsVoice(
            name=voice_name, description=f"{voice_name} ({synth.sr} Hz, length_scale {length_scale})",
            attribution=Attribution(name="liepa-tts", url="https://huggingface.co/meldynamics/liepa-tts"),
            installed=True, version="0.1", languages=["lt", "lt_LT", "lt-LT"])])])

    server = AsyncServer.from_uri(args.uri)
    _LOGGER.info("%s klauso %s (tempas %s%s, plėtiklis: %s)", voice_name, args.uri, length_scale,
                 "" if args.length_scale is not None else " iš konfigo", "taip" if expand else "ne")
    await server.run(partial(ReginuteHandler, info, synth))


if __name__ == "__main__":
    asyncio.run(main())
