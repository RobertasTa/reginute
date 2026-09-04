# Wyoming kliento testas: Describe -> Info, Synthesize -> WAV. Tikrina, kad
# wyoming_reginute.py kalba protokolu taip, kaip jo laukia Home Assistant.
#   _darbal\pw_venv\Scripts\python.exe _irankiai\piper_lt\testas_wyoming_klientas.py tcp://127.0.0.1:10250 "tekstas" out.wav
import asyncio
import sys
import wave

from wyoming.audio import AudioChunk, AudioStart, AudioStop
from wyoming.client import AsyncClient
from wyoming.info import Describe, Info
from wyoming.tts import Synthesize

sys.stdout.reconfigure(encoding="utf-8")
uri, tekstas, isvestis = sys.argv[1:4]


async def main():
    async with AsyncClient.from_uri(uri) as c:
        await c.write_event(Describe().event())
        ev = await c.read_event()
        assert Info.is_type(ev.type), ev.type
        info = Info.from_event(ev)
        for t in info.tts:
            print("TTS:", t.name, "|", t.description, "| balsai:",
                  [(v.name, v.languages) for v in t.voices])

        await c.write_event(Synthesize(text=tekstas).event())
        w = None
        frames = 0
        while True:
            ev = await c.read_event()
            if ev is None:
                raise SystemExit("ryšys nutrūko")
            if AudioStart.is_type(ev.type):
                a = AudioStart.from_event(ev)
                w = wave.open(isvestis, "wb")
                w.setnchannels(a.channels); w.setsampwidth(a.width); w.setframerate(a.rate)
                rate = a.rate
            elif AudioChunk.is_type(ev.type):
                ch = AudioChunk.from_event(ev)
                w.writeframes(ch.audio)
                frames += len(ch.audio) // 2
            elif AudioStop.is_type(ev.type):
                break
        w.close()
        print(f"WAV {isvestis}: {frames/rate:.1f} s")


asyncio.run(main())
