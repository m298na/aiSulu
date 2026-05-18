import { Route, Routes } from "react-router-dom";
import KioskPage from "./pages/KioskPage";
import AdminPage from "./pages/AdminPage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<KioskPage />} />
      <Route path="/admin" element={<AdminPage />} />
    </Routes>
  );
}
