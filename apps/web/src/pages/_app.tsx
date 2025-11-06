import "src/styles/globals.css";
import type { AppProps } from "next/app";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";
import { TopNav } from "src/components/Layout/TopNav";

export default function App({ Component, pageProps }: AppProps) {
  const [client] = useState(() => new QueryClient());
  return (
    <QueryClientProvider client={client}>
      <TopNav />
      <Component {...pageProps} />
    </QueryClientProvider>
  );
}
