import { RouterProvider } from 'react-router';
import { router } from './routes';
import TechnicalBackground from '../components/TechnicalBackground';

export default function App() {
  return (
    <>
      <TechnicalBackground />
      <RouterProvider router={router} />
    </>
  );
}
