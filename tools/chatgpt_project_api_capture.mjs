import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const MAX_RESPONSE_BYTES = 16 * 1024 * 1024;
const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const defaultCaptureRoot = path.join(projectRoot, 'runtime', 'artifacts', 'chatgpt-project-captures');

function usage() {
  return [
    'Usage: node tools/chatgpt_project_api_capture.mjs [options]',
    '  --cdp-url <url>       Chrome DevTools HTTP endpoint (default: http://127.0.0.1:9222)',
    '  --duration <seconds>  Bounded capture duration (default: 30, maximum: 600)',
    '  --match <text>        Capture only response URLs containing text (repeatable)',
    '  --page <text>         Select a page whose URL contains text',
    '  --output <path>       Output directory beneath the project root',
  ].join('\n');
}

function parseArgs(argv) {
  const options = { cdpUrl: 'http://127.0.0.1:9222', duration: 30, matches: [], page: '', output: '' };
  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === '--help' || token === '-h') return { ...options, help: true };
    const value = argv[index + 1];
    if (!value || value.startsWith('--')) throw new Error(`missing value for ${token}`);
    if (token === '--cdp-url') options.cdpUrl = value;
    else if (token === '--duration') options.duration = Number(value);
    else if (token === '--match') options.matches.push(value);
    else if (token === '--page') options.page = value;
    else if (token === '--output') options.output = value;
    else throw new Error(`unknown option: ${token}`);
    index += 1;
  }
  if (!Number.isFinite(options.duration) || options.duration <= 0 || options.duration > 600) {
    throw new Error('duration must be between 1 and 600 seconds');
  }
  return options;
}

function projectOwnedOutput(requested, prefix) {
  const timestamp = new Date().toISOString().replaceAll(':', '-').replaceAll('.', '-');
  const resolved = path.resolve(requested || path.join(defaultCaptureRoot, `${prefix}-${timestamp}`));
  const relative = path.relative(projectRoot, resolved);
  if (!relative || relative.startsWith('..') || path.isAbsolute(relative)) {
    throw new Error('output must resolve beneath the NexusNet project root');
  }
  return resolved;
}

async function selectPage(cdpUrl, pageMatch) {
  const endpoint = new URL('/json/list', cdpUrl).toString();
  const response = await fetch(endpoint, { signal: AbortSignal.timeout(5000) });
  if (!response.ok) throw new Error(`CDP target discovery failed: ${response.status}`);
  const targets = await response.json();
  const pages = targets.filter((target) => target.type === 'page' && target.webSocketDebuggerUrl);
  const selected = pages.find((target) => !pageMatch || String(target.url || '').includes(pageMatch));
  if (!selected) throw new Error('no matching CDP page target is available');
  return selected;
}

function connect(webSocketUrl) {
  const socket = new WebSocket(webSocketUrl);
  const pending = new Map();
  const listeners = new Set();
  let nextId = 1;
  socket.addEventListener('message', (event) => {
    const payload = JSON.parse(String(event.data));
    if (payload.id && pending.has(payload.id)) {
      const { resolve, reject } = pending.get(payload.id);
      pending.delete(payload.id);
      if (payload.error) reject(new Error(payload.error.message || 'CDP command failed'));
      else resolve(payload.result || {});
      return;
    }
    if (payload.method) for (const listener of listeners) listener(payload);
  });
  const ready = new Promise((resolve, reject) => {
    socket.addEventListener('open', resolve, { once: true });
    socket.addEventListener('error', () => reject(new Error('CDP WebSocket connection failed')), { once: true });
  });
  return {
    ready,
    onEvent(listener) { listeners.add(listener); },
    async send(method, params = {}) {
      await ready;
      const id = nextId;
      nextId += 1;
      return new Promise((resolve, reject) => {
        pending.set(id, { resolve, reject });
        socket.send(JSON.stringify({ id, method, params }));
      });
    },
    close() { socket.close(); },
  };
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  if (options.help) {
    console.log(usage());
    return;
  }
  const outputRoot = projectOwnedOutput(options.output, 'api');
  await mkdir(outputRoot, { recursive: true });
  const page = await selectPage(options.cdpUrl, options.page);
  const cdp = connect(page.webSocketDebuggerUrl);
  const captures = [];
  const jobs = new Set();
  cdp.onEvent((event) => {
    if (event.method !== 'Network.responseReceived') return;
    const response = event.params?.response || {};
    const url = String(response.url || '');
    if (options.matches.length && !options.matches.some((match) => url.includes(match))) return;
    if (!['Fetch', 'XHR'].includes(String(event.params?.type || ''))) return;
    const job = cdp.send('Network.getResponseBody', { requestId: event.params.requestId })
      .then(async ({ body = '', base64Encoded = false }) => {
        const bytes = Buffer.byteLength(body, base64Encoded ? 'base64' : 'utf8');
        if (bytes > MAX_RESPONSE_BYTES) return;
        const sequence = String(captures.length + 1).padStart(4, '0');
        const record = {
          captured_at: new Date().toISOString(),
          url,
          status: Number(response.status || 0),
          mime_type: String(response.mimeType || ''),
          base64_encoded: Boolean(base64Encoded),
          body,
        };
        const filename = `${sequence}-${event.params.requestId.replaceAll('.', '-')}.json`;
        await writeFile(path.join(outputRoot, filename), JSON.stringify(record, null, 2), 'utf8');
        captures.push({ filename, url, status: record.status, bytes });
      })
      .catch(() => undefined)
      .finally(() => jobs.delete(job));
    jobs.add(job);
  });
  await cdp.send('Network.enable', { maxTotalBufferSize: MAX_RESPONSE_BYTES * 2, maxResourceBufferSize: MAX_RESPONSE_BYTES });
  await new Promise((resolve) => setTimeout(resolve, options.duration * 1000));
  await Promise.allSettled([...jobs]);
  await writeFile(
    path.join(outputRoot, 'manifest.json'),
    JSON.stringify({ page_url: page.url, capture_count: captures.length, captures }, null, 2),
    'utf8',
  );
  cdp.close();
  console.log(JSON.stringify({ output_root: path.relative(projectRoot, outputRoot), capture_count: captures.length }));
}

main().catch((error) => {
  console.error(`capture failed: ${error.message}`);
  process.exitCode = 1;
});
