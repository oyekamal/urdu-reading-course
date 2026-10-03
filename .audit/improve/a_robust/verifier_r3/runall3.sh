cd ~/Documents/free_work/urdu-reading-course/.audit/improve/a_robust/verifier_r2
export BASE=http://localhost:5371/
for f in o3_csv o2_inputs o1_names n1_roundtrip m1_restorebust k1_finishfail i3_unlocked i2_read i1_gate l1_ids; do
  timeout 400 python3 $f.py > ../verifier_r3/r2out/$f.out 2>&1; echo "$f rc=$?" >> ../verifier_r3/r2out/_status3
done
