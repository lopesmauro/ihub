# IntegrationHub MVP - Validacao operacional

Base local assumida:

```bash
export IHUB_URL=http://localhost:8000
```

Use um servico destino local que responda 2xx em `POST /api/deliveries/` para validar o caminho de sucesso. Se o destino nao existir ou retornar erro, a `Delivery` deve ficar `FAILED`, mas ainda deve gravar `rendered_request`.

## 1. Criar EventType

```bash
curl -sS -X POST "$IHUB_URL/api/event-types/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "order.created",
    "description": "Pedido criado",
    "is_active": true
  }'
```

Guarde o `id` retornado como `EVENT_TYPE_ID`.

## 2. Criar Rule HTTP

Substitua `EVENT_TYPE_ID` pelo id real antes de enviar.

```bash
curl -sS -X POST "$IHUB_URL/api/rules/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Enviar pedido criado para entrega",
    "event_type": EVENT_TYPE_ID,
    "action_type": "http.request",
    "config": {
      "method": "POST",
      "url": "http://localhost:9001/api/deliveries/"
    },
    "is_active": true
  }'
```

Guarde o `id` retornado como `RULE_ID`.

## 3. Criar outra Rule para o mesmo EventType

Para gerar mais de uma chamada quando `order.created` for recebido, crie outra `Rule` ativa ligada ao mesmo `EVENT_TYPE_ID`.

```bash
curl -sS -X POST "$IHUB_URL/api/rules/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Notificar cliente sobre pedido criado",
    "event_type": EVENT_TYPE_ID,
    "action_type": "http.request",
    "config": {
      "method": "POST",
      "url": "http://localhost:9001/api/notifications/"
    },
    "is_active": true
  }'
```

Cada `Rule` ativa aplicavel ao `EventType` gera sua propria `Delivery`.

## 4. Ingerir evento

```bash
curl -sS -X POST "$IHUB_URL/api/events/ingest/" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "order.created",
    "source": "purchases-service",
    "payload": {
      "order_id": "ORD-123",
      "customer_name": "Mauro"
    }
  }'
```

Resposta esperada em sucesso:

```json
{
  "event_id": 1,
  "status": "PROCESSED"
}
```

Se o destino HTTP nao responder 2xx, o status esperado e `FAILED`.

## 5. Consultar Event e Deliveries

```bash
curl -sS "$IHUB_URL/api/events/"
curl -sS "$IHUB_URL/api/deliveries/"
```

Cada `Delivery` deve apontar para a `Rule` executada e conter `rendered_request` semelhante a:

```json
{
  "method": "POST",
  "url": "http://localhost:9001/api/deliveries/",
  "body": {
    "order_id": "ORD-123",
    "customer_name": "Mauro"
  }
}
```

## Escopo fora do MVP

Este MVP nao deve conter Celery, filas, retries, workers, `DeliveryAttempt`, JWT, `RuleCondition`, dashboard, multi-tenant, criptografia de secrets, template de corpo ou tipos de acao diferentes de `http.request`.
