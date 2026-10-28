import {
  Button,
  Callout,
  EmptyState,
  PageHeader,
  Skeleton,
} from "@suite/design-system";
import { useLanguage } from "@suite/i18n";
import { CircleAlert, Settings } from "lucide-react";

interface ImpostazioniProps {
  sources: string[] | null;
  loading: boolean;
  error: string | null;
  onRetry: () => void;
}

export function Impostazioni({
  sources,
  loading,
  error,
  onRetry,
}: ImpostazioniProps) {
  const { t } = useLanguage();
  return (
    <div className="grid gap-6">
      <PageHeader
        icon={<Settings aria-hidden />}
        title={t("settings.title")}
        subtitle={t("settings.subtitle")}
      />
      {loading ? (
        <Skeleton className="h-32" />
      ) : error ? (
        <Callout variant="danger" title={t("settings.error")}>
          <div className="grid gap-3">
            <span>{t("settings.errorDescription")}</span>
            <div>
              <Button variant="secondary" size="sm" onClick={onRetry}>
                {t("common.retry")}
              </Button>
            </div>
          </div>
        </Callout>
      ) : !sources?.length ? (
        <EmptyState
          icon={<CircleAlert aria-hidden />}
          title={t("settings.empty")}
        />
      ) : (
        <ul className="grid gap-2">
          {sources.map((source) => (
            <li
              key={source}
              className="rounded-card border border-border bg-surface px-4 py-3"
            >
              {source}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
