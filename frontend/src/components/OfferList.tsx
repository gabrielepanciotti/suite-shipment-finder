import {
  Badge,
  Card,
  CardBody,
  CardHeader,
  CardTitle,
} from "@suite/design-system";
import { useLanguage } from "@suite/i18n";
import type { Comparison } from "../types";

const eur = new Intl.NumberFormat("it-IT", {
  style: "currency",
  currency: "EUR",
});

function days(min: number | null, max: number | null): string {
  if (min == null && max == null) return "—";
  if (min != null && max != null && min !== max) return `${min}–${max}`;
  return String(max ?? min);
}

export function OfferList({ result }: { result: Comparison }) {
  const { t } = useLanguage();
  const failed = result.outcomes.filter(
    (o) => o.status !== "ok" && o.status !== "empty",
  );

  return (
    <div className="grid gap-4">
      <Card>
        <CardHeader>
          <CardTitle>{t("results.title")}</CardTitle>
        </CardHeader>
        <CardBody>
          {result.offers.length === 0 ? (
            <p className="text-sm text-muted">{t("results.none")}</p>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-muted">
                  <th className="py-2">{t("results.carrier")}</th>
                  <th>{t("results.source")}</th>
                  <th>{t("results.days")}</th>
                  <th className="text-right">{t("results.price")}</th>
                </tr>
              </thead>
              <tbody>
                {result.offers.map((o, i) => (
                  <tr
                    key={`${o.source}-${o.carrier}-${o.service}-${i}`}
                    className="border-t border-border"
                  >
                    <td className="py-2">
                      {o.carrier}{" "}
                      {o.service && (
                        <span className="text-muted">· {o.service}</span>
                      )}
                      {i === 0 && (
                        <Badge className="ml-2">{t("results.best")}</Badge>
                      )}
                    </td>
                    <td>
                      {o.url ? (
                        <a
                          className="text-info underline underline-offset-4"
                          href={o.url}
                          target="_blank"
                          rel="noreferrer"
                        >
                          {o.source}
                        </a>
                      ) : (
                        o.source
                      )}
                    </td>
                    <td>{days(o.delivery_days_min, o.delivery_days_max)}</td>
                    <td className="text-right font-semibold">
                      {eur.format(o.price_eur)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </CardBody>
      </Card>
      {failed.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>{t("results.degraded")}</CardTitle>
          </CardHeader>
          <CardBody className="grid gap-2 text-sm">
            {failed.map((o) => (
              <div key={o.source} className="flex items-center gap-2">
                <Badge>{o.status}</Badge>
                <span className="font-medium">{o.source}</span>
                {o.detail && <span className="text-muted">{o.detail}</span>}
              </div>
            ))}
          </CardBody>
        </Card>
      )}
    </div>
  );
}
