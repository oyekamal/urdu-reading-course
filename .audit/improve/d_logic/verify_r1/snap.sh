#!/bin/bash
M=/home/oye/Documents/free_work/urdu-reading-course/mobile; S=/tmp/claude-1000/snap_r1
mkdir -p $S; rm -rf $S/src; cp -r $M/src $S/src
[ -d $S/public ] || cp -r $M/public $S/public
cp $M/index.html $M/vite.config.js $M/package.json $S/; [ -e $S/node_modules ] || ln -s $M/node_modules $S/node_modules
