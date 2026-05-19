import { motion } from "motion/react";
import { ArrowRight } from "lucide-react";

export function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center px-6 py-20 overflow-hidden">
      {/* Decorative gradient blobs */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl" />
      <div className="absolute bottom-0 left-0 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl" />

      <div className="relative z-10 max-w-7xl mx-auto grid md:grid-cols-2 gap-12 items-center">
        {/* Left content */}
        <motion.div
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8 }}
          className="space-y-8"
        >
          <div className="inline-block px-4 py-2 bg-blue-500/10 border border-blue-500/20 rounded-full backdrop-blur-sm">
            <p className="text-sm uppercase tracking-wider text-blue-300">
              Welcome to ZeroTruthLabs
            </p>
          </div>

          <div className="space-y-4">
            <h1 className="text-6xl md:text-7xl lg:text-8xl font-bold leading-tight">
              Let's get
              <br />
              <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
                digital
              </span>
            </h1>

            <p className="text-xl md:text-2xl text-gray-300 max-w-lg">
              Our new deepfake detector is here to help
            </p>
          </div>

          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="group px-8 py-4 bg-blue-600 hover:bg-blue-500 rounded-lg transition-all duration-300 flex items-center gap-3 shadow-lg shadow-blue-500/25"
          >
            <span className="uppercase tracking-wide">Let's Get Started</span>
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </motion.button>
        </motion.div>

        {/* Right content - decorative mockup */}
        <motion.div
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="hidden md:block relative"
        >
          <div className="relative bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-8 shadow-2xl border border-gray-700">
            <div className="aspect-video bg-gradient-to-br from-blue-900/50 to-purple-900/50 rounded-lg flex items-center justify-center backdrop-blur-sm">
              <div className="text-center space-y-4">
                <div className="w-20 h-20 mx-auto bg-blue-500/20 rounded-full flex items-center justify-center">
                  <div className="w-12 h-12 bg-blue-500 rounded-full animate-pulse" />
                </div>
                <p className="text-gray-400">Analyzing Video...</p>
              </div>
            </div>
          </div>

          {/* Floating decoration */}
          <motion.div
            animate={{ y: [0, -20, 0] }}
            transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
            className="absolute -top-8 -right-8 w-32 h-32 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-3xl opacity-20 blur-2xl"
          />
        </motion.div>
      </div>

      {/* Scroll indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
        className="absolute bottom-8 left-1/2 transform -translate-x-1/2"
      >
        <motion.div
          animate={{ y: [0, 10, 0] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="w-6 h-10 border-2 border-gray-500 rounded-full flex justify-center pt-2"
        >
          <div className="w-1.5 h-2 bg-gray-400 rounded-full" />
        </motion.div>
      </motion.div>
    </section>
  );
}
