import { useState } from "react";
import {
  Button,
  Card,
  CardBody,
  CardHeader,
  CardTitle,
  Field,
  Input,
} from "@suite/design-system";
import { useLanguage } from "@suite/i18n";
import type { QuoteRequest } from "../types";

interface Props {
  loading: boolean;
  onSubmit: (request: QuoteRequest) => void;
}

const blank = { postal_code: "", city: "" };

export function QuoteForm({ loading, onSubmit }: Props) {
  const { t } = useLanguage();
  const [from, setFrom] = useState(blank);
  const [to, setTo] = useState(blank);
  const [dims, setDims] = useState({ l: "", w: "", h: "", kg: "" });

  const num = (v: string) => Number(v.replace(",", "."));
  const valid =
    from.postal_code &&
    from.city &&
    to.postal_code &&
    to.city &&
    [dims.l, dims.w, dims.h, dims.kg].every((v) => num(v) > 0);

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!valid) return;
    onSubmit({
      sender: { ...from, country: "IT" },
      recipient: { ...to, country: "IT" },
      parcel: {
        length_cm: num(dims.l),
        width_cm: num(dims.w),
        height_cm: num(dims.h),
        weight_kg: num(dims.kg),
        count: 1,
      },
    });
  };

  return (
    <form onSubmit={submit} className="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>{t("form.sender")}</CardTitle>
        </CardHeader>
        <CardBody className="grid gap-3">
          <Field label={t("form.postalCode")} htmlFor="sender-cap" required>
            <Input
              id="sender-cap"
              value={from.postal_code}
              inputMode="numeric"
              onChange={(e) =>
                setFrom({ ...from, postal_code: e.target.value })
              }
            />
          </Field>
          <Field label={t("form.city")} htmlFor="sender-city" required>
            <Input
              id="sender-city"
              value={from.city}
              onChange={(e) => setFrom({ ...from, city: e.target.value })}
            />
          </Field>
        </CardBody>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>{t("form.recipient")}</CardTitle>
        </CardHeader>
        <CardBody className="grid gap-3">
          <Field label={t("form.postalCode")} htmlFor="recipient-cap" required>
            <Input
              id="recipient-cap"
              value={to.postal_code}
              inputMode="numeric"
              onChange={(e) => setTo({ ...to, postal_code: e.target.value })}
            />
          </Field>
          <Field label={t("form.city")} htmlFor="recipient-city" required>
            <Input
              id="recipient-city"
              value={to.city}
              onChange={(e) => setTo({ ...to, city: e.target.value })}
            />
          </Field>
        </CardBody>
      </Card>
      <Card className="sm:col-span-2">
        <CardHeader>
          <CardTitle>{t("form.parcel")}</CardTitle>
        </CardHeader>
        <CardBody className="grid grid-cols-2 gap-3">
          <Field label={t("form.length")} htmlFor="len" required>
            <Input
              id="len"
              value={dims.l}
              inputMode="decimal"
              onChange={(e) => setDims({ ...dims, l: e.target.value })}
            />
          </Field>
          <Field label={t("form.width")} htmlFor="wid" required>
            <Input
              id="wid"
              value={dims.w}
              inputMode="decimal"
              onChange={(e) => setDims({ ...dims, w: e.target.value })}
            />
          </Field>
          <Field label={t("form.height")} htmlFor="hei" required>
            <Input
              id="hei"
              value={dims.h}
              inputMode="decimal"
              onChange={(e) => setDims({ ...dims, h: e.target.value })}
            />
          </Field>
          <Field label={t("form.weight")} htmlFor="kg" required>
            <Input
              id="kg"
              value={dims.kg}
              inputMode="decimal"
              onChange={(e) => setDims({ ...dims, kg: e.target.value })}
            />
          </Field>
        </CardBody>
      </Card>
      <div className="sm:col-span-2">
        <Button type="submit" loading={loading} disabled={!valid || loading}>
          {t("form.compare")}
        </Button>
      </div>
    </form>
  );
}
