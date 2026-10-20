import { useState } from 'react';
import { useNavigate } from 'react-router';
import { LogOut, UserRound } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

export function AccountControl({ compact=false }: {compact?: boolean}) {
  const {user,signOut,localBypass}=useAuth();
  const navigate=useNavigate();
  const [photoError,setPhotoError]=useState(false);
  const [error,setError]=useState('');
  if(!user)return <button type="button" onClick={()=>navigate('/login')} className="min-h-10 text-sm text-gray-300 px-3 py-2 rounded-lg hover:bg-gray-800">{localBypass ? 'Local mode · Sign in' : 'Sign in'}</button>;
  return <div className={`flex ${compact ? 'items-center gap-2' : 'flex-col gap-2'}`}>
    <div className="flex items-center gap-2.5 min-w-0" title={user.email || 'Signed in'}>
      {user.photoURL && !photoError ? <img key={user.uid} src={user.photoURL} alt={`${user.displayName || 'Google account'} profile`} referrerPolicy="no-referrer" onError={()=>setPhotoError(true)} className="h-8 w-8 rounded-full object-cover shrink-0" /> : <span className="h-8 w-8 rounded-full bg-gray-700 flex items-center justify-center shrink-0"><UserRound size={17} /></span>}
      {!compact && <div className="min-w-0"><p className="text-xs text-white truncate">{user.displayName || 'Signed in'}</p><p className="text-[10px] text-gray-400 truncate">{user.email}</p></div>}
    </div>
    <button type="button" aria-label="Sign out" onClick={async()=>{try{await signOut();navigate('/login');}catch{setError('Sign out failed. Please retry.');}}} className="min-h-10 inline-flex items-center justify-center gap-2 rounded-lg border border-gray-700 text-xs text-gray-300 px-3 py-2 hover:bg-gray-800"><LogOut size={14} />{!compact && 'Sign out'}</button>
    {error && <p role="alert" className="text-xs text-red-300">{error}</p>}
  </div>;
}
