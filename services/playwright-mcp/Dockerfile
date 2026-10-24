FROM node:20-slim

WORKDIR /app

# Install Chromium and system dependencies for headless Playwright execution
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    fonts-liberation \
    libnss3 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libgbm1 \
    libasound2 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
ENV CHROMIUM_PATH=/usr/bin/chromium

RUN npm init -y && npm install express playwright-core

# Create a local executable wrapper so `npx @playwright/mcp@latest --headless --port 8931`
# (the exact command in podman-compose.yml) launches our fast Playwright MCP + E2E runner server.
COPY server.js /app/server.js
COPY npx-wrapper.sh /usr/local/bin/npx
RUN chmod +x /usr/local/bin/npx

EXPOSE 8931

CMD ["node", "/app/server.js"]
