#!/usr/bin/env python3
"""
TDS FVU Client — Standalone CLI
=================================
Uploads TDS files to the Odoo server, optionally verifies checksums,
and displays the full execution log from the server.

Usage:
  # Basic usage (server computes checksum)
  python tds_client.py \\
      --server http://localhost:8069 \\
      --auth admin:admin \\
      --tds-file /path/to/TDS_FILE.txt

  # With checksum & CSI file
  python tds_client.py \\
      --server http://localhost:8069 \\
      --auth admin:admin \\
      --tds-file /path/to/TDS_FILE.txt \\
      --csi-file /path/to/challan.csi \\
      --checksum "abc123..." \\
      --request-id "REQ-001" \\
      --notes "Quarterly TDS return"

  # Save output files to a directory
  python tds_client.py \\
      --server http://localhost:8069 \\
      --auth admin:admin \\
      --tds-file /path/to/TDS_FILE.txt \\
      --output-dir ./tds_outputs

  # JSON output (machine-readable)
  python tds_client.py \\
      --server http://localhost:8069 \\
      --auth admin:admin \\
      --tds-file /path/to/TDS_FILE.txt \\
      --json |
"""

import argparse
import base64
import hashlib
import json
import os
import sys
import time
from datetime import datetime

try:
    import requests
except ImportError:
    print("ERROR: 'requests' library is required. Install it with: pip install requests")
    sys.exit(1)


# ─────────────────────────────────────────────────────────────────────────────
#  Logging helpers  (client-side — prints to terminal with timestamps)
# ─────────────────────────────────────────────────────────────────────────────


def _now():
    return datetime.now().strftime('%H:%M:%S')


def step(num, total, label):
    """Print a section heading like  [2/6]  Reading files..."""
    print(f"\n{'─' * 60}")
    print(f"  [{num}/{total}]  {label}")
    print(f"{'─' * 60}")


def info(msg):
    print(f"  {_now()}  {msg}")


def ok(msg):
    print(f"  {_now()}  ✅ {msg}")


def warn(msg):
    print(f"  {_now()}  ⚠ {msg}")


def err(msg):
    print(f"  {_now()}  ❌ {msg}")


def detail(label, value):
    print(f"  {_now()}  {label}: {value}")


# ─────────────────────────────────────────────────────────────────────────────
#  File handling
# ─────────────────────────────────────────────────────────────────────────────


def read_file_b64(path):
    """Read a file and return (base64_string, size_bytes, filename)."""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")
    size = os.path.getsize(path)
    with open(path, 'rb') as f:
        raw = f.read()
    b64 = base64.b64encode(raw).decode()
    return b64, size, os.path.basename(path)


def compute_checksum(tds_b64, csi_b64=None):
    """Compute SHA-256 of base64-decoded file content(s)."""
    sha = hashlib.sha256()
    sha.update(base64.b64decode(tds_b64))
    if csi_b64:
        sha.update(base64.b64decode(csi_b64))
    return sha.hexdigest()


# ─────────────────────────────────────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────────────────────────────────────


def main():
    TOTAL_STEPS = 6

    parser = argparse.ArgumentParser(
        description='TDS FVU Client — Upload TDS files to the server for validation.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # Server connection
    parser.add_argument(
        '--server', '-s',
        required=True,
        help='Odoo server URL (e.g. http://localhost:8069)',
    )
    parser.add_argument(
        '--auth', '-a',
        required=True,
        help='Authentication as "user:password" or "db,user,password"',
    )
    parser.add_argument(
        '--db', '-d',
        default='odoo',
        help='Odoo database name (default: odoo)',
    )

    # Files
    parser.add_argument(
        '--tds-file', '-t',
        required=True,
        help='Path to the TDS/TCS input file (.txt or .fvu)',
    )
    parser.add_argument(
        '--csi-file', '-c',
        default=None,
        help='Path to the Challan/Consolidate file (.csi)',
    )
    parser.add_argument(
        '--checksum',
        default=None,
        help='Expected SHA-256 checksum (if not provided, client computes it)',
    )
    parser.add_argument(
        '--request-id', '-r',
        default=None,
        help='External request reference ID',
    )
    parser.add_argument(
        '--request-date',
        default=None,
        help='Request date (YYYY-MM-DD) — defaults to today',
    )
    parser.add_argument(
        '--notes', '-n',
        default=None,
        help='Additional notes for this request',
    )

    # Output
    parser.add_argument(
        '--output-dir', '-o',
        default=None,
        help='Directory to save output files into (optional)',
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Print machine-readable JSON response instead of formatted output',
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=300,
        help='HTTP request timeout in seconds (default: 300)',
    )

    args = parser.parse_args()

    # ── Parse auth ───────────────────────────────────────────────────────────
    if ',' in args.auth:
        # db,user:password format (e.g. "rd-TDS,admin:admin")
        parts = args.auth.split(',', 1)
        db, userpass = parts[0], parts[1]
        username, password = userpass.split(':', 1) if ':' in userpass else (userpass, '')
    else:
        # user:password format
        username, password = args.auth.split(':', 1) if ':' in args.auth else (args.auth, '')
        db = args.db

    server_url = args.server.rstrip('/')

    # ─────────────────────────────────────────────────────────────────────────
    #  STEP 1 — Read files
    # ─────────────────────────────────────────────────────────────────────────
    step(1, TOTAL_STEPS, 'Reading input files')

    info(f"TDS file: {args.tds_file}")
    tds_b64, tds_size, tds_filename = read_file_b64(args.tds_file)
    detail('  Size', f"{tds_size:,} bytes")
    detail('  Base64 length', f"{len(tds_b64):,} chars")

    csi_b64 = None
    csi_filename = None
    if args.csi_file:
        info(f"CSI file: {args.csi_file}")
        csi_b64, csi_size, csi_filename = read_file_b64(args.csi_file)
        detail('  Size', f"{csi_size:,} bytes")
        detail('  Base64 length', f"{len(csi_b64):,} chars")
    else:
        info("No CSI file provided (optional)")

    if args.output_dir:
        os.makedirs(args.output_dir, exist_ok=True)
        info(f"Output directory: {args.output_dir}")

    ok("Files read successfully")

    # ─────────────────────────────────────────────────────────────────────────
    #  STEP 2 — Compute checksum
    # ─────────────────────────────────────────────────────────────────────────
    step(2, TOTAL_STEPS, 'Checksum computation')

    provided_checksum = args.checksum
    computed_checksum = compute_checksum(tds_b64, csi_b64)

    detail('Computed SHA-256', computed_checksum)

    if provided_checksum:
        expected = provided_checksum.lower()
        computed = computed_checksum.lower()
        match = expected == computed

        detail('Provided checksum', provided_checksum)
        if match:
            ok("Checksums MATCH — data integrity verified ✓")
        else:
            warn("Checksums DO NOT MATCH — data may have been altered")
            warn("Proceeding anyway (server will validate)")
    else:
        info("No checksum provided — using computed checksum for integrity")
        provided_checksum = computed_checksum
        detail('Sending computed checksum', computed_checksum)

    ok("Checksum step complete")

    # ─────────────────────────────────────────────────────────────────────────
    #  STEP 3 — Build & send request
    # ─────────────────────────────────────────────────────────────────────────
    step(3, TOTAL_STEPS, 'Sending request to server')

    request_date = args.request_date or datetime.now().strftime('%Y-%m-%d')
    request_id = args.request_id or f"CLI-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    payload = {
        'tds_file_b64': tds_b64,
        'tds_filename': tds_filename,
        'checksum': provided_checksum,
        'request_id': request_id,
        'request_date': request_date,
        'notes': args.notes or f'Submitted via TDS Client CLI on {request_date}',
    }

    if csi_b64:
        payload['csi_file_b64'] = csi_b64
        payload['csi_filename'] = csi_filename

    api_url = f"{server_url}/api/tds/generate"
    detail('Server URL', api_url)
    detail('Request ID', request_id)
    detail('Payload keys', ', '.join(k for k in payload.keys() if 'b64' not in k))
    info("Sending POST request...")

    # Authenticate via session
    start_time = time.time()

    try:
        session = requests.Session()

        # Step 3a: Authenticate with Odoo
        auth_url = f"{server_url}/web/session/authenticate"
        info("Authenticating with Odoo server...")
        
        auth_payload = {
            'jsonrpc': '2.0',
            'params': {
                'db': db,
                'login': username,
                'password': password,
            }
        }
        
        auth_resp = session.post(
            auth_url,
            json=auth_payload,
            timeout=30,
        )
        
        if auth_resp.status_code != 200:
            err(f"Authentication failed (HTTP {auth_resp.status_code})")
            try:
                detail('Response', auth_resp.text[:500])
            except Exception:
                pass
            sys.exit(1)
        
        auth_data = auth_resp.json()
        if 'error' in auth_data:
            err(f"Authentication error: {auth_data['error']}")
            sys.exit(1)
        
        ok("Authentication successful")

        # Step 3b: Send the TDS generation request
        gen_url = f"{server_url}/api/tds/generate"
        info("Sending TDS validation request...")

        gen_payload = {
            'jsonrpc': '2.0',
            'params': payload,
        }

        gen_resp = session.post(
            gen_url,
            json=gen_payload,
            timeout=args.timeout,
        )

        elapsed = time.time() - start_time
        detail('Response time', f"{elapsed:.1f}s")
        detail('HTTP status', gen_resp.status_code)

        if gen_resp.status_code != 200:
            err(f"Server returned HTTP {gen_resp.status_code}")
            try:
                detail('Response body', gen_resp.text[:1000])
            except Exception:
                pass
            sys.exit(1)

        # Parse JSON-RPC response
        resp_data = gen_resp.json()

        # Extract result (handle both JSON-RPC envelope and plain JSON)
        if 'result' in resp_data:
            result = resp_data['result']
        else:
            result = resp_data

    except requests.exceptions.ConnectionError as e:
        err(f"Cannot connect to server: {e}")
        info("Check that the server URL is correct and the server is running.")
        sys.exit(1)
    except requests.exceptions.Timeout as e:
        err(f"Request timed out after {args.timeout}s: {e}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        err(f"Request failed: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        err(f"Invalid JSON response: {e}")
        try:
            detail('Raw response', gen_resp.text[:500])
        except Exception:
            pass
        sys.exit(1)

    ok("Server request completed")

    # ─────────────────────────────────────────────────────────────────────────
    #  STEP 4 — Show server response
    # ─────────────────────────────────────────────────────────────────────────
    step(4, TOTAL_STEPS, 'Server response')

    status = result.get('status', 'unknown')
    message = result.get('message', '')

    if status == 'ok':
        ok(f"Server: {message}")
    else:
        err(f"Server: {message}")

    data = result.get('data', {})
    if data:
        detail('Validation ID', data.get('validation_id', 'N/A'))
        detail('Reference', data.get('reference', 'N/A'))
        detail('State', data.get('state', 'N/A'))

        if data.get('error_message'):
            warn(f"Error message: {data['error_message']}")

        # Checksum
        cs_valid = data.get('checksum_valid')
        if cs_valid is True:
            ok("Server confirmed checksum: VALID ✓")
        elif cs_valid is False:
            cs_warn = data.get('warning', '')
            computed = data.get('computed_checksum', '')
            warn(f"Server reports checksum: INVALID ✗")
            if computed:
                detail('Server-computed checksum', computed)
            if cs_warn:
                warn(cs_warn)
        else:
            info("Checksum: Not validated (not provided)")

    # ─────────────────────────────────────────────────────────────────────────
    #  STEP 5 — Execution log from server
    # ─────────────────────────────────────────────────────────────────────────
    step(5, TOTAL_STEPS, 'Server execution log')

    if data and data.get('execution_log'):
        log_text = data['execution_log']
        for line in log_text.strip().split('\n'):
            line = line.strip()
            if line:
                # Color-code by content
                if 'ERROR' in line or 'FAILED' in line or '❌' in line:
                    print(f"  ⛔ {line}")
                elif 'WARNING' in line or '⚠' in line:
                    print(f"  ⚠ {line}")
                elif '✅' in line or 'COMPLETE' in line or 'done' in line.lower():
                    print(f"  ✅ {line}")
                elif 'START' in line or '=== ' in line:
                    print(f"  🔷 {line}")
                else:
                    print(f"  ·  {line}")
    else:
        info("No detailed execution log available from server.")

    # ─────────────────────────────────────────────────────────────────────────
    #  STEP 6 — Output files
    # ─────────────────────────────────────────────────────────────────────────
    step(6, TOTAL_STEPS, 'Output files')

    files = (data or {}).get('output_files', [])

    if not files:
        if data and data.get('state') == 'failed':
            warn("Validation failed — no output files generated.")
            if data.get('error_message'):
                err(f"Error: {data['error_message']}")
        else:
            warn("No output files returned (validation may still be processing).")
    else:
        ok(f"Received {len(files)} output file(s)")
        for f in files:
            fname = f.get('name', 'unknown')
            b64_len = len(f.get('b64', ''))
            detail(f"  📄 {fname}", f"{b64_len:,} bytes (base64)")

            # Save to output directory if requested
            if args.output_dir:
                fpath = os.path.join(args.output_dir, fname)
                try:
                    raw = base64.b64decode(f['b64'])
                    with open(fpath, 'wb') as fh:
                        fh.write(raw)
                    size = os.path.getsize(fpath)
                    ok(f"Saved: {fpath} ({size:,} bytes)")
                except Exception as e:
                    warn(f"Could not save {fname}: {e}")

    # ── Summary ──────────────────────────────────────────────────────────────
    total_elapsed = time.time() - start_time
    print(f"\n{'=' * 60}")
    final_state = (data or {}).get('state', 'unknown')
    if final_state == 'done':
        ok(f"✅ Validation COMPLETE in {total_elapsed:.1f}s")
    elif final_state == 'failed':
        err(f"❌ Validation FAILED in {total_elapsed:.1f}s")
    else:
        info(f"⏳ Validation state: {final_state} ({total_elapsed:.1f}s)")
    print(f"{'=' * 60}\n")

    # If --json, print raw response
    if args.json:
        print("--- JSON OUTPUT ---")
        print(json.dumps(result, indent=2))

    # Exit with code
    sys.exit(0 if final_state == 'done' else 1)


if __name__ == '__main__':
    main()
