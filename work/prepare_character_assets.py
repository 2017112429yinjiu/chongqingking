from pathlib import Path
import zipfile,json,hashlib
ROOT=Path(__file__).resolve().parent
pack=ROOT/'assets_incoming/mpfb/makehuman_system_assets_cc0.zip'
dest=ROOT/'assets_incoming/mpfb/system_assets'
with zipfile.ZipFile(pack) as z:
    assert z.testzip() is None
    for n in z.namelist():
        p=(dest/n).resolve();assert p.is_relative_to(dest.resolve())
    z.extractall(dest)
print('EXTRACTED',len(list(dest.rglob('*'))))
print('\n'.join(str(p.relative_to(dest)) for p in dest.rglob('*.mhclo') if any(k in p.name for k in ['casualsuit','short0','shoes0'])))
data={'reviewed':'2026-11-20','tool_version':'MPFB 2.0.18 source archive','tool_source':'https://github.com/makehumancommunity/mpfb2',
 'tool_license':'GPL-3.0-or-later; build tool only. Assets and generated output CC0 per LICENSE.md.',
 'asset_source':'https://files2.makehumancommunity.org/asset_packs/makehuman_system_assets/makehuman_system_assets_cc0.zip',
 'asset_license_page':'https://static.makehumancommunity.org/assets/assetpacks/makehuman_system_assets.html',
 'asset_license':'CC0-1.0','author':'MakeHuman team / makehuman_system','attribution_required':False,
 'files':[{'name':f.name,'bytes':f.stat().st_size,'sha256':hashlib.file_digest(f.open('rb'),'sha256').hexdigest()} for f in [pack,ROOT/'assets_incoming/mpfb/mpfb2-master.zip']]}
(ROOT/'assets_incoming/mpfb/PROVENANCE.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
