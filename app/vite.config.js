import { sveltekit } from "@sveltejs/kit/vite";
import replace from "@rollup/plugin-replace";

let replaceVersion = () =>
  replace({
    __VERSION__: process.env.npm_package_version,
    __BUILD_TIME__: new Date().toISOString(),
    preventAssignment: true
  });

/** @type {import('vite').UserConfig} */
const config = {
  plugins: [sveltekit(), replaceVersion()],
  server: {
    watch: {
      // wsl2
      usePolling: true
    }
  }
};

export default config;
