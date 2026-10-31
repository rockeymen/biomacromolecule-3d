#!/usr/bin/env node
// Optional teaching envelope, not an atomic or solvent-excluded surface.
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
const args={};for(let i=2;i<process.argv.length;i+=2){if(!process.argv[i].startsWith('--')||!process.argv[i+1])throw Error('Use --key value pairs');args[process.argv[i].slice(2)]=process.argv[i+1];}
for(const key of ['project','input','out'])if(!args[key])throw Error('Required: --project PROJECT --input CA_JSON --out OUTPUT_PREFIX');
const resolution=Number(args.resolution||44),radius=Number(args.radius||.37),maxTriangles=Number(args['max-triangles']||100000);
if(!Number.isInteger(resolution)||resolution<16||resolution>128||!Number.isFinite(radius)||radius<=0||!Number.isInteger(maxTriangles)||maxTriangles<100)throw Error('Invalid resolution, radius or triangle capacity');
const require=createRequire(path.resolve(args.project,'package.json')),threeRoot=path.resolve(path.dirname(require.resolve('three')),'..');
const THREE=await import(pathToFileURL(path.join(threeRoot,'build/three.module.js')));
const {MarchingCubes}=await import(pathToFileURL(path.join(threeRoot,'examples/jsm/objects/MarchingCubes.js')));
const {mergeVertices}=await import(pathToFileURL(path.join(threeRoot,'examples/jsm/utils/BufferGeometryUtils.js')));
const source=JSON.parse(await fs.readFile(args.input,'utf8'));
if(source.representation!=='ca'||source.unit!=='nm')throw Error('Input must be protein C-alpha coordinates in nm, not nucleic traces/all atoms');
for(const ext of ['.bin','.json'])if(await fs.stat(args.out+ext).catch(()=>null))throw Error('Output exists; choose a new prefix');
const blocks=[],chains=[];let offset=0;
function align4(){const padding=(4-offset%4)%4;if(padding){blocks.push(Buffer.alloc(padding));offset+=padding;}}
for(const chain of source.chains){
 const points=chain.points;if(!points.length||points.some(p=>p.length!==3||p.some(v=>!Number.isFinite(v))))throw Error('Invalid points');
 const bounds=new THREE.Box3().setFromPoints(points.map(p=>new THREE.Vector3(...p))),center=bounds.getCenter(new THREE.Vector3()),size=bounds.getSize(new THREE.Vector3()),span=Math.max(size.x,size.y,size.z)+Math.max(1.6,radius*4);
 if(span/(resolution-2)>radius*.85)console.warn(`${chain.id}: voxel size is coarse relative to the envelope radius; inspect or increase resolution`);
 const mc=new MarchingCubes(resolution,new THREE.MeshBasicMaterial(),false,false,maxTriangles);mc.isolation=1;mc.reset();
 for(const p of points)mc.addBall((p[0]-center.x)/span+.5,(p[1]-center.y)/span+.5,(p[2]-center.z)/span+.5,12*(radius/span)**2,12);
 mc.update();const count=mc.count;
 if(count===0||count>=maxTriangles*3)throw Error(`${chain.id}: empty/truncated surface; adjust resolution/radius/capacity`);
 const raw=new THREE.BufferGeometry();raw.setAttribute('position',new THREE.BufferAttribute(mc.geometry.attributes.position.array.slice(0,count*3),3));raw.setAttribute('normal',new THREE.BufferAttribute(mc.geometry.attributes.normal.array.slice(0,count*3),3));
 const geometry=mergeVertices(raw,.00001);geometry.normalizeNormals();const n=geometry.attributes.position.count,position=geometry.attributes.position.array,normal=geometry.attributes.normal.array;
 const quantum=Math.max(.001,span/2/32760),vertices=Buffer.alloc(n*12);
 for(let i=0;i<n;i++)for(let j=0;j<3;j++){
  const value=Math.round(position[i*3+j]*span/2/quantum),norm=Math.round(normal[i*3+j]*32767);
  if(Math.abs(value)>32767||!Number.isFinite(value)||!Number.isFinite(norm))throw Error('Non-finite or overflowing packed coordinate');
  vertices.writeInt16LE(value,i*12+j*2);vertices.writeInt16LE(THREE.MathUtils.clamp(norm,-32767,32767),i*12+6+j*2);
 }
 const indexBytes=n>65535?4:2,indices=Buffer.alloc(geometry.index.count*indexBytes);
 for(let i=0;i<geometry.index.count;i++){const value=geometry.index.array[i];if(value>=n)throw Error('Invalid triangle index');if(indexBytes===4)indices.writeUInt32LE(value,i*4);else indices.writeUInt16LE(value,i*2);}
 align4();const vertexOffset=offset;blocks.push(vertices);offset+=vertices.length;align4();const indexOffset=offset;blocks.push(indices);offset+=indices.length;
 chains.push({id:chain.id,authId:chain.authId,entityId:chain.entityId,polymerType:chain.polymerType,residues:points.length,vertexOffset,vertices:n,indexOffset,indexCount:geometry.index.count,indexBytes,centerNm:center.toArray(),positionUnitNm:quantum,bounds:{min:bounds.min.toArray(),max:bounds.max.toArray()}});
 geometry.dispose();raw.dispose();mc.geometry.dispose();mc.material.dispose();
}
await fs.mkdir(path.dirname(path.resolve(args.out)),{recursive:true});await fs.writeFile(args.out+'.bin',Buffer.concat(blocks));
await fs.writeFile(args.out+'.json',JSON.stringify({format:'rcsb-ca-envelope-v1',unit:'nm',provenance:source.provenance||null,sourceSha256:source.inputSha256,sourceToWorld:source.sourceToWorld,model:source.model,representation:'inflated C-alpha teaching envelope; not an atomic surface',envelopeRadiusNm:radius,resolution,encoding:'LE int16 position xyz + int16 normal xyz per vertex; per-chain uint16/uint32 triangle indices',normalDivisor:32767,bytes:offset,chains},null,2)+'\n');
console.log(JSON.stringify({prefix:args.out,chains:chains.length,bytes:offset,triangles:chains.reduce((sum,c)=>sum+c.indexCount/3,0)}));
