# Rebuild dark_knight_live.html from src/ (Nov 5 2026). Run: python3 live_page/build.py
import os
d = os.path.dirname(os.path.abspath(__file__)); s = lambda f: open(os.path.join(d, 'src', f)).read()
h = s('part1.html') + s('part2.html').replace('@@ICON@@', s('icon.uri').strip()) + '<script>\n' + s('part3.js') + s('part4.js') + '</script>\n'
open(os.path.join(d, 'dark_knight_live.html'), 'w').write(h); print('built', len(h), 'bytes')
