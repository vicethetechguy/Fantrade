import fs from 'fs';
import path from 'path';

const ROOT_DIR = process.cwd();
const DIST_DIR = path.resolve(ROOT_DIR, 'dist');

function copyFolderSync(from: string, to: string) {
  if (!fs.existsSync(from)) return;
  fs.mkdirSync(to, { recursive: true });
  fs.cpSync(from, to, { recursive: true });
}

function copyFileSync(from: string, to: string) {
  if (!fs.existsSync(from)) return;
  fs.mkdirSync(path.dirname(to), { recursive: true });
  fs.copyFileSync(from, to);
}

export function buildDist() {
  console.log('[Build] Preparing production distribution in ./dist ...');
  fs.mkdirSync(DIST_DIR, { recursive: true });

  // 1. Copy all HTML files from root into dist
  const files = fs.readdirSync(ROOT_DIR);
  let htmlCount = 0;
  for (const file of files) {
    if (file.endsWith('.html')) {
      copyFileSync(path.join(ROOT_DIR, file), path.join(DIST_DIR, file));
      htmlCount++;
    }
  }
  console.log(`[Build] Copied ${htmlCount} HTML pages to ./dist.`);

  // 2. Copy assets directory
  const assetsDir = path.join(ROOT_DIR, 'assets');
  if (fs.existsSync(assetsDir)) {
    copyFolderSync(assetsDir, path.join(DIST_DIR, 'assets'));
    console.log('[Build] Copied assets/ directory to ./dist/assets.');
  }

  // 3. Copy public directory
  const publicDir = path.join(ROOT_DIR, 'public');
  if (fs.existsSync(publicDir)) {
    copyFolderSync(publicDir, path.join(DIST_DIR, 'public'));
    // Also copy fantrade-api.js directly into dist root as a fallback convenience
    if (fs.existsSync(path.join(publicDir, 'fantrade-api.js'))) {
      copyFileSync(path.join(publicDir, 'fantrade-api.js'), path.join(DIST_DIR, 'fantrade-api.js'));
    }
    console.log('[Build] Copied public/ directory to ./dist/public.');
  }

  console.log('[Build] Production build ready in ./dist!');
}

buildDist();
