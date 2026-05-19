import { motion } from "motion/react";
import { Navigation, Eye, Lightbulb } from "lucide-react";

const features = [
  {
    icon: Navigation,
    title: "Getting lost in the digital maze?",
    description:
      "Stop the second-guessing. Our tech scans for the tiny AI 'glitches' the human eye misses, guiding you straight back to the truth.",
    gradient: "from-blue-600 to-blue-400",
  },
  {
    icon: Eye,
    title: "Is your 'gut feeling' enough to spot fake?",
    description:
      "Intuition isn't enough anymore. We provide a technical reality check, analyzing pixels and metadata to ensure you aren't being played by a script.",
    gradient: "from-cyan-600 to-cyan-400",
  },
  {
    icon: Lightbulb,
    title: "Feeling like you're left in the dark?",
    description:
      "Don't let misinformation dim your vision. We expose the hidden data fingerprints in deepfakes, shining a light on what's real and what's rendered.",
    gradient: "from-blue-700 to-cyan-500",
  },
];

export function FeatureCards() {
  return (
    <section className="relative py-20 px-6">
      <div className="max-w-7xl mx-auto space-y-20">
        {/* Main tagline */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="text-center space-y-4"
        >
          <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold max-w-4xl mx-auto leading-tight">
            Not Every Video is real in this world!
            <br />
            <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
              We're here to help.
            </span>
          </h2>
        </motion.div>

        {/* Feature cards */}
        <div className="grid md:grid-cols-3 gap-6 lg:gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: index * 0.2 }}
              whileHover={{ scale: 1.05, y: -10 }}
              className="group relative"
            >
              <div
                className={`relative h-full p-8 rounded-3xl bg-gradient-to-br ${feature.gradient} overflow-hidden`}
              >
                {/* Background pattern */}
                <div className="absolute inset-0 opacity-10">
                  <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_120%,rgba(255,255,255,0.1),transparent)]" />
                </div>

                {/* Content */}
                <div className="relative z-10 space-y-6">
                  <div className="w-14 h-14 bg-white/20 rounded-2xl flex items-center justify-center backdrop-blur-sm group-hover:bg-white/30 transition-colors">
                    <feature.icon className="w-7 h-7 text-white" />
                  </div>

                  <h3 className="text-2xl font-bold uppercase tracking-tight leading-tight">
                    {feature.title}
                  </h3>

                  <p className="text-white/90 leading-relaxed">
                    {feature.description}
                  </p>
                </div>

                {/* Hover effect */}
                <div className="absolute inset-0 bg-white/0 group-hover:bg-white/5 transition-colors duration-300" />
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
