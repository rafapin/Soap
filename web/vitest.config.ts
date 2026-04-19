import { defineConfig } from 'vitest/config';
import { sveltekit } from '@sveltejs/kit/vite';
import { svelteTesting } from '@testing-library/svelte/vite';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  plugins: [tailwindcss(), sveltekit(), svelteTesting({ resolveBrowser: true })],
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test-setup.ts']
  }
});
