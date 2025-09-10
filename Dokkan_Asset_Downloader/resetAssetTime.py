import json

with open('settings.json') as f:
    data = json.load(f)

data['GlbAssetVersion'] = 0

with open('settings.json', 'w') as f:
    json.dump(data, f, indent="\t")
