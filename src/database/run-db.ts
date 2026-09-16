import { spawn, execSync } from 'child_process';
import * as path from 'path';
import * as fs from 'fs';

const rootDir = process.cwd();
const dataDir = path.resolve(rootDir, '.data');
const pgsqlDir = path.resolve(dataDir, 'pgsql');
const pgdataDir = path.resolve(dataDir, 'pgdata');
const binDir = path.resolve(pgsqlDir, 'bin');

export async function startDatabase(port = 5432, dbName = 'fantrade') {
  const postgresExe = path.resolve(binDir, 'postgres.exe');
  const initdbExe = path.resolve(binDir, 'initdb.exe');
  const createdbExe = path.resolve(binDir, 'createdb.exe');

  if (!fs.existsSync(postgresExe)) {
    console.error(`[Database] PostgreSQL binary not found at: ${postgresExe}`);
    console.error(`[Database] Please ensure portable PostgreSQL is extracted to: ${pgsqlDir}`);
    throw new Error(`PostgreSQL binary not found at ${postgresExe}`);
  }

  // 1. Initialize data cluster if it doesn't exist
  if (!fs.existsSync(pgdataDir) || !fs.existsSync(path.resolve(pgdataDir, 'PG_VERSION'))) {
    console.log(`[Database] Initializing cluster at: ${pgdataDir}...`);
    fs.mkdirSync(pgdataDir, { recursive: true });
    execSync(`"${initdbExe}" -D "${pgdataDir}" -U postgres -A trust -E UTF8 --locale=C`, {
      stdio: 'inherit',
    });
    console.log(`[Database] Cluster initialized successfully.`);
  }

  // 2. Start postgres process
  console.log(`[Database] Starting PostgreSQL server on port ${port}...`);
  const pgProcess = spawn(`"${postgresExe}"`, ['-D', `"${pgdataDir}"`, '-p', String(port)], {
    shell: true,
    stdio: ['ignore', 'pipe', 'pipe'],
  });

  pgProcess.stdout?.on('data', (data) => {
    const msg = data.toString();
    if (msg.includes('ready to accept connections')) {
      console.log(`[Database] PostgreSQL is ready and accepting connections on port ${port}.`);
    }
  });

  pgProcess.stderr?.on('data', (data) => {
    const msg = data.toString();
    if (msg.includes('ready to accept connections')) {
      console.log(`[Database] PostgreSQL is ready and accepting connections on port ${port}.`);
    } else if (msg.toLowerCase().includes('error') || msg.toLowerCase().includes('fatal')) {
      console.error(`[Database Server Error]: ${msg}`);
    }
  });

  // Wait for server to be responsive
  await new Promise((resolve) => setTimeout(resolve, 3000));

  // 3. Ensure database exists
  try {
    console.log(`[Database] Ensuring database "${dbName}" exists...`);
    execSync(`"${createdbExe}" -U postgres -p ${port} ${dbName}`, {
      stdio: 'ignore',
    });
    console.log(`[Database] Database "${dbName}" verified.`);
  } catch {
    // Already exists or created
    console.log(`[Database] Database "${dbName}" is ready.`);
  }

  const shutdown = () => {
    console.log('\n[Database] Shutting down PostgreSQL...');
    try {
      const pgctlExe = path.resolve(binDir, 'pg_ctl.exe');
      if (fs.existsSync(pgctlExe)) {
        execSync(`"${pgctlExe}" -D "${pgdataDir}" stop -m fast`, { stdio: 'inherit' });
      } else {
        pgProcess.kill();
      }
      console.log('[Database] PostgreSQL stopped successfully.');
    } catch {
      pgProcess.kill();
    }
    process.exit(0);
  };

  process.on('SIGINT', shutdown);
  process.on('SIGTERM', shutdown);

  return pgProcess;
}

if (process.argv[1]?.endsWith('run-db.ts')) {
  startDatabase().catch((err) => {
    console.error('[Database] Fatal:', err.message);
    process.exit(1);
  });
}
