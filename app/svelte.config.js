import adapter from "@sveltejs/adapter-node";
import { mdsvex } from "mdsvex";
import rehypeKatexSvelte from "rehype-katex-svelte";
import remarkMath from "remark-math";
import remarkToc from "remark-toc";
import rehypeSlug from "rehype-slug";
import rehypeAutolinkHeadings from "rehype-autolink-headings";

/** @type {import('@sveltejs/kit').Config} */
const config = {
  kit: {
    adapter: adapter()
  },
  extensions: [".svelte", ".md"],
  preprocess: mdsvex({
    remarkPlugins: [remarkMath, [remarkToc, { tight: true }]],
    rehypePlugins: [rehypeKatexSvelte, rehypeSlug, rehypeAutolinkHeadings],
    extensions: [".md"]
  })
};

export default config;
