import { sveltekit } from "@sveltejs/kit/vite";

/** @type {import('vite').UserConfig} */
const config = {
  plugins: [sveltekit()],
  server: {
    watch: {
      // wsl2
      usePolling: true
    }
  }
};

export default config;
