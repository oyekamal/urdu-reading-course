#!/bin/sh
cd /home/oye/Documents/free_work/urdu-reading-course/.audit/improve/b_a11y
R="python3 -u walk.py --port 5199"
$R --track child --vp 320x568 --axe 1 --tag r1_child_320x568 
$R --track child --vp 360x640 --tag r1_child_360x640
$R --track child --vp 390x844 --axe 1 --aria 1 --tag r1_child_390x844_light
$R --track child --vp 390x844 --scheme dark --axe 1 --tag r1_child_390x844_dark
$R --track child --vp 412x915 --tag r1_child_412x915
$R --track child --vp 844x390 --tag r1_child_844x390
$R --track child --vp 768x1024 --tag r1_child_768x1024
$R --track child --vp 390x844 --fs 1.3 --tag r1_child_390x844_fs1.3
$R --track child --vp 390x844 --fs 2.0 --tag r1_child_390x844_fs2.0
$R --track child --vp 360x640 --fs 2.0 --tag r1_child_360x640_fs2.0
$R --track child --vp 320x568 --fs 1.3 --tag r1_child_320x568_fs1.3
$R --track child --vp 320x568 --fs 2.0 --tag r1_child_320x568_fs2.0
$R --track adult --vp 390x844 --axe 1 --aria 1 --tag r1_adult_390x844_light
$R --track adult --vp 844x390 --tag r1_adult_844x390
$R --track adult --vp 320x568 --fs 2.0 --tag r1_adult_320x568_fs2.0
echo ALLDONE
