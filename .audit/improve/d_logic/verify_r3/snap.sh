#!/bin/bash
M=/home/oye/Documents/free_work/urdu-reading-course/mobile; S=/tmp/claude-1000/snap_r3
rm -rf $S/src; cp -r $M/src $S/src; rm -rf $S/public; cp -r $M/public $S/public; cp $M/index.html $M/vite.config.js $M/package.json $M/vite-sw-plugin.js $S/
