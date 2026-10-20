import type { AuditEvidence } from './components/AudioReview';
import { hasCloudHistory, listCloudScans, saveCloudScan, clearCloudHistory } from './firebaseHistory';

export interface AnalysisResult {
  is_fake: boolean;
  fake_probability: number;
  file_type?: 'audio' | 'video' | 'image';
  audit_report?: AuditEvidence;
  report_pdf_base64?: string;
  report_filename?: string;
  report_error?: string;
  review_required?: boolean;
  detected_tool?: string;
}
export interface SavedScan {
  id: string;
  title: string;
  type: 'audio' | 'video' | 'image';
  time: string;
  status: 'high' | 'low';
  createdAt: number;
  result?: AnalysisResult;
  remote?: boolean;
  sourceUrl?: string;
  mediaBlob?: Blob;
}
const DB = 'synphi-local-scan-history';
export function compactScans(rows: SavedScan[]): SavedScan[] {
  let bytes=0;
  return rows.slice(0,20).map(row=>{
    bytes+=row.mediaBlob?.size || 0;
    if(bytes>200*1024*1024 && row.mediaBlob){const {mediaBlob: _media,...rest}=row;return rest;}
    return row;
  });
}
function database(owner: string): Promise<IDBDatabase> {
  return new Promise((resolve,reject) => {
    const request = indexedDB.open(owner==='local-development' ? DB : `${DB}:${owner}`,1);
    request.onupgradeneeded = () => request.result.createObjectStore('scans',{keyPath:'id'});
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}
export async function loadScans(owner='local-development', notice?: (message: string)=>void): Promise<SavedScan[]> {
  let rows: SavedScan[]=[];
  const db=await database(owner);
  try {
    rows=await new Promise((resolve,reject) => {
      const transaction=db.transaction('scans','readonly');
      const request=transaction.objectStore('scans').getAll();
      request.onsuccess=()=>resolve((request.result as SavedScan[]).sort((a,b)=>b.createdAt-a.createdAt));
      request.onerror=()=>reject(request.error);
    });
  } finally { db.close(); }
  if(hasCloudHistory(owner)){
    try {
      const cloud=await listCloudScans(owner);
      const merged=new Map([...cloud,...rows].map(scan=>[scan.id,scan]));
      rows=[...merged.values()].sort((a,b)=>b.createdAt-a.createdAt);
    } catch {notice?.('Account sync is unavailable. Showing scans saved on this device.');}
  }
  return compactScans(rows);
}
export async function saveScan(scan: SavedScan, owner='local-development', notice?: (message: string)=>void): Promise<void> {
  const db=await database(owner);
  try {
    await new Promise<void>((resolve,reject)=>{
      const transaction=db.transaction('scans','readwrite');
      const store=transaction.objectStore('scans');store.put(scan);
      const request=store.getAll();
      request.onsuccess=()=>{
        const rows=(request.result as SavedScan[]).sort((a,b)=>b.createdAt-a.createdAt);
        let mediaBytes=0;
        rows.forEach((row,index)=>{
          if(index>=20){store.delete(row.id);return;}
          mediaBytes+=row.mediaBlob?.size || 0;
          if(mediaBytes>200*1024*1024 && row.mediaBlob){delete row.mediaBlob;store.put(row);}
        });
      };
      transaction.oncomplete=()=>resolve();
      transaction.onerror=()=>reject(transaction.error);
      transaction.onabort=()=>reject(transaction.error);
    });
  } finally {db.close();}
  if(hasCloudHistory(owner)){
    try {await saveCloudScan(scan,owner);}
    catch {notice?.('Result saved on this device. Account sync is unavailable; check the Firebase database and access rules.');}
  }
}

export async function clearScans(owner: string) {
  if(hasCloudHistory(owner))await clearCloudHistory(owner);
  const db=await database(owner);
  try {
    await new Promise<void>((resolve,reject)=>{
      const transaction=db.transaction('scans','readwrite');transaction.objectStore('scans').clear();
      transaction.oncomplete=()=>resolve();transaction.onerror=()=>reject(transaction.error);
    });
  } finally {db.close();}
}
