import { Link } from "react-router-dom";
import AdminPanel from "../components/AdminPanel";

export default function AdminPage() {
  return (
    <main className="admin-page">
      <div className="admin-topbar">
        <Link className="ghost-button" to="/">
          Открыть kiosk-экран
        </Link>
      </div>
      <AdminPanel />
    </main>
  );
}
