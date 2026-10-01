"""Side-by-side: canonical PNG (hello) vs animated frames at 512 px -> /tmp/claude-1000/cmp.png"""
import sys; sys.argv = ['x']
from sheet import *
fr = web_frames(['idle', 'point'], 512)
ref = Image.open('/tmp/claude-1000/ref512.png').convert('RGB')
s = Image.new('RGB', (1536, 512), 'white'); s.paste(ref, (0, 0)); s.paste(fr['idle'][0][0].convert('RGB'), (512, 0))
s.paste(fr['point'][0][3].convert('RGB'), (1024, 0)); s.save('/tmp/claude-1000/cmp.png')
