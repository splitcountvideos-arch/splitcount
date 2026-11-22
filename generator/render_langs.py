import json,subprocess
L={"EN":{"l1":"Every wall hit","l2":"splits the ball in two!","q":"How fast will it reach 2000?","s":"s","done":"Reached in {:.1f} seconds!"},
"DE":{"l1":"Bei jedem Aufprall","l2":"teilt sich der Ball!","q":"Wie schnell sind es 2000?","s":"s","done":"Nach {:.1f} Sekunden geschafft!"},
"TR":{"l1":"Duvara her çarpışta","l2":"top ikiye bölünür!","q":"2000'e kaç saniyede ulaşır?","s":"sn","done":"{:.1f} saniyede ulaştı!"}}
for k,v in L.items(): subprocess.run(["python3","generator/split_sim.py",json.dumps(v),f"split_{k}.mp4"],check=True)
