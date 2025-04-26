import path from "path";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// https://vite.dev/config/
export default defineConfig({
	plugins: [react(), tailwindcss()],
	resolve: {
		alias: {
			"@": path.resolve(__dirname, "./src"),
		},
	},
	preview: {
		port: 8080,
		strictPort: true,
	},
	server: {
		port: 8080,
		strictPort: true,
		host: true,
		origin: "http://0.0.0.0:8080",
	},
});
