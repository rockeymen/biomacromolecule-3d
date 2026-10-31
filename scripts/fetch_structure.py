#!/usr/bin/env python3
"""Fetch one entry/expanded biological assembly and retain a small provenance manifest."""
import argparse, datetime, hashlib, json, pathlib, re, urllib.request

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('pdb_id');ap.add_argument('--out',type=pathlib.Path,required=True)
    ap.add_argument('--assembly',type=int);args=ap.parse_args()
    if not re.fullmatch(r'(?:[A-Za-z0-9]{4}|pdb_[A-Za-z0-9]{8})',args.pdb_id):ap.error('Use a 4-character PDB ID or pdb_XXXXXXXX identifier')
    if args.assembly is not None and args.assembly<1:ap.error('Assembly must be positive')
    ident=args.pdb_id.upper() if len(args.pdb_id)==4 else args.pdb_id.lower()
    stem=ident+(f'-assembly{args.assembly}' if args.assembly else '')
    args.out.mkdir(parents=True,exist_ok=True)
    target=args.out/(stem+'.cif');manifest=args.out/(stem+'.source.json')
    if target.exists() or manifest.exists():ap.error('Output already exists; reuse it or choose a new output directory')
    url=f'https://files.rcsb.org/download/{stem}.cif'
    req=urllib.request.Request(url,headers={'User-Agent':'Biomolecular-3D educational structure preparation'})
    with urllib.request.urlopen(req,timeout=90) as response:data=response.read()
    if b'data_' not in data[:512] or b'_atom_site.' not in data:raise ValueError('Response is not coordinate mmCIF')
    info={'pdbId':ident,'assembly':args.assembly,'coordinatesExpanded':args.assembly is not None,'sourceUrl':url,'downloadedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'dataLicense':'CC0-1.0','licenseUrl':'https://www.rcsb.org/pages/policies'}
    target.write_bytes(data);manifest.write_text(json.dumps(info,indent=2)+'\n')
    print(json.dumps({'coordinates':str(target),'manifest':str(manifest),'bytes':len(data)}))
if __name__=='__main__':main()
