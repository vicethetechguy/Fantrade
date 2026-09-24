# -*- coding: utf-8 -*-
with open('tools/pages2.py', 'r', encoding='utf-8') as f:
    c = f.read()

old_wa = 'WALLET_ASSETS = [("FSAKA", "Bukayo Saka", "boot", "", 6.4, 0),'
new_wa = 'WALLET_ASSETS = [("FSAKA", "Bukayo Saka", "boot", "", 6.4, 0),\n                 ("FAITN", "Aitana Bonmatí", "boot", "", 5.8, 0),'

if 'FAITN' not in c:
    c = c.replace(old_wa, new_wa)
    with open('tools/pages2.py', 'w', encoding='utf-8') as f:
        f.write(c)
    print('Updated tools/pages2.py')
else:
    print('Already in pages2.py')
