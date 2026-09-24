# -*- coding: utf-8 -*-
with open('tools/pages3.py', 'r', encoding='utf-8') as f:
    c = f.read()

# Add Bonmati and Kerr to fallbackListings
old_listings = """      { id:'lst-haaland-drop', asset_id:'FHLND', ticker:'FHLND', name:'Erling Haaland', title:'Goal Machine Drop', shares:500000 }
    ]"""

new_listings = """      { id:'lst-haaland-drop', asset_id:'FHLND', ticker:'FHLND', name:'Erling Haaland', title:'Goal Machine Drop', shares:500000 },
      { id:'lst-bonmati-drop', asset_id:'FAITN', ticker:'FAITN', name:'Aitana Bonmatí', title:'Ballon d\\'Or Féminin Drop', shares:500000 },
      { id:'lst-kerr-drop', asset_id:'FKERR', ticker:'FKERR', name:'Sam Kerr', title:'Chelsea Queen Drop', shares:500000 }
    ]"""

if "lst-bonmati-drop" not in c:
    c = c.replace(old_listings, new_listings)

# Add female stars to trending / hot list
old_hot = "if(homeFilter === 'hot') list = list.filter(function(a){ return ['FSAKA','FHLND','FKM7','FYAML','FPLMR','FARTA'].indexOf(a.t) >= 0; });"
new_hot = "if(homeFilter === 'hot') list = list.filter(function(a){ return ['FSAKA','FAITN','FHLND','FKERR','FKM7','FYAML','FRUSS','FPLMR','FLJMS','FWIEG','FARTA'].indexOf(a.t) >= 0; });"
c = c.replace(old_hot, new_hot)

with open('tools/pages3.py', 'w', encoding='utf-8') as f:
    f.write(c)

print('Updated tools/pages3.py')
