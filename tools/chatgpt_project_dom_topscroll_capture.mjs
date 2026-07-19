import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const MAX_DOM_BYTES = 32 * 1024 * 1024;
const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const defaultCaptureRoot = path.join(projectRoot, 'runtime', 'artifacts', 'chatgpt-project-captures');

function usage() {
  return [
    'Usage: node tools/chatgpt_project_dom_topscroll_capture.mjs [options]',
    '  --cdp-url <url>   Chrome DevTools HTTP endpoint (default: http://127.0.0.1:9222)',
    '  --page <text>     Select a page whose URL contains text',
    '  --output <path>   Output directory beneath the project root',
    '  --steps <count>   Maximum upward scroll steps (default: 200, maximum: 2000)',
  ].join('\n');
}

function parseArgs(argv) {
  const options = { cdpUrl: 'http://127.0.0.1:9222', page: '', output: '', steps: 200 };
  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === '--help' || token === '-h') return { ...options, help: true };
    const value = argv[index + 1];
    if (!value || value.startsWith('--')) throw new Error(`missing value for ${token}`);
    if (token === '--cdp-url') options.cdpUrl = value;
    else if (token === '--page') options.page = value;
    else if (token === '--output') options.output = value;
    else if (token === '--steps') options.steps = Number(value);
    else throw new Error(`unknown option: ${token}`);
    index += 1;
  }
  if (!Number.isInteger(options.steps) || options.steps <= 0 || options.steps > 2000) {
    throw new Error('steps must be an integer between 1 and 2000');
  }
  return options;
}

function projectOwnedOutput(requested) {
  const timestamp = new Date().toISOString().replaceAll(':', '-').replaceAll('.', '-');
  const resolved = path.resolve(requested || path.join(defaultCaptureRoot, `dom-${timestamp}`));
  const relative = path.relative(projectRoot, resolved);
  if (!relative || relative.startsWith('..') || path.isAbsolute(relative)) {
    throw new Error('output must resolve beneath the NexusNet project root');
  }
  return resolved;
}

async function selectPage(cdpUrl, pageMatch) {
  const response = await fetch(new URL('/json/list', cdpUrl), { signal: AbortSignal.timeout(5000) });
  if (!response.ok) throw new Error(`CDP target discovery failed: ${response.status}`);
  const pages = (await response.json()).filter((target) => target.type === 'page' && target.webSocketDebuggerUrl);
  const selected = pages.find((target) => !pageMatch || String(target.url || '').includes(pageMatch));
  if (!selected) throw new Error('no matching CDP page target is available');
  return selected;
}

async function evaluate(webSocketUrl, expression) {
  const socket = new WebSocket(webSocketUrl);
  await new Promise((resolve, reject) => {
    socket.addEventListener('open', resolve, { once: true });
    socket.addEventListener('error', () => reject(new Error('CDP WebSocket connection failed')), { once: true });
  });
  const result = await new Promise((resolve, reject) => {
    const id = 1;
    socket.addEventListener('message', (event) => {
      const payload = JSON.parse(String(event.data));
      if (payload.id !== id) return;
      if (payload.error) reject(new Error(payload.error.message || 'CDP evaluation failed'));
      else resolve(payload.result?.result?.value);
    });
    socket.send(JSON.stringify({
      id,
      method: 'Runtime.evaluate',
      params: { expression, awaitPromise: true, returnByValue: true },
    }));
  });
  socket.close();
  return result;
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  if (options.help) {
    console.log(usage());
    return;
  }
  const outputRoot = projectOwnedOutput(options.output);
  await mkdir(outputRoot, { recursive: true });
  const page = await selectPage(options.cdpUrl, options.page);
  const expression = `(async () => {
    const limit = ${options.steps};
    const candidates = [document.scrollingElement, ...document.querySelectorAll('main, [role="main"], [class*="scroll"]')]
      .filter(Boolean);
    const scroller = candidates.sort((a, b) => b.scrollHeight - a.scrollHeight)[0] || document.documentElement;
    let steps = 0;
    while (scroller.scrollTop > 0 && steps < limit) {
      scroller.scrollTop = Math.max(0, scroller.scrollTop - Math.max(480, scroller.clientHeight * 0.8));
      await new Promise((resolve) => setTimeout(resolve, 120));
      steps += 1;
    }
    return {
      captured_at: new Date().toISOString(),
      title: document.title,
      url: location.href,
      reached_top: scroller.scrollTop === 0,
      scroll_steps: steps,
      html: document.documentElement.outerHTML,
    };
  })()`;
  const capture = await evaluate(page.webSocketDebuggerUrl, expression);
  if (!capture || typeof capture.html !== 'string') throw new Error('page returned no DOM capture');
  if (Buffer.byteLength(capture.html, 'utf8') > MAX_DOM_BYTES) throw new Error('DOM capture exceeds 32 MiB');
  await writeFile(path.join(outputRoot, 'page.json'), JSON.stringify(capture, null, 2), 'utf8');
  console.log(JSON.stringify({ output_root: path.relative(projectRoot, outputRoot), reached_top: capture.reached_top }));
}

main().catch((error) => {
  console.error(`capture failed: ${error.message}`);
  process.exitCode = 1;
});
