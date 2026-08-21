#!/usr/bin/env bash
# Baixa o dataset pNEUMA (open-traffic.epfl.ch) para as regioes d2-d10,
# nas mesmas datas/horarios ja presentes para d1.
set -uo pipefail

cd "$(dirname "$0")"

DRONES="d2 d3 d4 d5 d6 d7 d8 d9 d10"
DATES="20181024 20181029 20181030 20181101"
TIMES="0830_0900 0900_0930 0930_1000 1000_1030"

URL="https://open-traffic.epfl.ch/wp-content/uploads/mydownloads.php"
LOG="download_pneuma.log"

total=0
ok=0
fail=0

for d in $DRONES; do
  for date in $DATES; do
    for t in $TIMES; do
      out="${date}_${d}_${t}.csv"
      total=$((total+1))
      if [ -s "$out" ]; then
        echo "[skip] $out ja existe" | tee -a "$LOG"
        ok=$((ok+1))
        continue
      fi

      tmp="${out}.part"
      attempt=0
      success=0
      while [ $attempt -lt 5 ]; do
        attempt=$((attempt+1))
        code=$(curl -sS -A "Mozilla/5.0" -X POST "$URL" \
          --data-urlencode "fpLocation=${d}" \
          --data-urlencode "fpDate=${date}" \
          --data-urlencode "fpTime=${t}" \
          -o "$tmp" -w "%{http_code}")
        if [ "$code" = "200" ] && [ -s "$tmp" ]; then
          mv "$tmp" "$out"
          echo "[ok] $out ($(du -h "$out" | cut -f1))" | tee -a "$LOG"
          success=1
          break
        else
          echo "[retry $attempt] $out falhou (http $code)" | tee -a "$LOG"
          sleep 3
        fi
      done

      if [ $success -eq 1 ]; then
        ok=$((ok+1))
      else
        fail=$((fail+1))
        echo "[fail] $out desistindo apos $attempt tentativas" | tee -a "$LOG"
      fi
    done
  done
done

echo "Concluido: $ok/$total ok, $fail falhas" | tee -a "$LOG"
