cd ~/Documents/free_work/urdu-reading-course/.audit/improve/a_robust/verifier_r2
export BASE=http://localhost:5371/
for f in z1_tabdup_teacher y1_place u1_deadbtn t1_share s1_recovery q1_atomic p2_versionchange p1_dbvariants w1_pin v1_start; do
  timeout 400 python3 $f.py > ../verifier_r3/r2out/$f.out 2>&1; echo "$f rc=$?" >> ../verifier_r3/r2out/_status2
done
