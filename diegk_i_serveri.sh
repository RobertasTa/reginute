#!/usr/bin/env bash
# DIEGIMAS Į SERVERĮ IŠ PAKETO — LXC 214 (Roberto namai) arba bet kuris kitas.
#
# Principas (PIPER_PATEIKIMO_PLANAS 9 sk.): į serverį keliauja TIKSLIAI tas
# failų rinkinys, kuris keliaus į HF — `hf/` + modulis. Kas išbandyta, tas
# išsiunčiama. SHA256 tikrinamas konteineryje prieš perjungiant tarnybą.
#
# Ką keičia serveryje: įkelia failus į /opt/reginute (senų NETRINA — atšaukimas
# = grąžinti dvi tarnybos eilutes), tarnybos faile pakeičia TIK --model ir
# --config kelius, perleidžia wyoming-reginute. Balso vardo (reginute1),
# porto (10250), tempo (--length-scale) NELIEČIA.
#
# Naudojimas (Git Bash Windows'e, iš piper_lt katalogo):
#   bash diegk_i_serveri.sh              # LXC 214 per Proxmox host'ą
#   HOST=root@kitas CT=999 bash diegk_i_serveri.sh
set -euo pipefail
HOST="${HOST:-root@192.168.0.95}"
CT="${CT:-214}"
TIKSLAS="${TIKSLAS:-/opt/reginute}"
CIA="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VARDAS="lt_LT-reginute1-medium"
TMP="/tmp/reginute_pkg"

FAILAI=(
  "hf/$VARDAS.onnx"
  "hf/$VARDAS.onnx.json"
  "hf/SHA256SUMS"
  "phonemize_lithuanian.py"
  "lt_kirciai.tsv"
  "zodziai_trumpi.txt"
  "synth_reginute.py"
  "wyoming_reginute.py"
  "skaiciu_pletiklis.py"
)

echo "== 1. Paketo failai (vietoje):"
for f in "${FAILAI[@]}"; do
  [ -f "$CIA/$f" ] || { echo "TRŪKSTA: $f"; exit 1; }
  awk -v f="$f" -v b="$(stat -c%s "$CIA/$f")" 'BEGIN{printf "   %-34s %8.2f MB\n", f, b/1048576}'
done

echo "== 2. Keliu į $HOST:$TMP"
ssh "$HOST" "mkdir -p $TMP"
for f in "${FAILAI[@]}"; do scp -q "$CIA/$f" "$HOST:$TMP/$(basename "$f")"; done

echo "== 3. Į konteinerį $CT:$TIKSLAS (pct push)"
for f in "${FAILAI[@]}"; do
  b="$(basename "$f")"
  ssh "$HOST" "pct push $CT $TMP/$b $TIKSLAS/$b" >/dev/null
done

echo "== 4. SHA256 konteineryje (hf/ failai prieš SHA256SUMS):"
# Only the two files that travel here: the .ckpt is in SHA256SUMS too (HF gets
# it), but the server does not - found 09-06 when the check tripped over it.
ssh "$HOST" "pct exec $CT -- bash -c 'cd $TIKSLAS && grep -E \"$VARDAS\.onnx(\.json)?\$\" SHA256SUMS | sha256sum -c -'"

echo "== 5. Tarnyba: keičiu TIK --model ir --config"
ssh "$HOST" "pct exec $CT -- bash -c '
  U=/etc/systemd/system/wyoming-reginute.service
  cp -n \$U \$U.pries_$(date +%Y%m%d) || true
  sed -i -E \"s#--model +[^ ]+#--model $TIKSLAS/$VARDAS.onnx#; s#--config +[^ ]+#--config $TIKSLAS/$VARDAS.onnx.json#\" \$U
  grep -o -- \"--model [^ ]*\|--config [^ ]*\|--length-scale [^ ]*\" \$U
  systemctl daemon-reload && systemctl restart wyoming-reginute && sleep 3
  systemctl is-active wyoming-reginute
  journalctl -u wyoming-reginute -n 5 --no-pager | tail -3
'"
echo "== Baigta. Egzaminas B: testas_wyoming_klientas.py tcp://192.168.0.220:10250"
