import re

pattern = re.compile('smarthome\.([a-z]*)\.switch\.([a-z]*)')
# matches = pattern.match('smarthome.lights.switch.off')
matches = pattern.match('smarthome.lights.switch')

if matches:
    print(matches.groups())
else:
    print('test')