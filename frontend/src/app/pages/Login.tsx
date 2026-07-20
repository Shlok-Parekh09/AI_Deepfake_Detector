import { useState } from 'react';
import { useNavigate } from 'react-router';
import { useAuth } from '../../contexts/AuthContext';
import svgPaths from '../../imports/MacBookPro166/svg-vk1owfvmuu';
import BrandLogo from '../components/BrandLogo';

export default function Login() {
  const navigate = useNavigate();
  const { signInWithGoogle, signInWithEmail } = useAuth();
  
  const [showEmailForm, setShowEmailForm] = useState(false);
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleGoogleLogin = async () => {
    try {
      await signInWithGoogle();
      // Note: Supabase handles the redirect automatically to /dashboard
    } catch (error) {
      console.error("Failed to sign in", error);
    }
  };

  const handleEmailSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;
    try {
      setLoading(true);
      setError('');
      setMessage('');
      await signInWithEmail(email);
      setMessage('Check your email for the login link!');
    } catch (err: any) {
      setError(err.message || 'Failed to send login link');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-[#08080e] via-[#10101c] to-[#08080e] flex items-center justify-center p-4 overflow-hidden relative">
      {/* Animated background gradients */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-[30%] -left-[10%] w-[70%] h-[70%] bg-cyan-500/10 rounded-full blur-[120px] mix-blend-screen animate-pulse duration-10000"></div>
        <div className="absolute -bottom-[30%] -right-[10%] w-[70%] h-[70%] bg-indigo-500/10 rounded-full blur-[120px] mix-blend-screen"></div>
      </div>

      <div className="relative z-10 w-full max-w-md">
        {/* Logo */}
        <div className="flex items-center justify-center gap-3 mb-8">
          <BrandLogo size={56} />
          <h1 className="text-white text-4xl font-bold" style={{ fontFamily: "'Eagle Lake', serif" }}>
            SynPhi
          </h1>
        </div>

        {/* Login Card */}
        <div className="bg-[#0e0e18]/80 backdrop-blur-2xl rounded-3xl p-8 sm:p-10 shadow-2xl border border-white/[0.06] relative z-20">
          {/* Profile Icon */}
          <div className="flex justify-center mb-8">
            <div className="w-16 h-16 bg-gradient-to-tr from-cyan-500/20 to-indigo-500/20 rounded-2xl flex items-center justify-center border border-white/5 shadow-inner">
              <svg className="w-8 h-8 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
          </div>

          {/* Title */}
          <h2 className="text-center text-2xl md:text-3xl text-white mb-2 font-bold tracking-tight">
            Welcome back
          </h2>

          {/* Subtitle */}
          <p className="text-center text-sm md:text-base text-gray-400 mb-8">
            Log in to continue to your dashboard
          </p>

          {showEmailForm ? (
            <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-300">
              <form onSubmit={handleEmailSubmit} className="space-y-4">
                <div>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Enter your email address"
                    required
                    className="w-full bg-white/[0.04] border border-white/[0.06] rounded-xl py-3.5 px-4 text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 transition-all"
                  />
                </div>
                {error && <p className="text-red-400 text-sm text-center">{error}</p>}
                {message && <p className="text-green-400 text-sm text-center">{message}</p>}
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-cyan-500 to-indigo-500 hover:from-cyan-400 hover:to-indigo-400 text-white rounded-xl py-3.5 px-4 font-semibold transition-all duration-200 shadow-lg shadow-cyan-500/25 disabled:opacity-50"
                >
                  {loading ? 'Sending link...' : 'Send Magic Link'}
                </button>
              </form>
              <button
                onClick={() => {
                  setShowEmailForm(false);
                  setError('');
                  setMessage('');
                }}
                className="w-full bg-transparent hover:bg-white/[0.04] border border-transparent hover:border-white/[0.06] rounded-xl py-3.5 px-4 text-gray-400 hover:text-white font-semibold transition-all duration-200"
              >
                Back to options
              </button>
            </div>
          ) : (
            <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-300">
              {/* Google Login */}
              <button
                onClick={handleGoogleLogin}
                className="w-full bg-white hover:bg-gray-100 rounded-xl py-3.5 px-4 flex items-center justify-center gap-3 transition-all duration-200 shadow-[0_0_20px_rgba(255,255,255,0.05)] hover:shadow-[0_0_25px_rgba(255,255,255,0.1)] group"
              >
                <div className="w-5 h-5">
                  <svg className="w-full h-full" fill="none" preserveAspectRatio="none" viewBox="0 0 50 50">
                    <g clipPath="url(#clip0_1_85)">
                      <path d={svgPaths.p261be200} fill="white" />
                      <path d={svgPaths.p162c3280} fill="#E33629" />
                      <path d={svgPaths.p2ef4a0c0} fill="#F8BD00" />
                      <path d={svgPaths.p2e8dbf80} fill="#587DBD" />
                      <path d={svgPaths.p35c11100} fill="#319F43" />
                    </g>
                    <defs>
                      <clipPath id="clip0_1_85">
                        <rect fill="white" height="50" width="50" />
                      </clipPath>
                    </defs>
                  </svg>
                </div>
                <span className="text-base font-semibold text-gray-900 group-hover:text-black">
                  Continue with Google
                </span>
              </button>

              {/* Divider */}
              <div className="relative py-4">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-white/[0.06]"></div>
                </div>
                <div className="relative flex justify-center text-xs uppercase tracking-widest font-semibold">
                  <span className="px-4 bg-[#0e0e18] text-gray-500">or</span>
                </div>
              </div>

              {/* Email Login */}
              <button
                onClick={() => setShowEmailForm(true)}
                className="w-full bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.06] hover:border-white/[0.1] rounded-xl py-3.5 px-4 flex items-center justify-center gap-3 transition-all duration-200 group"
              >
                <svg className="w-5 h-5 text-gray-400 group-hover:text-white transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                <span className="text-base font-semibold text-gray-300 group-hover:text-white transition-colors">
                  Continue with Email
                </span>
              </button>
            </div>
          )}

          {/* Terms and Conditions */}
          <p className="text-center text-xs md:text-sm text-slate-500 mt-6 leading-relaxed">
            By continuing, you agree to SynPhi's{' '}
            <a href="#" className="text-blue-400 hover:text-blue-300 underline">
              Terms and Conditions
            </a>
            . Read our{' '}
            <a href="#" className="text-blue-400 hover:text-blue-300 underline">
              Privacy Policy
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
