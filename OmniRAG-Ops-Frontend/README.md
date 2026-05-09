# OmniRAG-Ops Frontend

Management dashboard for the OmniRAG-Ops ingestion engine.

Built with **Next.js 15** (App Router), **Tailwind CSS**, **Shadcn/UI**, **TanStack Query**, and **Axios**.

## Getting started

```bash
cp .env.example .env.local
# Set NEXT_PUBLIC_API_URL to your backend URL
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Pages

| Route | Description |
|-------|-------------|
| `/login` | JWT authentication |
| `/dashboard` | RAG operations overview |
| `/ingest` | Document upload and processing |
| `/collections` | Vector collection management |
