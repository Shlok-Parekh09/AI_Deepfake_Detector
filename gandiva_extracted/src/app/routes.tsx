import { createBrowserRouter } from "react-router";
import Login from "./pages/Login";
import Home from "./pages/Home";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: Login,
  },
  {
    path: "/home",
    Component: Home,
  },
]);
