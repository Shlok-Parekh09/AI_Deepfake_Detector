import { createBrowserRouter } from "react-router";
import Home from "./pages/Home";
import HowItWorks from "./pages/HowItWorks";
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
