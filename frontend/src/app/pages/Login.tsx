import { useState } from 'react';
import { useNavigate } from 'react-router';
import svgPaths from '../../imports/MacBookPro166/svg-vk1owfvmuu';
import BrandLogo from '../components/BrandLogo';

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');

  const handleGoogleLogin = () => {
    // Mock login - in production, implement OAuth
    navigate('/home');
  };

  const handleFacebookLogin = () => {
    // Mock login - in production, implement OAuth
    navigate('/home');
  };

  const handleEmailLogin = () => {
    // Mock login - in production, implement email authentication
    navigate('/home');
  };

  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center p-4 overflow-hidden relative">
      {/* Animated background gradients */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-1/2 -left-1/2 w-full h-full bg-blue-500/10 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-1/2 -right-1/2 w-full h-full bg-purple-500/10 rounded-full blur-3xl"></div>
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
        <div className="bg-slate-800/50 backdrop-blur-xl rounded-2xl p-8 shadow-2xl border border-slate-700/50">
          {/* Profile Icon */}
          <div className="flex justify-center mb-6">
            <div className="w-16 h-16 bg-blue-500/20 rounded-full flex items-center justify-center">
              <svg className="w-10 h-10" fill="none" preserveAspectRatio="none" viewBox="0 0 55 55">
                <path clipRule="evenodd" d={svgPaths.p37dbf600} fill="#60A5FA" fillRule="evenodd" />
                <path clipRule="evenodd" d={svgPaths.p2268b970} fill="#60A5FA" fillRule="evenodd" />
              </svg>
            </div>
          </div>

          {/* Title */}
          <h2 className="text-center text-2xl md:text-3xl text-white mb-3 font-semibold">
            Log in or sign up
          </h2>

          {/* Subtitle */}
          <p className="text-center text-sm md:text-base text-slate-400 mb-8">
            Use your email or another service to continue with SynPhi
          </p>

          {/* Login Buttons */}
          <div className="space-y-4">
            {/* Google Login */}
            <button
              onClick={handleGoogleLogin}
              className="w-full bg-white hover:bg-gray-50 rounded-xl py-3 px-4 flex items-center justify-center gap-3 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
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
              <span className="text-base md:text-lg font-medium text-gray-900">
                Continue with Google
              </span>
            </button>

            {/* Facebook Login */}
            <button
              onClick={handleFacebookLogin}
              className="w-full bg-white hover:bg-gray-50 rounded-xl py-3 px-4 flex items-center justify-center gap-3 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
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
              <span className="text-base md:text-lg font-medium text-gray-900">
                Continue with Facebook
              </span>
            </button>

            {/* Divider */}
            <div className="relative py-3">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-slate-600"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-4 bg-slate-800/50 text-slate-400">or</span>
              </div>
            </div>

            {/* Email Login */}
            <button
              onClick={handleEmailLogin}
              className="w-full bg-blue-600 hover:bg-blue-700 rounded-xl py-3 px-4 flex items-center justify-center gap-3 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
            >
              <div className="w-6 h-6">
                <svg className="w-full h-full" fill="none" preserveAspectRatio="none" viewBox="0 0 50 50">
                  <path d={svgPaths.p3a483a00} fill="white" />
                </svg>
              </div>
              <span className="text-base md:text-lg font-medium text-white">
                Continue with Email
              </span>
            </button>
          </div>

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
