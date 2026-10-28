import {
  Button,
  Card,
  CardBody,
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  EmptyState,
  PageHeader,
} from "@suite/design-system";
import { useLanguage } from "@suite/i18n";
import { Star } from "lucide-react";
import { useState } from "react";
import type { SavedOffer } from "../types";

const euro = new Intl.NumberFormat("it-IT", {
  style: "currency",
  currency: "EUR",
});

interface SalvatiProps {
  offers: SavedOffer[];
  onRemove: (id: string) => void;
}

function navigateToSearch() {
  location.hash = "#cerca";
}

export function Salvati({ offers, onRemove }: SalvatiProps) {
  const { t } = useLanguage();
  const [target, setTarget] = useState<SavedOffer | null>(null);

  return (
    <div className="grid gap-6">
      <PageHeader
        icon={<Star aria-hidden />}
        title={t("saved.title")}
        subtitle={t("saved.subtitle")}
      />
      {offers.length === 0 ? (
        <EmptyState
          icon={<Star aria-hidden />}
          title={t("saved.empty")}
          description={t("saved.emptyDescription")}
          action={
            <Button onClick={navigateToSearch}>{t("saved.newSearch")}</Button>
          }
        />
      ) : (
        <div className="grid gap-3">
          {offers.map(({ id, offer }) => (
            <Card key={id}>
              <CardBody className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="font-medium">
                    {offer.carrier}
                    {offer.service ? ` · ${offer.service}` : ""}
                  </p>
                  <p className="text-sm text-muted">{offer.source}</p>
                </div>
                <div className="flex items-center gap-3">
                  <span className="font-semibold">
                    {euro.format(offer.price_eur)}
                  </span>
                  <Button
                    variant="destructive"
                    onClick={() => setTarget({ id, offer, savedAt: "" })}
                  >
                    {t("saved.remove")}
                  </Button>
                </div>
              </CardBody>
            </Card>
          ))}
        </div>
      )}
      <Dialog
        open={target !== null}
        onOpenChange={(open) => !open && setTarget(null)}
      >
        <DialogContent state="danger">
          <DialogHeader>
            <DialogTitle>{t("saved.dialogTitle")}</DialogTitle>
            <DialogDescription>{t("saved.dialogDescription")}</DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <DialogClose asChild>
              <Button variant="secondary">{t("saved.cancel")}</Button>
            </DialogClose>
            <Button
              variant="destructive"
              onClick={() => {
                if (target) onRemove(target.id);
                setTarget(null);
              }}
            >
              {t("saved.confirm")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
