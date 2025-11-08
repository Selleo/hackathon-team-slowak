import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.tsx";
import { QueryClientContext } from "@tanstack/react-query";
import { queryClient } from "@/app/api/queryClient.ts";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientContext value={queryClient}>
      <App />
    </QueryClientContext>
  </StrictMode>,
);
