/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly NEXT_PUBLIC_API_URL: string;
  readonly NEXT_PUBLIC_APP_NAME: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

declare namespace NodeJS {
  interface ProcessEnv {
    NEXT_PUBLIC_API_URL: string;
    NEXT_PUBLIC_APP_NAME: string;
  }
}
