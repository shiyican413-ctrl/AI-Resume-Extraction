import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  base: "/AI-Resume-Extraction/",
  plugins: [react()],
  server: {
    port: 5173,
  },
});
