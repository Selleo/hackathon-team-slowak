import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { HomePage } from "@/app/modules/home/Home.page.tsx";
import { LoginPage } from "@/app/modules/login/Login.page.tsx";
import { LogoutPage } from "@/app/modules/logout/Logout.page.tsx";
import { NotFoundPage } from "@/app/modules/notFound/NotFound.page.tsx";
import { RegisterPage } from "@/app/modules/register/Register.page.tsx";
import HomeLayout from "@/app/modules/home/Home.layout.tsx";
import { Toaster } from "@/components/ui/sonner.tsx";

function App() {
  return (
    <>
      <Toaster position="top-right" />
      <BrowserRouter>
        <Routes>
          <Route index element={<Navigate to="/home" />} />
          <Route path="/home" element={<HomeLayout />}>
            <Route index element={<HomePage />} />
          </Route>
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/logout" element={<LogoutPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </BrowserRouter>
    </>
  );
}

export default App;
