import {
  Button,
  Callout,
  Card,
  CardBody,
  DataTable,
  EmptyState,
  PageHeader,
  Skeleton,
} from "@suite/design-system";
import { useLanguage } from "@suite/i18n";
import { CircleAlert, ListFilter, Search } from "lucide-react";
import { useMemo } from "react";
import type { Column } from "@suite/design-system";
import type { Comparison, Offer } from "../types";

const euro = new Intl.NumberFormat("it-IT", {
  style: "currency",
  currency: "EUR",
});

const days = (min: number | null, max: number | null) => {
  if (min === null && max === null) return "—";
  return min !== null && max !== null && min !== max
    ? `${min}–${max}`
    : String(max ?? min);
};

const offerKey = (offer: Offer) =>
  `${offer.source}:${offer.carrier}:${offer.service}:${offer.price_eur}`;

interface RisultatiProps {
  result: Comparison | null;
  loading: boolean;
  error: string | null;
  onRetry: () => void;
  onSave: (offer: Offer) => void;
  saved: Set<string>;
}

function navigateToSearch() {
  location.hash = "#cerca";
}

export function Risultati({
  result,
  loading,
  error,
  onRetry,
  onSave,
  saved,
}: RisultatiProps) {
  const { t } = useLanguage();
  const columns = useMemo<Column<Offer>[]>(
    () => [
      {
        key: "carrier",
        header: t("results.carrier"),
        sortable: true,
        accessor: (offer) => offer.carrier,
        render: (offer) => (
          <span className="font-medium">
            {offer.carrier}
            {offer.service ? (
              <span className="text-muted"> · {offer.service}</span>
            ) : null}
          </span>
        ),
      },
      {
        key: "source",
        header: t("results.source"),
        sortable: true,
        accessor: (offer) => offer.source,
      },
      {
        key: "days",
        header: t("results.days"),
        accessor: (offer) => days(offer.delivery_days_min, offer.delivery_days_max),
      },
      {
        key: "price",
        header: t("results.price"),
        sortable: true,
        accessor: (offer) => offer.price_eur,
        render: (offer) => (
          <span className="font-semibold">{euro.format(offer.price_eur)}</span>
        ),
      },
      {
        key: "save",
        header: t("results.save"),
        actions: true,
        accessor: () => "",
        render: (offer) => (
          <Button
            variant="secondary"
            size="sm"
            disabled={saved.has(offerKey(offer))}
            onClick={() => onSave(offer)}
          >
            {saved.has(offerKey(offer))
              ? t("results.saved")
              : t("results.save")}
          </Button>
        ),
      },
    ],
    [onSave, saved, t],
  );

  return (
    <div className="grid gap-6">
      <PageHeader
        icon={<ListFilter aria-hidden />}
        title={t("results.title")}
        subtitle={t("results.subtitle")}
        actions={
          <Button variant="secondary" onClick={navigateToSearch}>
            {t("results.newSearch")}
          </Button>
        }
      />
      {loading ? (
        <Skeleton className="h-48" />
      ) : error ? (
        <EmptyState
          icon={<CircleAlert aria-hidden />}
          title={t("results.error")}
          description={t("results.errorDescription")}
          action={<Button onClick={onRetry}>{t("common.retry")}</Button>}
        />
      ) : !result ? (
        <EmptyState
          icon={<Search aria-hidden />}
          title={t("results.noSearch")}
          action={<Button onClick={navigateToSearch}>{t("results.startSearch")}</Button>}
        />
      ) : result.offers.length === 0 ? (
        <EmptyState
          icon={<ListFilter aria-hidden />}
          title={t("results.none")}
          description={t("results.noneDescription")}
          action={
            <Button onClick={navigateToSearch}>
              {t("results.modifyCriteria")}
            </Button>
          }
        />
      ) : (
        <ResultsContent
          result={result}
          columns={columns}
          onSave={onSave}
          saved={saved}
          t={t}
        />
      )}
    </div>
  );
}

interface ResultsContentProps {
  result: Comparison;
  columns: Column<Offer>[];
  onSave: (offer: Offer) => void;
  saved: Set<string>;
  t: (key: string) => string;
}

function ResultsContent({
  result,
  columns,
  onSave,
  saved,
  t,
}: ResultsContentProps) {
  const failedOutcomes = result.outcomes.filter(
    (outcome) => outcome.status !== "ok" && outcome.status !== "empty",
  );

  return (
    <>
      <div className="hidden md:block">
        <DataTable columns={columns} data={result.offers} rowKey={offerKey} />
      </div>
      <div className="grid gap-3 md:hidden">
        {result.offers.map((offer) => (
          <Card key={offerKey(offer)}>
            <CardBody className="grid gap-3">
              <div className="flex items-start justify-between gap-3">
                <span className="font-medium">
                  {offer.carrier}
                  {offer.service ? ` · ${offer.service}` : ""}
                </span>
                <span className="font-semibold">{euro.format(offer.price_eur)}</span>
              </div>
              <span className="text-sm text-muted">
                {offer.source} · {t("results.days")}: {days(
                  offer.delivery_days_min,
                  offer.delivery_days_max,
                )}
              </span>
              <Button
                variant="secondary"
                disabled={saved.has(offerKey(offer))}
                onClick={() => onSave(offer)}
              >
                {saved.has(offerKey(offer))
                  ? t("results.saved")
                  : t("results.save")}
              </Button>
            </CardBody>
          </Card>
        ))}
      </div>
      {failedOutcomes.length > 0 && (
        <Callout variant="warning" title={t("results.degraded")}>
          {failedOutcomes.map((outcome) => (
            <div key={outcome.source}>
              {outcome.source}: {outcome.detail || outcome.status}
            </div>
          ))}
        </Callout>
      )}
    </>
  );
}

export { offerKey };
