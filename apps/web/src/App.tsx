import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { HomePage } from "@/app/modules/home/Home.page.tsx";
import { LoginPage } from "@/app/modules/login/Login.page.tsx";
import { LogoutPage } from "@/app/modules/logout/Logout.page.tsx";
import { NotFoundPage } from "@/app/modules/notFound/NotFound.page.tsx";
import { RegisterPage } from "@/app/modules/register/Register.page.tsx";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route index element={<Navigate to="/home" />} />
        <Route path="/home" element={<HomePage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/logout" element={<LogoutPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
