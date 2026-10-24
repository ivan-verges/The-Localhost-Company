const express = require('express');
const { chromium } = require('playwright-core');

const app = express();
app.use(express.json());

const PORT = 8931;
const CHROMIUM_PATH = process.env.CHROMIUM_PATH || '/usr/bin/chromium';

// SSE endpoint for MCP compatibility (`http://playwright-mcp:8931/sse`)
app.get('/sse', (req, res) => {
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  res.write(`event: endpoint\ndata: /mcp/messages\n\n`);
});

app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'playwright-mcp', port: PORT });
});

// Execute live E2E Playwright scenario checks using real headless Chromium
app.post('/run-e2e', async (req, res) => {
  const targetUrl = req.body.target_url || 'http://dev-hermes:8080';
  let browser = null;

  try {
    browser = await chromium.launch({
      executablePath: CHROMIUM_PATH,
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
    });

    const page = await browser.newPage();
    const trace = [];

    // Scenario 1: Happy Path - Base price $100 -> apply OPENHUB20 -> $80
    trace.push(`[MCP tool: browser_navigate] -> ${targetUrl}`);
    await page.goto(targetUrl, { waitUntil: 'domcontentloaded', timeout: 10000 });

    const initialTotal = (await page.locator('[data-testid="total-amount"]').textContent() || '').trim();
    trace.push(`[MCP tool: browser_snapshot] Initial [data-testid="total-amount"] = "${initialTotal}"`);

    if (initialTotal !== '$100') {
      const domSnapshot = await page.content();
      await browser.close();
      return res.json({
        passed: false,
        scenario: 'Escenario Inicial: Precio Base de $100',
        expected: '$100',
        received: initialTotal,
        trace,
        dom_snapshot: domSnapshot.slice(0, 800)
      });
    }

    trace.push(`[MCP tool: browser_fill] [data-testid="coupon-input"] <- "OPENHUB20"`);
    await page.locator('[data-testid="coupon-input"]').fill('OPENHUB20');

    trace.push(`[MCP tool: browser_click] [data-testid="apply-btn"]`);
    await page.locator('[data-testid="apply-btn"]').click();

    const discountedTotal = (await page.locator('[data-testid="total-amount"]').textContent() || '').trim();
    const errorVisibleHappy = await page.locator('[data-testid="error-banner"]').isVisible();
    trace.push(`[MCP tool: browser_snapshot] After OPENHUB20 -> [data-testid="total-amount"] = "${discountedTotal}", error-banner visible = ${errorVisibleHappy}`);

    if (discountedTotal !== '$80' || errorVisibleHappy) {
      const domSnapshot = await page.locator('body').innerHTML();
      await browser.close();
      return res.json({
        passed: false,
        scenario: 'Scenario 1: Camino Feliz - Aplicación del cupón válido OPENHUB20 (20% de descuento)',
        expected: '$80 (y error-banner oculto)',
        received: `${discountedTotal} (error-banner visible: ${errorVisibleHappy})`,
        trace,
        dom_snapshot: domSnapshot.slice(0, 900)
      });
    }

    // Scenario 2: Edge Case - Invalid coupon -> error banner visible & total stays $100
    trace.push(`[MCP tool: browser_navigate] -> ${targetUrl} (Reset para Escenario 2)`);
    await page.goto(targetUrl, { waitUntil: 'domcontentloaded', timeout: 10000 });

    trace.push(`[MCP tool: browser_fill] [data-testid="coupon-input"] <- "INVALIDO99"`);
    await page.locator('[data-testid="coupon-input"]').fill('INVALIDO99');

    trace.push(`[MCP tool: browser_click] [data-testid="apply-btn"]`);
    await page.locator('[data-testid="apply-btn"]').click();

    const invalidTotal = (await page.locator('[data-testid="total-amount"]').textContent() || '').trim();
    const errorVisibleInvalid = await page.locator('[data-testid="error-banner"]').isVisible();
    const errorText = (await page.locator('[data-testid="error-banner"]').textContent() || '').trim();
    trace.push(`[MCP tool: browser_snapshot] After INVALIDO99 -> [data-testid="total-amount"] = "${invalidTotal}", error-banner visible = ${errorVisibleInvalid} ("${errorText}")`);

    if (invalidTotal !== '$100' || !errorVisibleInvalid) {
      const domSnapshot = await page.locator('body').innerHTML();
      await browser.close();
      return res.json({
        passed: false,
        scenario: 'Scenario 2: Caso Borde - Ingreso de cupón inválido muestra error y mantiene total en $100',
        expected: '$100 y [data-testid="error-banner"] visible',
        received: `Total=${invalidTotal}, error-banner visible=${errorVisibleInvalid}`,
        trace,
        dom_snapshot: domSnapshot.slice(0, 900)
      });
    }

    await browser.close();
    return res.json({
      passed: true,
      scenario: 'Todos los escenarios Gherkin (Happy Path OPENHUB20 -> $80 & Invalid Coupon -> $100 + Error Banner)',
      expected: 'Scenario 1 = $80, Scenario 2 = $100 + Error Banner',
      received: 'Scenario 1 = $80, Scenario 2 = $100 + Error Banner',
      trace
    });
  } catch (err) {
    if (browser) {
      try { await browser.close(); } catch (_) {}
    }
    return res.json({
      passed: false,
      scenario: 'Ejecución de navegador Playwright MCP',
      expected: 'Aplicación accesible y selectores data-testid presentes',
      received: String(err.message || err),
      trace: [String(err)],
      dom_snapshot: ''
    });
  }
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Playwright MCP Server listening on port ${PORT} (headless Chromium ready)`);
});
