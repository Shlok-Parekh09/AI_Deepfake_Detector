import { motion } from "motion/react";
import { Mail, MapPin, Phone } from "lucide-react";

export function Contact() {
  return (
    <section className="relative py-20 px-6 overflow-hidden">
      {/* Decorative gradient */}
      <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-[800px] h-[400px] bg-gradient-to-t from-blue-600/20 to-transparent rounded-full blur-3xl" />

      <div className="relative z-10 max-w-7xl mx-auto">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          {/* Left side - Decorative icon */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="flex justify-center"
          >
            <div className="relative">
              {/* Hashtag/Grid pattern */}
              <div className="grid grid-cols-3 gap-4 p-12 bg-gradient-to-br from-blue-500/20 to-cyan-500/20 rounded-3xl backdrop-blur-sm border border-blue-400/20">
                {[...Array(9)].map((_, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, scale: 0 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    viewport={{ once: true }}
                    transition={{ delay: i * 0.1, duration: 0.4 }}
                    className={`w-16 h-16 rounded-2xl ${
                      i === 4
                        ? "bg-transparent"
                        : i % 2 === 0
                        ? "bg-gradient-to-br from-emerald-400 to-teal-500"
                        : "bg-gradient-to-br from-cyan-400 to-blue-500"
                    }`}
                  />
                ))}
              </div>

              {/* Glow effect */}
              <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/30 to-blue-500/30 rounded-3xl blur-2xl -z-10" />
            </div>
          </motion.div>

          {/* Right side - Contact info */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="space-y-8"
          >
            <h2 className="text-5xl md:text-6xl lg:text-7xl font-bold">
              Questions?
            </h2>

            <div className="space-y-6">
              <motion.div
                whileHover={{ x: 10 }}
                className="flex items-center gap-4 group"
              >
                <div className="w-12 h-12 bg-blue-600/20 rounded-xl flex items-center justify-center group-hover:bg-blue-600/30 transition-colors">
                  <MapPin className="w-6 h-6 text-blue-400" />
                </div>
                <div>
                  <p className="text-sm text-gray-400 uppercase tracking-wider">
                    Location
                  </p>
                  <p className="text-xl">Mumbai</p>
                </div>
              </motion.div>

              <motion.div
                whileHover={{ x: 10 }}
                className="flex items-center gap-4 group"
              >
                <div className="w-12 h-12 bg-blue-600/20 rounded-xl flex items-center justify-center group-hover:bg-blue-600/30 transition-colors">
                  <Phone className="w-6 h-6 text-blue-400" />
                </div>
                <div>
                  <p className="text-sm text-gray-400 uppercase tracking-wider">
                    Phone
                  </p>
                  <a
                    href="tel:9137143315"
                    className="text-xl hover:text-blue-400 transition-colors"
                  >
                    9137143315
                  </a>
                </div>
              </motion.div>

              <motion.div
                whileHover={{ x: 10 }}
                className="flex items-center gap-4 group"
              >
                <div className="w-12 h-12 bg-blue-600/20 rounded-xl flex items-center justify-center group-hover:bg-blue-600/30 transition-colors">
                  <Mail className="w-6 h-6 text-blue-400" />
                </div>
                <div>
                  <p className="text-sm text-gray-400 uppercase tracking-wider">
                    Email
                  </p>
                  <a
                    href="mailto:yugshah197@gmail.com"
                    className="text-xl hover:text-blue-400 transition-colors break-all"
                  >
                    yugshah197@gmail.com
                  </a>
                </div>
              </motion.div>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Footer */}
      <motion.div
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        className="text-center mt-20 pt-8 border-t border-gray-700/50"
      >
        <p className="text-gray-500 text-sm">
          © 2026 ZeroTruthLabs. Detecting deepfakes, protecting truth.
        </p>
      </motion.div>
    </section>
  );
}
