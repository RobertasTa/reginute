# ĮRODYMAS GALAS Į GALĄ: mūsų modulis + IŠLEISTAS piper-tts ratas (1.7.0, be
# jokių mūsų lopų) + Reginutės ONNX -> WAV. Tai lygiai ta grandinė, kurią
# gautų „grynas Piper" vartotojas, kol PR dar nesulietas: balsas su
# phoneme_type "text", o priekyje — phonemize_lithuanian + synth_reginute
# (pauzės ir tylos kirpimas kaip kadruose, BE piper normalizacijos).
# Leisti su piper-tts ratu:
#   _darbal\pw_venv\Scripts\python.exe _irankiai\piper_lt\demo_piper_wheel.py ONNX JSON "tekstas" out.wav [tempas]
import os
import sys
import time
import wave

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from phonemize_lithuanian import LithuanianPhonemizer
from synth_reginute import ReginuteSynth, i_int16
from piper import PiperVoice

try:
    from skaiciu_pletiklis import isplesk
except Exception:
    isplesk = None

onnx, cfg, tekstas, isvestis = sys.argv[1:5]
tempas = float(sys.argv[5]) if len(sys.argv) > 5 else 1.25
min_zodziu = int(sys.argv[6]) if len(sys.argv) > 6 else 0   # 0 = kablelį skaidyti visada

voice = PiperVoice.load(onnx, config_path=cfg)
assert voice.config.phoneme_type.value == "text", voice.config.phoneme_type
letumas = float(sys.argv[7]) if len(sys.argv) > 7 else 1.15   # santrumpų lėtumas
synth = ReginuteSynth(voice, LithuanianPhonemizer(), length_scale=tempas,
                      expand_text=isplesk, min_zodziu=min_zodziu,
                      santrumpu_letumas=letumas)

t0 = time.time()
garsas = synth.synthesize(tekstas)
trukme = time.time() - t0
with wave.open(isvestis, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(synth.sr)
    w.writeframes(i_int16(garsas))
print(f"WAV: {isvestis}  garso {len(garsas)/synth.sr:.1f} s, sintezė {trukme:.1f} s, "
      f"plėtiklis: {'taip' if isplesk else 'ne'}")
print("GABALAI (tekstas | trukmė | garsumas):")
for frag, trukme_s, rms in synth.zurnalas:
    print(f"  {trukme_s:5.2f} s  {rms:6.1f} dB  {frag[:70]}")
