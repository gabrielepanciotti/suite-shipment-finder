import { Button, EmptyState, PageHeader } from "@suite/design-system";
import { useLanguage } from "@suite/i18n";
import { Search } from "lucide-react";
import { QuoteForm } from "../components/QuoteForm";
import type { QuoteRequest } from "../types";

interface CercaProps {
  loading: boolean;
  onSearch: (request: QuoteRequest) => void;
}

export function Cerca({ loading, onSearch }: CercaProps) {
  const { t } = useLanguage();
  return (
    <div className="grid gap-6">
      <PageHeader
        icon={<Search aria-hidden />}
        title={t("cerca.title")}
        subtitle={t("cerca.subtitle")}
      />
      <QuoteForm loading={loading} onSubmit={onSearch} />
      <EmptyState
        icon={<Search aria-hidden />}
        title={t("cerca.emptyTitle")}
        description={t("cerca.emptyDescription")}
        action={
          <Button onClick={() => (location.hash = "#cerca")}>
            {t("cerca.startSearch")}
          </Button>
        }
      />
    </div>
  );
}
