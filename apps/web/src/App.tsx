import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { HomePage } from "@/app/modules/Home/Home.page.tsx";
import { LoginPage } from "@/app/modules/Login/Login.page.tsx";
import { LogoutPage } from "@/app/modules/Logout/Logout.page.tsx";
import { NotFoundPage } from "@/app/modules/NotFound/NotFound.page.tsx";
import { RegisterPage } from "@/app/modules/Register/Register.page.tsx";
import HomeLayout from "@/app/modules/Home/Home.layout.tsx";
import { Toaster } from "@/components/ui/sonner.tsx";
import { ProtectedRoute } from "@/app/modules/Auth/ProtectedRoute.tsx";

function App() {
  return (
    <>
      <Toaster position="top-right" />
      <BrowserRouter>
        <Routes>
          <Route index element={<Navigate to="/home" />} />
          <Route
            element={
              <ProtectedRoute>
                <HomeLayout />
              </ProtectedRoute>
            }
          >
            <Route path="/home" element={<HomePage />} />
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
