import json
import os

SETTINGSLOC=os.path.dirname(os.path.abspath(__file__))+"/Dokkan_Asset_Downloader/settings.json"

with open(SETTINGSLOC) as f:
    data = json.load(f)

data['GlbAssetVersion'] = 0

with open(SETTINGSLOC, 'w') as f:
    json.dump(data, f, indent="\t")
