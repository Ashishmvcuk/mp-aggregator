import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const pkg = JSON.parse(fs.readFileSync(path.join(__dirname, 'package.json'), 'utf8'))

let scraperVersion = '0.0.0'
try {
  scraperVersion = fs.readFileSync(path.join(__dirname, '..', 'scraper', 'VERSION'), 'utf8').trim()
} catch {
  // optional file for local dev
}

const siteLabel = process.env.VITE_APP_VERSION || `v${pkg.version}`
const scraperLabel = process.env.VITE_SCRAPER_VERSION || `v${scraperVersion}`
const buildTime = process.env.VITE_BUILD_TIME || new Date().toISOString()

// GitHub Pages: project sites use /<repo-name>/; custom domains use '/'. CI sets DEPLOY_BASE.
const repoName = 'mp-aggregator'

export default defineConfig(({ mode }) => {
  const deployBase =
    process.env.DEPLOY_BASE ||
    (mode === 'production' ? `/${repoName}/` : '/')
  return {
    plugins: [react()],
    base: mode === 'development' ? '/' : deployBase.replace(/\/?$/, '/'),
    define: {
      __APP_VERSION__: JSON.stringify(siteLabel),
      __SCRAPER_VERSION__: JSON.stringify(scraperLabel),
      __BUILD_TIME__: JSON.stringify(buildTime),
    },
  }
})
