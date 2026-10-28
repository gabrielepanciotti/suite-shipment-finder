# Guida d'uso — ShipmentFinder

## Cosa fa

ShipmentFinder confronta i preventivi di spedizione di tre siti — Paccofacile, IoSpedisco
e SpedireComodo — per un pacco, e mostra le offerte in un unico elenco dalla più economica.
Non acquista e non prepara la spedizione: si ferma al confronto. Per comprare si apre il
link dell'offerta, che rimanda al sito del corriere.

## Come si apre

Per lo sviluppo locale copia `.env.example` in `.env`, poi avvia i due servizi come indicato
nel README. In alternativa, con Docker e il framework Life disponibile accanto al repository:

```bash
docker compose -f deploy/docker-compose.example.yml up --build
```

L'interfaccia è su `http://127.0.0.1:5173` e l'API su `http://127.0.0.1:8000` per impostazione
predefinita. Spegni l'ambiente con `docker compose -f deploy/docker-compose.example.yml stop`.

## Casi d'uso passo per passo

### Confrontare un pacco singolo

1. Compila **Mittente** e **Destinatario** con CAP e Città.
2. In **Pacco** inserisci Lunghezza, Larghezza e Altezza in centimetri, e il Peso in kg.
3. Premi **Confronta i prezzi**.
4. Leggi la tabella **Offerte, dalla più economica**: Corriere (con il servizio), Fonte,
   Giorni di consegna e Prezzo IVA inclusa. La prima riga porta il segno **Migliore**.
5. Per comprare, clicca il nome nella colonna **Fonte**: apre la pagina del sito.

Se nessuna fonte ha servizi sulla tratta compare «Nessuna fonte ha restituito offerte per
questa tratta.».

### Più colli

Dall'interfaccia si confronta **un collo alla volta**: il modulo non ha il campo numero colli.
L'API lo accetta (`parcel.count`, da 1 a 20) per chi la chiama direttamente.

### Capire una fonte che non ha risposto

Sotto l'elenco delle offerte, il riquadro **Fonti che non hanno risposto** elenca le fonti
guaste con lo stato e un dettaglio. Una fonte che ha risposto senza servizi sulla tratta
(`empty`) non compare lì: semplicemente non ha righe in tabella.

## Servizi LLM

L'app non usa modelli linguistici.

## Problemi comuni

- **Stati di una fonte**:
  - `ok` — la fonte ha risposto con almeno un'offerta;
  - `empty` — nessun servizio su quella tratta;
  - `blocked` — il sito ha bloccato il bot (captcha o anti-bot);
  - `changed` — il sito ha cambiato formato e il bot va aggiornato;
  - `timeout` — il sito non ha risposto in tempo;
  - `error` — errore generico.
- **Prezzi**: sono sempre IVA inclusa. IoSpedisco e SpedireComodo quotano IVA esclusa: il bot
  aggiunge il 22%.
- **Offerte riservate a partita IVA**: sono escluse, un privato non può comprarle.
- **Località**: la località si sceglie per nome della città, quindi se un CAP copre più comuni
  scrivi la città per esteso.
- **Porta già occupata**: un'altra copia dei container è già accesa; fermala prima di riavviare.
