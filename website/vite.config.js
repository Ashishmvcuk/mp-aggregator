import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// GitHub Pages project sites use /<repo-name>/; local dev uses '/' for simpler URLs.
const repoName = 'mp-aggregator'

export default defineConfig(({ mode }) => ({
  plugins: [react()],
  base: mode === 'production' ? `/${repoName}/` : '/',
}))
