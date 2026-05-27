import os 

apps = os.listdir('apps')
for app in apps:
    x = os.stat('apps/' + app)[0] & 0x4000
    print(app, x)
    
print(apps)

