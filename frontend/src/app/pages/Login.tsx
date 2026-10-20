import { useState, type FormEvent } from 'react';
import { Link, useNavigate } from 'react-router';
import { Eye, EyeOff, ShieldCheck, AudioLines, FileText, Github } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import BrandLogo from '../components/BrandLogo';
import { GoogleLogo, AppleLogo } from '../components/ProviderLogo';
const providers = ['Google','GitHub','Apple','Microsoft'] as const;
const field = 'mt-2 min-h-12 w-full rounded-xl border border-white/10 bg-white/[0.035] px-4 text-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-sky-500';
export default function Login() {
 const navigate=useNavigate();
 const {signInWithProvider,signInWithEmail,signUpWithEmail,configurationError,localBypass}=useAuth();
 const [signup,setSignup]=useState(false), [email,setEmail]=useState(''), [password,setPassword]=useState('');
 const [visible,setVisible]=useState(false), [agreed,setAgreed]=useState(false), [busy,setBusy]=useState(''), [error,setError]=useState('');
 async function authenticate(method:'email'|typeof providers[number]) {
  if(signup&&!agreed){setError('Please agree to the Terms and Conditions first.');return;}
  setBusy(method);setError('');
  try { if(method!=='email') await signInWithProvider(method); else if(signup) await signUpWithEmail(email,password); else await signInWithEmail(email,password); navigate('/dashboard'); }
  catch(reason:unknown){const code=(reason as {code?:string}).code;setError(code==='auth/operation-not-allowed'?`${method} sign-in is not enabled in Firebase.`:code==='auth/popup-blocked'?'Allow pop-ups for this website and try again.':code==='auth/account-exists-with-different-credential'?'Use the sign-in method originally used for this account.':code==='auth/unauthorized-domain'?'This website domain must be authorized in Firebase.':code==='auth/popup-closed-by-user'?'Sign-in was cancelled. You can try again.':'Could not sign in. Check your details and try again.');}
  finally{setBusy('');}
 }
 function submit(event:FormEvent){event.preventDefault();void authenticate('email');}
 return <main className="min-h-dvh bg-[#191919] text-white lg:grid lg:grid-cols-[46%_54%]">
  <aside className="hidden lg:flex flex-col justify-between p-12 xl:p-16 bg-[#090f16]" style={{backgroundImage:'radial-gradient(ellipse at 15% 85%, #06446a99, transparent 55%),radial-gradient(ellipse at 85% 25%, #12365277, transparent 55%)'}}>
   <Link to="/" className="flex items-center gap-3 w-fit"><BrandLogo size={38}/><span className="text-2xl font-semibold">SynPhi <span className="font-normal text-gray-400">Detector</span></span></Link>
   <div className="py-16 max-w-xl"><h1 className="text-4xl xl:text-5xl font-semibold leading-tight tracking-tight">A closer look at what's real.</h1><p className="mt-6 text-lg leading-8 text-gray-400">Check audio, images and video, then bring the evidence into your verification workflow.</p>
    <div className="mt-14 space-y-8">
     <Feature icon={<ShieldCheck size={24}/>} title="Your account, your workspace" text="Keep your scan history connected to your account."/>
     <Feature icon={<AudioLines size={24}/>} title="Inspect the signal" text="Review measured audio views and media alongside the prediction."/>
     <Feature icon={<FileText size={24}/>} title="Take the report with you" text="Download an assessment with model details and analysis limits."/>
    </div>
   </div><p className="text-xs leading-5 text-gray-500">Automated predictions support review. They do not establish authenticity.</p>
  </aside>
  <section className="flex justify-center px-5 py-8 sm:px-10 lg:px-12 lg:py-14" aria-label="Account access"><div className="w-full max-w-lg my-auto">
   <Link to="/" className="flex items-center gap-2 mb-10 lg:hidden"><BrandLogo size={28}/><span className="font-semibold text-lg">SynPhi</span></Link>
   <h2 className="text-3xl sm:text-4xl font-semibold tracking-tight">{signup?'Create your account':'Welcome back'}</h2><p className="mt-3 mb-8 text-gray-400">{signup?'Start your media verification workspace.':'Sign in to your SynPhi workspace.'}</p>
   {configurationError&&<p role="alert" className="mb-5 text-sm text-red-300">{configurationError}</p>}
   {error&&<p role="alert" className="mb-5 rounded-lg border border-red-400/20 p-3 text-sm text-red-300">{error}</p>}
   <form onSubmit={submit} className="space-y-5">
    <label className="block text-sm text-gray-300">Email<input type="email" autoComplete="email" value={email} onChange={e=>setEmail(e.target.value)} required placeholder="you@example.com" className={field}/></label>
    <div><label htmlFor="account-password" className="text-sm text-gray-300">Password</label><div className="relative"><input id="account-password" type={visible?'text':'password'} autoComplete={signup?'new-password':'current-password'} minLength={signup?6:undefined} value={password} onChange={e=>setPassword(e.target.value)} required placeholder={signup?'Create a password':'Your password'} className={`${field} pr-12`}/><button type="button" onClick={()=>setVisible(!visible)} aria-label={visible?'Hide password':'Show password'} aria-pressed={visible} className="absolute right-1 bottom-0 min-h-12 min-w-11 flex items-center justify-center text-gray-400">{visible?<EyeOff size={18}/>:<Eye size={18}/>}</button></div></div>
    {signup&&<label className="flex items-start gap-3 text-sm leading-6 text-gray-400"><input type="checkbox" checked={agreed} onChange={e=>setAgreed(e.target.checked)} required className="mt-1 h-4 w-4 shrink-0 accent-sky-500"/><span>I agree to the <Link to="/terms" className="text-sky-400 hover:underline">Terms and Conditions</Link> and <Link to="/privacy" className="text-sky-400 hover:underline">Privacy Policy</Link>.</span></label>}
    <button disabled={Boolean(busy)||Boolean(configurationError)} className="w-full min-h-12 rounded-xl bg-sky-600 hover:bg-sky-500 disabled:opacity-50 font-semibold">{busy==='email'?'Please wait...':signup?'Create account':'Sign in'}</button>
   </form>
   <div className="flex items-center gap-4 my-6 text-xs text-gray-500"><span className="h-px flex-1 bg-white/10"/>or continue with<span className="h-px flex-1 bg-white/10"/></div>
   <div className="grid grid-cols-2 gap-3">{providers.map(provider=><button key={provider} type="button" disabled={Boolean(busy)||Boolean(configurationError)} onClick={()=>void authenticate(provider)} className="min-h-12 flex items-center justify-center gap-2 rounded-xl border border-white/15 bg-white/[0.025] hover:bg-white/[0.07] disabled:opacity-50 text-sm">{provider==='GitHub'?<Github size={19} aria-hidden/>:provider==='Apple'?<AppleLogo/>:provider==='Microsoft'?<span aria-hidden className="grid grid-cols-2 gap-0.5 w-4 h-4">{['#f25022','#7fba00','#00a4ef','#ffb900'].map(color=><span key={color} style={{background:color}}/>)}</span>:<GoogleLogo/>}{busy===provider?'Connecting...':provider}</button>)}</div>
   <p className="mt-7 text-center text-sm text-gray-400">{signup?'Already have an account?':'New to SynPhi?'} <button type="button" disabled={Boolean(busy)} onClick={()=>{setSignup(!signup);setError('');}} className="text-sky-400 hover:underline">{signup?'Sign in':'Create an account'}</button></p>
   {!signup&&<p className="mt-5 text-center text-xs leading-5 text-gray-500">By continuing, you agree to our <Link to="/terms" className="text-gray-300 underline">Terms and Conditions</Link>. Read our <Link to="/privacy" className="text-gray-300 underline">Privacy Policy</Link>.</p>}
   {localBypass&&<button type="button" onClick={()=>navigate('/dashboard')} className="mt-5 w-full min-h-11 text-xs text-gray-500 hover:text-gray-300">Continue locally without signing in</button>}
  </div></section>
 </main>;
}
function Feature({icon,title,text}:{icon:React.ReactNode;title:string;text:string}){return <div className="flex gap-5"><div className="h-12 w-12 shrink-0 rounded-xl bg-white/[0.07] flex items-center justify-center text-sky-200">{icon}</div><div><h2 className="font-semibold">{title}</h2><p className="mt-1 text-sm leading-6 text-gray-400">{text}</p></div></div>;}
