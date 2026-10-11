# Odoo 17 — REST API Documentation

**Base URL:** `https://<odoo-host>`  
**Format:** JSON  
**Authentication:** Odoo API key in the `x-api-key` request header for **all endpoints**.

```http
x-api-key: YOUR_API_KEY
Accept: application/json
```

API keys are issued to a dedicated Odoo integration user. Access to POS and product data is subject to that user's permissions. Use HTTPS and store the key securely.

## Endpoints

| Method | Endpoint | Purpose | Parameters |
|---|---|---|---|
| `GET` | `/api/orders` | Get POS orders within a date range | `start_date`, `end_date` (required, `YYYY-MM-DD`) |
| `GET` | `/api/products/rop` | List products with `rop_count > 0` | `page` (default `1`), `limit` (default `80`) |
| `POST` | `/api/products/rop/update` | Update a product's ROP count | JSON body: `product_id`, `rop_count` |
| `GET` | `/api/pos/sessions/{session_id}/orders` | Get POS orders in a session | `session_id` (path), `page` (default `1`), `limit` (default `80`) |
| `GET` | `/api/rop-product` | Get ROP products | - |

`product_id` refers to a `product.template` record. `rop_count` must be a non-negative integer.

## Request examples

**Orders by date**
```bash
curl 'https://<odoo-host>/api/orders?start_date=2026-10-01&end_date=2026-10-10' \
  -H 'x-api-key: YOUR_API_KEY'
```

**Products with ROP**
```bash
curl 'https://<odoo-host>/api/rop-product?page=1&limit=20' \
  -H 'x-api-key: YOUR_API_KEY'
```

**Update product ROP**
```bash
curl -X POST 'https://<odoo-host>/api/products/rop/update' \
  -H 'x-api-key: YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{"product_id":23,"rop_count":25}'
```

**Orders by POS session**
```bash
curl 'https://<odoo-host>/api/pos/sessions/4/orders?page=1&limit=20' \
  -H 'x-api-key: YOUR_API_KEY'
```

## Response format

**Successful list response** (example):
```json
{
  "success": true,
  "count": 1,
  "total_count": 1,
  "page": 1,
  "limit": 20,
  "products": [{"id": 23, "name": "Office Chair", "rop_count": 25}]
}
```



**Successful update response** (example):
```json
{
  "success": true,
  "message": "ROP count updated successfully for product Office Chair.",
  "product": {"id": 23, "name": "Office Chair", "rop_count": 25}
}
```

**Error response** (example):
```json
{"success": false, "message": "Unauthorized: Invalid or missing API key."}
```

**HTTP statuses:** `200` success · `400` invalid input · `401` missing/invalid key · `403` insufficient permissions · `404` record not found · `500` server error.

