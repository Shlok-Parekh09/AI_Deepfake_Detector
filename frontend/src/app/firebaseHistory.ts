import { collection, doc, getDocs, getDoc, limit, orderBy, query, writeBatch } from 'firebase/firestore';
import { auth, database } from '../lib/firebase';
import type { SavedScan, AnalysisResult } from './scanHistory';

export function hasCloudHistory(owner: string) {
  return Boolean(database && auth?.currentUser?.uid === owner);
}
function checkedDatabase(owner: string) {
  if(!database || auth?.currentUser?.uid !== owner)throw new Error('Sign in to access this account’s history.');
  return database;
}
export async function saveCloudScan(scan: SavedScan, owner: string) {
  const db=checkedDatabase(owner);
  if(!scan.result)throw new Error('No analysis result to save.');
  // Bounded chunks avoid Firestore's one-megabyte document limit for embedded PDFs.
  const payload=JSON.stringify(scan.result);
  const chunks=payload.match(/[\s\S]{1,180000}/g) || [];
  if(chunks.length>40)throw new Error('Report exceeds account history size limit.');
  const reference=doc(db,'users',owner,'scans',scan.id);
  const batch=writeBatch(db);
  batch.set(reference,{title:scan.title,type:scan.type,time:scan.time,status:scan.status,createdAt:scan.createdAt,chunkCount:chunks.length});
  chunks.forEach((data,index)=>batch.set(doc(reference,'payload',String(index).padStart(3,'0')),{data,index}));
  await batch.commit();
}
export async function listCloudScans(owner: string): Promise<SavedScan[]> {
  const db=checkedDatabase(owner);
  const snapshots=await getDocs(query(collection(db,'users',owner,'scans'),orderBy('createdAt','desc'),limit(20)));
  return snapshots.docs.map(record=>({id:record.id,...record.data(),remote:true}) as SavedScan);
}
export async function fetchCloudResult(id: string, owner: string): Promise<AnalysisResult> {
  const db=checkedDatabase(owner);
  const reference=doc(db,'users',owner,'scans',id);
  const header=await getDoc(reference);
  const count=header.data()?.chunkCount;
  if(!Number.isInteger(count) || count<1 || count>40)throw new Error('Saved report is incomplete.');
  const snapshots=await getDocs(query(collection(reference,'payload'),orderBy('index')));
  if(snapshots.size!==count)throw new Error('Saved report is incomplete.');
  const result=JSON.parse(snapshots.docs.map(part=>part.data().data).join('')) as AnalysisResult;
  if(typeof result.is_fake!=='boolean' || !Number.isFinite(result.fake_probability))throw new Error('Saved analysis is invalid.');
  return result;
}

export async function clearCloudHistory(owner: string) {
  const db=checkedDatabase(owner);
  while(true){
    const scans=await getDocs(query(collection(db,'users',owner,'scans'),limit(40)));
    if(scans.empty)return;
    for(const scan of scans.docs){
      const parts=await getDocs(collection(scan.ref,'payload'));
      // Each saved payload is capped at 40 chunks.
      const batch=writeBatch(db);parts.docs.forEach(part=>batch.delete(part.ref));batch.delete(scan.ref);await batch.commit();
    }
  }
}
