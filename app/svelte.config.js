import adapter from "@sveltejs/adapter-auto";
import { mdsvex } from "mdsvex";
import rehypeKatexSvelte from "rehype-katex-svelte";
import remarkMath from "remark-math";

/** @type {import('@sveltejs/kit').Config} */
const config = {
  kit: {
    adapter: adapter()
  },
  extensions: [".svelte", ".md"],
  preprocess: mdsvex({
    remarkPlugins: [remarkMath],
    rehypePlugins: [rehypeKatexSvelte],
    extensions: [".md"]
  })
};

export default config;
