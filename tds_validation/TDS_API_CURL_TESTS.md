# TDS API — Curl / Postman Test Collection

## 1. Authenticate (Server — port 8070)

This is the standard Odoo JSON-RPC auth. Required before calling the TDS API.

```bash
curl -X POST http://localhost:8070/web/session/authenticate \
  -H "Content-Type: application/json" \
  -c /tmp/odoo_cookies.txt \
  -d '{
    "jsonrpc": "2.0",
    "params": {
      "db": "rd-TDS",
      "login": "admin",
      "password": "admin"
    }
  }'
```

**Postman:**

- Method: `POST`
- URL: `http://localhost:8070/web/session/authenticate`
- Headers: `Content-Type: application/json`
- Body (raw JSON):

```json
{
  "jsonrpc": "2.0",
  "params": {
    "db": "rd-TDS",
    "login": "admin",
    "password": "admin"
  }
}
```

- ✅ Expected response: `{ "jsonrpc": "2.0", "result": { "uid": 1, ... } }`
- ⚠️ This must be called first — it sets a session cookie needed by the TDS endpoint

---

## 2. Generate TDS (Server — port 8070)

### 2a. Minimal request (TDS file only)

```bash
curl -X POST http://localhost:8070/api/tds/generate \
  -H "Content-Type: application/json" \
  -b /tmp/odoo_cookies.txt \
  -d '{
    "tds_file_b64": "'$(base64 -w0 community/tds.txt)'",
    "tds_filename": "tds.txt"
  }'
```

### 2b. With challan file and request ID

```bash
curl -X POST http://localhost:8070/api/tds/generate \
  -H "Content-Type: application/json" \
  -b /tmp/odoo_cookies.txt \
  -d '{
    "tds_file_b64": "'$(base64 -w0 community/tds.txt)'",
    "tds_filename": "tds.txt",
    "csi_file_b64": "'$(base64 -w0 community/challan.csi)'",
    "csi_filename": "challan.csi",
    "checksum": "1a70432e...",
    "request_id": "REQ-001",
    "request_date": "2026-07-15",
    "notes": "Test from Postman"
  }'
```

### 2c. Full request with checksum + webhook

```bash
# Step 1: Compute SHA-256 of files
CHECKSUM=$(base64 -w0 community/tds.txt | sha256sum | head -c64)

# Step 2: Send with checksum and webhook
curl -X POST http://localhost:8070/api/tds/generate \
  -H "Content-Type: application/json" \
  -b /tmp/odoo_cookies.txt \
  -d '{
    "tds_file_b64": "'$(base64 -w0 community/tds.txt)'",
    "tds_filename": "tds.txt",
    "csi_file_b64": "'$(base64 -w0 community/challan.csi)'",
    "csi_filename": "challan.csi",
    "checksum": "'$CHECKSUM'",
    "request_id": "REQ-WEBHOOK-001",
    "request_date": "2026-07-15",
    "notes": "Testing webhook callback",
    "webhook_url": "http://localhost:8909/api/tds/webhook/receive"
  }'
```

**Postman setup:**

- Method: `POST`
- URL: `http://localhost:8070/api/tds/generate`
- Headers:
  - `Content-Type: application/json`
- Auth: No auth needed (uses session cookie from step 1)
- Body (raw JSON):

```json
{
  "tds_file_b64": "<base64_of_your_file>",
  "tds_filename": "tds.txt"
}
```

**Expected response (success):**

```json
{
  "status": "ok",
  "message": "TDS validation processed.",
  "data": {
    "validation_id": 42,
    "reference": "TDS/2026/0042",
    "state": "done",
    "output_files": [
      {
        "name": "tds.err",
        "b64": "<base64>..."
      },
      {
        "name": "tdserr.html",
        "b64": "<base64>..."
      }
    ],
    "error_message": "",
    "execution_log": "[05:56:11] === TDS Validation START...",
    "checksum_valid": true
  }
}
```

**Expected response (validation failed):**

```json
{
  "status": "ok",
  "message": "TDS validation processed.",
  "data": {
    "validation_id": 43,
    "reference": "TDS/2026/0043",
    "state": "failed",
    "output_files": [],
    "error_message": "FVU did not produce output within 180s...",
    "execution_log": "[05:56:11] === TDS Validation START...\n[05:56:11] ❌ ERROR: FVU did not...",
    "checksum_valid": null
  }
}
```

**Expected response (validation error):**

```json
{
  "status": "ok",
  "message": "TDS validation processed.",
  "data": {
    "validation_id": 44,
    "reference": "TDS/2026/0044",
    "state": "done",
    "output_files": [
      {
        "name": "tds.err",
        "b64": "<base64>..."
      }
    ],
    "error_message": "",
    "execution_log": "[05:56:11] === TDS Validation START...",
    "checksum_valid": null
  }
}
```

**Expected response (input error — bad filename):**

```json
{
  "status": "error",
  "message": "tds_filename must end with .txt or .fvu"
}
```

---

## 3. Test Webhook Directly (Client — port 8909)

Use this to test the webhook receiver independently without running the full validation:

```bash
curl -X POST http://localhost:8909/api/tds/webhook/receive \
  -H "Content-Type: application/json" \
  -d '{
    "event": "validation.complete",
    "validation_id": 9999,
    "reference": "TDS/2026/0099",
    "state": "done",
    "request_id": "REQ-WEBHOOK-001",
    "checksum": "1a70432e...",
    "checksum_valid": true,
    "execution_log": "[00:00:01] === TDS Validation START ===\n[00:00:02] ✅ Input validation passed\n[00:00:05] ✅ FVU version up-to-date (9.4)\n[00:00:06] ✅ State set to Running\n[00:00:10] ✅ Output files detected\n[00:00:11] ✅ Validation complete",
    "error_message": "",
    "output_files": [
      {
        "name": "test_output.fvu",
        "b64": "VGVzdCBmaWxlIENvbnRlbnQ="
      }
    ]
  }'
```

**Postman setup:**

- Method: `POST`
- URL: `http://localhost:8909/api/tds/webhook/receive`
- Headers: `Content-Type: application/json`
- Body: raw JSON as shown above

**Expected response:**

```json
{
  "status": "ok",
  "message": "Processed for TDSCLI/2026/0001"
}
```

Or if no matching record found:

```json
{
  "status": "error",
  "message": "Record not found"
}
```

---

## 4. Quick one-liner (bash, copies from `community/tds.txt`)

```bash
# Authenticate and save cookie
curl -s -X POST http://localhost:8070/web/session/authenticate \
  -H "Content-Type: application/json" \
  -c /tmp/odoo_cookies.txt \
  -d '{"jsonrpc":"2.0","params":{"db":"rd-TDS","login":"admin","password":"admin"}}' | jq .

# Send TDS file using the cookie
curl -X POST http://localhost:8070/api/tds/generate \
  -H "Content-Type: application/json" \
  -b /tmp/odoo_cookies.txt \
  -d '{
    "tds_file_b64": "'$(base64 -w0 community/tds.txt)'",
    "tds_filename": "tds.txt",
    "request_id": "CURL-DEMO-'$(date +%s)'"
  }' | jq .
```

---

## 5. Test webhook from server (simulate after validation)

If you want the server to actually fire the webhook, include `webhook_url` in the generate call (see 2c above). The server calls it automatically after validation completes (success or failure).

```bash
# First create a tds.client record in the Client UI with request_id = "WH-001"
# Then trigger from server:
curl -X POST http://localhost:8070/api/tds/generate \
  -H "Content-Type: application/json" \
  -b /tmp/odoo_cookies.txt \
  -d '{
    "tds_file_b64": "'$(base64 -w0 community/tds.txt)'",
    "tds_filename": "tds.txt",
    "request_id": "WH-001",
    "webhook_url": "http://localhost:8909/api/tds/webhook/receive"
  }'
```

---

## Postman Collection (Import)

Create a **Postman Collection** with these 3 requests:

### Request 1: Authenticate

- `POST http://localhost:8070/web/session/authenticate`
- Body: `{"jsonrpc":"2.0","params":{"db":"rd-TDS","login":"admin","password":"admin"}}`

### Request 2: Generate TDS

- `POST http://localhost:8070/api/tds/generate`
- Headers: `Content-Type: application/json`
- Body: Enable raw JSON, paste:

```json
{
  "tds_file_b64": "{{tds_file_b64}}",
  "tds_filename": "tds.txt",
  "request_id": "POSTMAN-{{$timestamp}}"
}
```

- Pre-request Script (to compute base64 from a local file — or just paste the base64 manually):

```javascript
// If you have a local file, you'd need to paste the base64 directly
// Use https://www.base64encode.org/ to encode your tds.txt, then paste it here
pm.collectionVariables.set("tds_file_b64", "<paste_base64_here>");
```

### Request 3: Webhook Receiver (direct test)

- `POST http://localhost:8909/api/tds/webhook/receive`
- Body:

```json
{
  "event": "validation.complete",
  "validation_id": 123,
  "reference": "TDS/2026/0123",
  "state": "done",
  "request_id": "POSTMAN-WH-001",
  "output_files": [{ "name": "test.fvu", "b64": "VGVzdCBGaWxlIENvbnRlbnQ=" }]
}
```
