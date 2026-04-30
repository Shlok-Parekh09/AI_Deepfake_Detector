import { createBrowserRouter } from "react-router";
import Home from "./pages/Home";
import HowItWorks from "./pages/HowItWorks";
import Features from "./pages/Features";
import Solutions from "./pages/Solutions";
import Analyze from "./pages/Analyze";
import AnalysisPage from "./pages/AnalysisPage";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: Home,
  },
  {
    path: "/home",
    Component: Home,
  },
  {
    path: "/features",
    Component: Features,
  },
  {
    path: "/solutions",
    Component: Solutions,
  },
  {
    path: "/how-it-works",
    Component: HowItWorks,
  },
  {
    path: "/analyze",
    Component: Analyze,
  },
  {
    path: "/analyze/:type",
    Component: AnalysisPage,
  },
]);
