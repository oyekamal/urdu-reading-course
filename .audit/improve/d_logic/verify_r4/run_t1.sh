#!/bin/bash
export PORT=5530
cd "$(dirname "$0")"
for st in naskh nastaliq; do
  for c in ابکلم ٹثورد زژفقخ طظذئ غعحصض گںھڈڑ نتیےپ ہسشجچ; do
    python3 t1.py $st $c > o_t1_${st}_$c.log 2>&1 &
    sleep 3
  done
  wait
done
echo ALLDONE > o_t1_done.txt
