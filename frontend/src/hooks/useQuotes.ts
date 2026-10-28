import { useCallback, useState } from "react";
import type { Comparison, QuoteRequest } from "../types";

export function useQuotes() {
  const [result, setResult] = useState<Comparison | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const run = useCallback(async (request: QuoteRequest) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/quotes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(request),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setResult((await res.json()) as Comparison);
    } catch (e) {
      setResult(null);
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }, []);

  return { result, loading, error, run };
}
