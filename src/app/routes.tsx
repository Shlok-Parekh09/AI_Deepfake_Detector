import { createBrowserRouter } from "react-router";
import Login from "./pages/Login";
import Home from "./pages/Home";
import HowItWorks from "./pages/HowItWorks";
import Analyze from "./pages/Analyze";
import AnalysisPage from "./pages/AnalysisPage";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: Login,
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
