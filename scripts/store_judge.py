#!/usr/bin/env python3
"""Blind critic for store screenshots (Gemini vision). Two image strips, labels stripped, order shuffled.

  python3 scripts/store_judge.py <strip_ours.png> <strip_theirs.png> "<context>"
"""
import base64, json, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import listen_judge as J


def img(p):
    return {"inline_data": {"mime_type": "image/png", "data": base64.b64encode(open(p, "rb").read()).decode()}}


def ab(a, b, context, model="gemini-3.1-pro-preview"):
    pair = [a, b]; random.shuffle(pair)
    prompt = (f"You are a harsh app-store conversion expert and also a Pakistani parent. {context} "
              "Below are the Google Play screenshot sets of two different apps (first screenshots on the left). "
              "Judge only what a parent sees while scrolling the store: would they tap Install? Weigh the first 3 screenshots most. "
              'Reply JSON: {"better": "1"|"2", "why": "<one line>", "loser_gap": "<the single biggest thing the losing set must fix>", "winner_gap": "<the biggest remaining weakness of the winning set>"}')
    r = J.ask([{"text": prompt}, {"text": "Set 1:"}, img(pair[0]), {"text": "Set 2:"}, img(pair[1])], model)
    r["winner"] = pair[int(r["better"]) - 1]
    return r


if __name__ == "__main__":
    a, b, ctx = sys.argv[1:4]
    wins = []
    for _ in range(3):  # 3 shuffled trials; order bias shows up as a split
        r = ab(a, b, ctx); wins.append(r["winner"] == a); print(json.dumps(r, ensure_ascii=False))
    print(f"ours won {sum(wins)}/3")
