import { Hero } from "./components/Hero";
import { FeatureCards } from "./components/FeatureCards";
import { Contact } from "./components/Contact";

export default function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900 text-white overflow-x-hidden">
      <Hero />
      <FeatureCards />
      <Contact />
    </div>
  );
}