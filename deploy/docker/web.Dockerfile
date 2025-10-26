FROM node:20-alpine

WORKDIR /app

ENV NEXT_TELEMETRY_DISABLED=1

# Install deps
COPY apps/web/package.json apps/web/pnpm-lock.yaml ./apps/web/
RUN corepack enable && cd apps/web && pnpm i

# Copy sources
COPY apps/web ./apps/web
COPY packages/common ./packages/common

WORKDIR /app/apps/web

EXPOSE 3000

CMD ["npm", "run", "dev", "--host"]

