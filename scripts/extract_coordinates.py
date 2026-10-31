#!/usr/bin/env python3
"""Parse real mmCIF using gemmi; preserve label/auth IDs, choose one model/conformer, convert A to nm."""
import argparse, hashlib, json, pathlib

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input',type=pathlib.Path,required=True);ap.add_argument('--out',type=pathlib.Path,required=True)
    ap.add_argument('--representation',choices=['ca','nucleic','atoms'],default='atoms')
    ap.add_argument('--model',default='1');ap.add_argument('--chains',help='comma-separated label_asym_id values')
    ap.add_argument('--include-water',action='store_true');ap.add_argument('--include-hydrogen',action='store_true')
    ap.add_argument('--center-auth-chains',help='Optional origin group, author chain IDs')
    ap.add_argument('--axis-auth-chains',help='Optional +Y group measured from the chosen origin; requires --center-auth-chains')
    args=ap.parse_args()
    try:import gemmi,numpy as np
    except ImportError:ap.error('Use a task environment with gemmi and numpy installed')
    if args.out.exists():ap.error('Output exists; choose a new path')
    if args.axis_auth_chains and not args.center_auth_chains:ap.error('An oriented axis requires an explicit center group')
    block=gemmi.cif.read_file(str(args.input)).sole_block()
    vals=lambda tag:list(block.find_values(tag))
    def category(prefix,names):
        columns={n:vals(prefix+n) for n in names}
        count=max((len(v) for v in columns.values()),default=0)
        return [{k:(v[i] if i<len(v) else '?') for k,v in columns.items()} for i in range(count)]
    poly={r['entity_id']:r['type'].strip("'\"") for r in category('_entity_poly.',['entity_id','type'])}
    cols=['group_PDB','type_symbol','label_atom_id','label_alt_id','label_comp_id','label_asym_id','label_entity_id','label_seq_id','auth_asym_id','auth_seq_id','pdbx_PDB_ins_code','Cartn_x','Cartn_y','Cartn_z','occupancy','pdbx_PDB_model_num']
    rows=category('_atom_site.',cols)
    selected=set(args.chains.split(',')) if args.chains else None
    # Choose one residue-level alternate by total occupancy. Common (blank) atoms are retained.
    alt_weights={}
    for r in rows:
        if r['pdbx_PDB_model_num']!=args.model:continue
        key=(r['label_asym_id'],r['auth_seq_id'],r['pdbx_PDB_ins_code'],r['label_comp_id'])
        alt=r['label_alt_id']
        if alt not in ('.','?',''):
            weights=alt_weights.setdefault(key,{})
            weights[alt]=weights.get(alt,0)+float(r['occupancy'] if r['occupancy'] not in ('.','?') else 0)
    chosen={k:sorted(v,key=lambda a:(-v[a],a))[0] for k,v in alt_weights.items()}
    groups={};seen=set();skipped=0
    for r in rows:
        if r['pdbx_PDB_model_num']!=args.model:continue
        chain=r['label_asym_id'];typ=poly.get(r['label_entity_id'],'non-polymer');name=r['label_atom_id'].strip("\"");element=r['type_symbol'].upper()
        if selected and chain not in selected:continue
        if not args.include_water and r['label_comp_id'] in ('HOH','DOD','WAT'):continue
        if not args.include_hydrogen and element in ('H','D'):continue
        residue=(chain,r['auth_seq_id'],r['pdbx_PDB_ins_code'],r['label_comp_id'])
        if r['label_alt_id'] not in ('.','?','',chosen.get(residue)):
            skipped+=1;continue
        if args.representation=='ca' and not ('polypeptide' in typ and name=='CA' and element=='C'):continue
        if args.representation=='nucleic' and not ('ribonucleotide' in typ and name in ('P',"C4'")):continue
        key=(*residue,name)
        if key in seen:skipped+=1;continue
        seen.add(key)
        point=[float(r['Cartn_'+axis])*.1 for axis in 'xyz']
        if not np.isfinite(point).all():raise ValueError('Non-finite coordinate')
        g=groups.setdefault(chain,{'id':chain,'authId':r['auth_asym_id'],'entityId':r['label_entity_id'],'polymerType':typ,'points':[],'atoms':[]})
        g['points'].append(point);g['atoms'].append({'name':name,'element':element,'component':r['label_comp_id'],'labelSeqId':r['label_seq_id'],'authSeqId':r['auth_seq_id'],'insertionCode':r['pdbx_PDB_ins_code'],'alternate':r['label_alt_id']})
    if not groups:ap.error('No matching coordinates; check model, representation and chain IDs')
    if selected and selected-set(groups):ap.error('Requested label chains absent after filtering: '+','.join(sorted(selected-set(groups))))
    def group_points(ids):
        requested=set(ids.split(','));found={g['authId'] for g in groups.values() if g['authId'] in requested}
        if requested!=found:ap.error('Origin/axis author IDs not found after filtering: '+','.join(requested-found))
        return np.array([p for g in groups.values() if g['authId'] in requested for p in g['points']])
    points=np.array([p for g in groups.values() for p in g['points']]);origin=group_points(args.center_auth_chains).mean(0) if args.center_auth_chains else points.mean(0)
    basis=np.eye(3)
    if args.axis_auth_chains:
        axis=group_points(args.axis_auth_chains).mean(0)-origin
        if np.linalg.norm(axis)<1e-8:ap.error('Origin and axis groups have the same centroid')
        axis/=np.linalg.norm(axis);helper=np.eye(3)[np.argmin(np.abs(axis))];right=np.cross(helper,axis);right/=np.linalg.norm(right);basis=np.array([right,axis,np.cross(right,axis)])
    for g in groups.values():
        delta=np.array(g['points'])-origin
        transformed=(delta[:,None,:]*basis[None,:,:]).sum(axis=2)
        if not np.isfinite(transformed).all():raise ValueError('Invalid transformed coordinate')
        g['points']=np.round(transformed,5).tolist()
    manifest_file=args.input.with_suffix('.source.json')
    provenance=json.loads(manifest_file.read_text()) if manifest_file.exists() else None
    digest=hashlib.sha256(args.input.read_bytes()).hexdigest()
    if provenance and provenance.get('sha256')!=digest:ap.error('Source manifest hash does not match coordinates')
    out={'provenance':provenance,'format':'rcsb-coordinates-v1','inputSha256':hashlib.sha256(args.input.read_bytes()).hexdigest(),'inputFile':args.input.name,'unit':'nm','model':args.model,'representation':args.representation,'alternatePolicy':'residue-level highest total occupancy; blank atoms retained','alternateRecordsSkipped':skipped,'sourceToWorld':{'angstromToNm':.1,'originNm':origin.tolist(),'basisRows':basis.tolist()},'chains':list(groups.values()),'pointCount':len(points)}
    args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(out,separators=(',',':'),allow_nan=False)+'\n')
    print(json.dumps({'output':str(args.out),'points':len(points),'chains':[{'label':g['id'],'auth':g['authId'],'points':len(g['points'])} for g in groups.values()]}))
if __name__=='__main__':main()
