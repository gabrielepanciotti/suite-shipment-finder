import {
  AppShell,
  Button,
  EmptyState,
  Skeleton,
  VistaProvider,
  useVista,
} from "@suite/design-system";
import { LanguageSwitcher, useLanguage } from "@suite/i18n";
import {
  CircleAlert,
  ListFilter,
  Search,
  Settings,
  Star,
} from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { useQuotes } from "./hooks/useQuotes";
import { vistaFetcher } from "./lib/vista";
import { Cerca } from "./pages/Cerca";
import { Impostazioni } from "./pages/Impostazioni";
import { offerKey, Risultati } from "./pages/Risultati";
import { Salvati } from "./pages/Salvati";
import type { Offer, QuoteRequest, SavedOffer } from "./types";

const storageKey = "shipmentfinder.saved-offers";

const sectionIcons = {
  cerca: Search,
  risultati: ListFilter,
  salvati: Star,
  impostazioni: Settings,
};

function readSaved(): SavedOffer[] {
  try {
    const parsed: unknown = JSON.parse(localStorage.getItem(storageKey) ?? "[]");
    return Array.isArray(parsed) ? (parsed as SavedOffer[]) : [];
  } catch {
    return [];
  }
}

function useSources(section: string) {
  const [sources, setSources] = useState<string[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch("/api/sources");
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const body = (await response.json()) as { sources: string[] };
      setSources(body.sources);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (section === "impostazioni" && sources === null && !loading) {
      void load();
    }
  }, [load, loading, section, sources]);

  return { sources, loading, error, load };
}

interface SidebarNavigationProps {
  section: string;
  sezioniVisibili: ReturnType<typeof useVista>["sezioniVisibili"];
  t: ReturnType<typeof useLanguage>["t"];
}

function SidebarNavigation({
  section,
  sezioniVisibili,
  t,
}: SidebarNavigationProps) {
  const item = (id: string, label: string) => {
    const Icon = sectionIcons[id as keyof typeof sectionIcons] ?? Search;
    return (
      <AppShell.Sidebar.Item
        key={id}
        icon={<Icon aria-hidden />}
        label={label}
        active={section === id}
        onClick={() => (location.hash = `#${id}`)}
      />
    );
  };
  const settings = sezioniVisibili.find((item) => item.id === "impostazioni");

  return (
    <AppShell.Sidebar
      settingsItem={
        settings ? item(settings.id, t(`nav.${settings.id}`)) : undefined
      }
    >
      {sezioniVisibili
        .filter((sezione) => sezione.id !== "impostazioni")
        .slice(0, 7)
        .map((sezione) => item(sezione.id, t(`nav.${sezione.id}`)))}
    </AppShell.Sidebar>
  );
}

interface FinderContentProps {
  section: string;
  result: ReturnType<typeof useQuotes>["result"];
  loading: boolean;
  error: string | null;
  saved: SavedOffer[];
  sources: string[] | null;
  sourcesLoading: boolean;
  sourcesError: string | null;
  onSearch: (request: QuoteRequest) => void;
  onRetry: () => void;
  onSave: (offer: Offer) => void;
  onRemove: (id: string) => void;
  onRetrySources: () => void;
}

function FinderContent({
  section,
  result,
  loading,
  error,
  saved,
  sources,
  sourcesLoading,
  sourcesError,
  onSearch,
  onRetry,
  onSave,
  onRemove,
  onRetrySources,
}: FinderContentProps) {
  if (section === "risultati") {
    return (
      <Risultati
        result={result}
        loading={loading}
        error={error}
        onRetry={onRetry}
        onSave={onSave}
        saved={new Set(saved.map((item) => item.id))}
      />
    );
  }

  if (section === "salvati") return <Salvati offers={saved} onRemove={onRemove} />;

  if (section === "impostazioni") {
    return (
      <Impostazioni
        sources={sources}
        loading={sourcesLoading}
        error={sourcesError}
        onRetry={onRetrySources}
      />
    );
  }

  return <Cerca loading={loading} onSearch={onSearch} />;
}

interface FinderShellProps extends FinderContentProps {
  defaultCollapsed: boolean;
  sezioniVisibili: ReturnType<typeof useVista>["sezioniVisibili"];
  t: ReturnType<typeof useLanguage>["t"];
  announcement: string;
}

function FinderShell({
  defaultCollapsed,
  sezioniVisibili,
  t,
  announcement,
  ...contentProps
}: FinderShellProps) {
  return (
    <AppShell defaultCollapsed={defaultCollapsed}>
      <SidebarNavigation
        section={contentProps.section}
        sezioniVisibili={sezioniVisibili}
        t={t}
      />
      <div className="flex min-w-0 flex-1 flex-col">
        <AppShell.Topbar className="max-md:pl-14">
          <span className="text-sm font-medium text-text">ShipmentFinder</span>
          <LanguageSwitcher labels={{ it: "IT", en: "EN" }} />
        </AppShell.Topbar>
        <AppShell.Content className="max-md:pl-12">
          <FinderContent {...contentProps} />
        </AppShell.Content>
      </div>
      <div className="sr-only" aria-live="polite">
        {announcement}
      </div>
    </AppShell>
  );
}

function Finder() {
  const { t } = useLanguage();
  const { stato, sezioniVisibili, ricarica } = useVista();
  const { result, loading, error, run } = useQuotes();
  const [defaultCollapsed] = useState(
    () =>
      typeof window !== "undefined" &&
      window.matchMedia("(max-width: 767px)").matches,
  );
  const [section, setSection] = useState(() => location.hash.slice(1) || "cerca");
  const [saved, setSaved] = useState<SavedOffer[]>(readSaved);
  const [announcement, setAnnouncement] = useState("");
  const sourceState = useSources(section);

  useEffect(() => {
    const listener = () => setSection(location.hash.slice(1) || "cerca");
    addEventListener("hashchange", listener);
    return () => removeEventListener("hashchange", listener);
  }, []);

  useEffect(() => {
    try {
      localStorage.setItem(storageKey, JSON.stringify(saved));
    } catch {
      // Saved offers are intentionally local-only: no backend endpoint persists them.
    }
  }, [saved]);

  useEffect(() => {
    if (result && !loading && !error) {
      setAnnouncement(`${result.offers.length} risultati trovati`);
    }
  }, [error, loading, result]);

  const search = useCallback(
    (request: QuoteRequest) => {
      run(request);
      location.hash = "#risultati";
    },
    [run],
  );

  const save = useCallback((offer: Offer) => {
    setSaved((current) => {
      if (current.some((item) => item.id === offerKey(offer))) return current;
      setAnnouncement("Elemento salvato");
      return [
        ...current,
        { id: offerKey(offer), offer, savedAt: new Date().toISOString() },
      ];
    });
  }, []);

  if (stato === "loading") return <Skeleton className="m-6 h-48" />;

  if (stato === "error") {
    return (
      <EmptyState
        icon={<CircleAlert aria-hidden />}
        title={t("vista.error")}
        action={
          <Button onClick={() => void ricarica()}>{t("common.retry")}</Button>
        }
      />
    );
  }

  return (
    <FinderShell
      defaultCollapsed={defaultCollapsed}
      sezioniVisibili={sezioniVisibili}
      t={t}
      announcement={announcement}
      section={section}
      result={result}
      loading={loading}
      error={error}
      saved={saved}
      sources={sourceState.sources}
      sourcesLoading={sourceState.loading}
      sourcesError={sourceState.error}
      onSearch={search}
      onRetry={() => result && run(result.request)}
      onSave={save}
      onRemove={(id) =>
        setSaved((current) => current.filter((item) => item.id !== id))
      }
      onRetrySources={() => void sourceState.load()}
    />
  );
}

export default function App() {
  return (
    <VistaProvider fetcher={vistaFetcher}>
      <Finder />
    </VistaProvider>
  );
}
