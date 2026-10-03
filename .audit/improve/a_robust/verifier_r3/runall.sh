cd ~/Documents/free_work/urdu-reading-course/.audit/improve/a_robust/verifier_r2
export BASE=http://localhost:5371/
for f in a1_csp b1_tabs b2_tabs2 c1_dbfail c2_dbfail2 d1_taps e1_malformed f1_onb_burst f2_plan_burst f3_plan_dbl g1_backup h1_flows h2_flows i1_gate i2_read i3_unlocked j1_xss k1_finishfail m1_restorebust n1_roundtrip o1_names o2_inputs o3_csv p1_dbvariants p2_versionchange q1_atomic r1_fastkid s1_recovery t1_share u1_deadbtn v1_start w1_pin x1_bigimport y1_place z1_tabdup_teacher l1_ids; do
  timeout 300 python3 $f.py > ../verifier_r3/r2out/$f.out 2>&1; echo "$f rc=$?" >> ../verifier_r3/r2out/_status
done
