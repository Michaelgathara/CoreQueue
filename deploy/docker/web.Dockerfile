FROM node:20-alpine

WORKDIR /app

ENV NEXT_TELEMETRY_DISABLED=1

# Copy sources first
COPY apps/web/package.json apps/web/pnpm-lock.yaml ./apps/web/
COPY apps/web ./apps/web
COPY packages/common ./packages/common

# Install deps after sources are in place
RUN corepack enable && cd apps/web && pnpm i

WORKDIR /app/apps/web

EXPOSE 3000

CMD ["npm", "run", "dev", "--host"]

