# Strip a training checkpoint down to what another person can use, so that the
# next Lithuanian voice can start from this one instead of from a Russian
# checkpoint - which is where this one had to start.
#
# The Piper catalogue keeps a PyTorch checkpoint beside each voice
# (rhasspy/piper-checkpoints). Without it a voice can only be USED; with it,
# it can be continued.
#
# Removed:
#   optimizer_states  537 MB - Adam moments, useful only for resuming this
#                     exact run on this exact machine; worthless to anyone else
#   loops/callbacks/lr_schedulers - Lightning's own bookkeeping
# Kept:
#   state_dict (model_g 90 MB + model_d 178 MB) - both the generator AND the
#     discriminator: a GAN needs both to continue training, and continuing is
#     the entire point of this file
#   hyper_parameters - without them Piper cannot tell what architecture was
#     trained
#
#   python svarus_checkpoint.py
#   python svarus_checkpoint.py --ckpt <path>   (default: best by val_mel)
import argparse
import glob
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

BAZE = r"D:\_Balsas Lietuviksas"
VARDAS = "lt_LT-reginute1-medium"
NUIMAM = ("optimizer_states", "loops", "callbacks", "lr_schedulers")


def geriausias_ckpt():
    k = []
    for kelias in glob.glob(os.path.join(BAZE, "lightning_logs", "version_*",
                                         "checkpoints", "epoch=*val_mel=*.ckpt")):
        m = re.search(r"epoch=(\d+)-val_mel=(\d+\.\d+)\.ckpt$", os.path.basename(kelias))
        if m:
            k.append((float(m.group(2)), int(m.group(1)), kelias))
    return sorted(k)[0] if k else None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ckpt", help="a specific checkpoint (default: best by val_mel)")
    p.add_argument("--output", "--isvestis", dest="isvestis",
                   default=os.path.join(BAZE, "_irankiai", "piper_lt", "hf"),
                   help="where to write the stripped checkpoint")
    args = p.parse_args()

    import torch

    if args.ckpt:
        kelias, aprasas = os.path.abspath(args.ckpt), "given on the command line"
        e = int(re.search(r"epoch=(\d+)", os.path.basename(kelias)).group(1))
        val = float(re.search(r"val_mel=(\d+\.\d+)", os.path.basename(kelias)).group(1))
    else:
        g = geriausias_ckpt()
        if not g:
            raise SystemExit("No checkpoints found")
        val, e, kelias = g
        aprasas = "best by val_mel"

    print(f"Using: {os.path.basename(kelias)} ({aprasas})")
    ck = torch.load(kelias, map_location="cpu", weights_only=False)

    svarus = {k: v for k, v in ck.items() if k not in NUIMAM}
    isv = os.path.join(args.isvestis, f"{VARDAS}-e{e}.ckpt")
    os.makedirs(args.isvestis, exist_ok=True)
    torch.save(svarus, isv)

    buvo = os.path.getsize(kelias) / 1048576
    liko = os.path.getsize(isv) / 1048576
    print(f"Removed: {', '.join(NUIMAM)}")
    print(f"{buvo:.0f} MB -> {liko:.0f} MB   ({isv})")

    # Verify: the file must open again, with the weights still in it.
    t = torch.load(isv, map_location="cpu", weights_only=False)
    sd = t.get("state_dict", {})
    g_yra = sum(1 for k in sd if k.startswith("model_g"))
    d_yra = sum(1 for k in sd if k.startswith("model_d"))
    print(f"Check: state_dict {len(sd)} tensors (model_g {g_yra}, model_d {d_yra}), "
          f"hyper_parameters {'yes' if 'hyper_parameters' in t else 'MISSING'}, "
          f"epoch {t.get('epoch')}")
    if not g_yra or "hyper_parameters" not in t:
        raise SystemExit("Verification failed - DO NOT ship this file")
    print(f"val_mel {val:.4f} - record it in MODEL_CARD together with epoch {e}")


if __name__ == "__main__":
    main()
