import { useState } from 'react';
import { useNavigate } from 'react-router';
import svgPaths from '../../imports/MacBookPro166/svg-vk1owfvmuu';

function GandivaBowLogo({ size = 40, className = '' }: { size?: number; className?: string }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 48 48"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <path
        d="M 14 3 Q 40 24 14 45"
        stroke="#f97316"
        strokeWidth="3.5"
        fill="none"
        strokeLinecap="round"
      />
      <line x1="14" y1="3" x2="14" y2="45" stroke="#fbbf24" strokeWidth="1.2" strokeLinecap="round" />
      <line x1="14" y1="24" x2="38" y2="24" stroke="#fbbf24" strokeWidth="1.4" strokeLinecap="round" />
      <polygon points="36,20 44,24 36,28" fill="#f97316" />
      <circle cx="14" cy="3" r="1.5" fill="#fbbf24" />
      <circle cx="14" cy="45" r="1.5" fill="#fbbf24" />
    </svg>
  );
}

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');

  const handleGoogleLogin = () => navigate('/home');
  const handleFacebookLogin = () => navigate('/home');
  const handleEmailLogin = () => navigate('/home');

  return (
    <div className="min-h-screen w-full bg-black flex items-center justify-center p-4 overflow-hidden relative">
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[400px] bg-orange-500/10 rounded-full blur-[100px]" />
        <div className="absolute bottom-0 right-0 w-[400px] h-[400px] bg-yellow-400/5 rounded-full blur-[100px]" />
      </div>

      <div className="relative z-10 w-full max-w-md">
        <div className="flex items-center justify-center gap-3 mb-8">
          <GandivaBowLogo size={44} />
          <h1 className="text-white text-4xl font-bold" style={{ fontFamily: "'Eagle Lake', serif" }}>
            Gandiva
          </h1>
        </div>

        <div className="bg-[#0d0d0d] backdrop-blur-xl rounded-2xl p-8 shadow-2xl border border-white/5">
          <div className="flex justify-center mb-6">
            <div className="w-16 h-16 bg-orange-500/10 border border-orange-500/20 rounded-full flex items-center justify-center">
              <svg className="w-10 h-10" fill="none" preserveAspectRatio="none" viewBox="0 0 55 55">
                <path clipRule="evenodd" d={svgPaths.p37dbf600} fill="#f97316" fillRule="evenodd" />
                <path clipRule="evenodd" d={svgPaths.p2268b970} fill="#f97316" fillRule="evenodd" />
              </svg>
            </div>
          </div>

          <h2 className="text-center text-2xl md:text-3xl text-white mb-3 font-semibold">
            Log in or sign up
          </h2>
          <p className="text-center text-sm md:text-base text-gray-500 mb-8">
            Use your email or another service to continue with Gandiva
          </p>

          <div className="space-y-4">
            <button
              onClick={handleGoogleLogin}
              className="w-full bg-white hover:bg-gray-100 rounded-xl py-3 px-4 flex items-center justify-center gap-3 transition-all duration-200 shadow-lg hover:-translate-y-0.5"
            >
              <div className="w-6 h-6">
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
              <span className="text-base font-medium text-gray-900">Continue with Google</span>
            </button>

            <button
              onClick={handleFacebookLogin}
              className="w-full bg-white hover:bg-gray-100 rounded-xl py-3 px-4 flex items-center justify-center gap-3 transition-all duration-200 shadow-lg hover:-translate-y-0.5"
            >
              <div className="w-6 h-6">
                <svg className="w-full h-full" fill="none" preserveAspectRatio="none" viewBox="0 0 50 50">
                  <g clipPath="url(#clip0_1_106)">
                    <path d={svgPaths.p1213fb00} fill="#1877F2" />
                    <path d={svgPaths.p36add380} fill="white" />
                  </g>
                  <defs>
                    <clipPath id="clip0_1_106">
                      <rect fill="white" height="50" width="50" />
                    </clipPath>
                  </defs>
                </svg>
              </div>
              <span className="text-base font-medium text-gray-900">Continue with Facebook</span>
            </button>

            <div className="relative py-3">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-white/10" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-4 bg-[#0d0d0d] text-gray-600">or</span>
              </div>
            </div>

            <button
              onClick={handleEmailLogin}
              className="w-full bg-orange-500 hover:bg-orange-400 rounded-xl py-3 px-4 flex items-center justify-center gap-3 transition-all duration-200 shadow-lg hover:-translate-y-0.5"
              style={{ boxShadow: '0 0 30px rgba(249,115,22,0.2)' }}
            >
              <div className="w-6 h-6">
                <svg className="w-full h-full" fill="none" preserveAspectRatio="none" viewBox="0 0 50 50">
                  <path d={svgPaths.p3a483a00} fill="white" />
                </svg>
              </div>
              <span className="text-base font-medium text-black font-semibold">Continue with Email</span>
            </button>
          </div>

          <p className="text-center text-xs text-gray-600 mt-6 leading-relaxed">
            By continuing, you agree to Gandiva's{' '}
            <a href="#" className="text-orange-400 hover:text-orange-300 underline">Terms and Conditions</a>.{' '}
            Read our{' '}
            <a href="#" className="text-orange-400 hover:text-orange-300 underline">Privacy Policy</a>
          </p>
        </div>
      </div>
    </div>
  );
}
