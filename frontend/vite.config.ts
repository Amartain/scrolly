import { svelte } from '@sveltejs/vite-plugin-svelte';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [svelte()],
  build: { outDir: '../src/scrolly/static', emptyOutDir: true },
  server: { proxy: { '/api': 'http://127.0.0.1:4748' } },
});
