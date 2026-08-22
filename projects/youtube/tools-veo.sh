#!/bin/bash
# Generowanie B-rolla przez Veo 3.1 (Gemini API).
#   ./tools-veo.sh <slug> "<prompt>" [model] [sekundy]
# Model: fast (domyslny) | lite | pro
set -e
KEY=$(python3 -c "print(open('$HOME/Repo/Gemini_API').read().split('=',1)[1].strip())")
SLUG="$1"; PROMPT="$2"; TIER="${3:-fast}"; SEC="${4:-8}"; RES="${5:-1080p}"
case "$TIER" in
  pro)  M="veo-3.1-generate-preview" ;;
  lite) M="veo-3.1-lite-generate-preview" ;;
  *)    M="veo-3.1-fast-generate-preview" ;;
esac
OUT="$(dirname "$0")/assets/broll-gemini"; mkdir -p "$OUT"
echo "model: $M | $SEC s | $RES | $SLUG"
# UWAGA: 1080p dziala tylko przy 8 s — przy 4 i 6 s API odrzuca zadanie.
REQ=$(python3 -c "
import json,sys
print(json.dumps({'instances':[{'prompt':sys.argv[1]}],
 'parameters':{'aspectRatio':'16:9','durationSeconds':int(sys.argv[2]),'resolution':sys.argv[3]}}))
" "$PROMPT" "$SEC" "$RES")
OP=$(curl -s -X POST "https://generativelanguage.googleapis.com/v1beta/models/$M:predictLongRunning?key=$KEY" \
  -H 'Content-Type: application/json' -d "$REQ" | python3 -c "
import sys,json; d=json.load(sys.stdin)
if 'error' in d: print('ERR:'+d['error'].get('message','')[:200]); raise SystemExit
print(d.get('name',''))")
case "$OP" in ERR:*) echo "  ${OP#ERR:}"; exit 1;; "") echo "  brak nazwy operacji"; exit 1;; esac
echo "  operacja: ${OP##*/}"
for i in $(seq 1 60); do
  sleep 10
  R=$(curl -s "https://generativelanguage.googleapis.com/v1beta/$OP?key=$KEY")
  D=$(echo "$R" | python3 -c "
import sys,json; d=json.load(sys.stdin)
if d.get('done'):
    if 'error' in d: print('ERR:'+str(d['error'])[:200])
    else:
        try:
            v=d['response']['generateVideoResponse']['generatedSamples'][0]['video']['uri']; print('URI:'+v)
        except Exception: print('RAW:'+json.dumps(d['response'])[:300])
else: print('WAIT')")
  case "$D" in
    URI:*) curl -s -L "${D#URI:}&key=$KEY" -o "$OUT/$SLUG.mp4"; echo "  gotowe → assets/broll-gemini/$SLUG.mp4"; exit 0;;
    ERR:*) echo "  ${D#ERR:}"; exit 1;;
    RAW:*) echo "  nieoczekiwana odpowiedz: ${D#RAW:}"; exit 1;;
  esac
  printf "  czekam %ss\r" $((i*10))
done
echo "  przekroczono czas"; exit 1
