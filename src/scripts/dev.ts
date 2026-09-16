import { startDatabase } from '../database/run-db.js';
import { startServer } from '../api/server.js';
import { config } from '../config/index.js';
import net from 'net';

async function isPortInUse(port: number): Promise<boolean> {
  return new Promise((resolve) => {
    const server = net.createServer();
    server.once('error', (err: any) => {
      if (err.code === 'EADDRINUSE') resolve(true);
      else resolve(false);
    });
    server.once('listening', () => {
      server.close();
      resolve(false);
    });
    server.listen(port);
  });
}

async function main() {
  console.log('[Dev] Starting Fantrade Development Environment...');

  const dbInUse = await isPortInUse(5432);
  if (!dbInUse) {
    console.log('[Dev] No active database detected on port 5432. Launching embedded PostgreSQL...');
    await startDatabase(5432, 'fantrade');
  } else {
    console.log('[Dev] PostgreSQL database already active on port 5432.');
  }

  // Start API server
  startServer(config.port);
}

main().catch((err) => {
  console.error('[Dev Fatal Error]:', err);
  process.exit(1);
});
