#!/usr/bin/env python3
"""
CSQAQ Market API CLI Tool

Unified CLI for discovering, syncing, and calling CSQAQ market APIs.
Data source: https://docs.csqaq.com/sitemap.xml

Usage:
    python csqaq_api.py sync                    # Sync API docs from sitemap
    python csqaq_api.py list --limit 200        # List available endpoints
    python csqaq_api.py call --operation-id <id> --query key=value
    python csqaq_api.py call --path <path> --method GET --query key=value
"""

import argparse
import json
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

import yaml

# Constants
CSQAQ_DOCS_BASE = "https://docs.csqaq.com"
CSQAQ_API_BASE = "https://csqaq.com"
SITEMAP_URL = f"{CSQAQ_DOCS_BASE}/sitemap.xml"
REFERENCES_DIR = Path(__file__).parent.parent / "references"
ENDPOINTS_JSON = REFERENCES_DIR / "endpoints.json"
ENDPOINTS_MD = REFERENCES_DIR / "endpoints.md"
MERGED_OPENAPI = REFERENCES_DIR / "merged_openapi.json"
SYNC_META = REFERENCES_DIR / "sync_meta.json"


def get_api_token() -> str:
    """Get API token from environment variable."""
    token = os.environ.get("CSQAQ_API_TOKEN")
    if not token:
        print("Error: CSQAQ_API_TOKEN environment variable not set.")
        print("Please set it with: export CSQAQ_API_TOKEN='<your_token>'")
        sys.exit(1)
    return token


def fetch_url(url: str) -> str:
    """Fetch content from URL."""
    import urllib.request
    import urllib.error

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "CSQAQ-Market-Lookup/1.0"})
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.read().decode("utf-8")
    except urllib.error.URLError as e:
        print(f"Error fetching {url}: {e}")
        sys.exit(1)


def parse_sitemap(sitemap_content: str) -> List[str]:
    """Parse sitemap XML and extract API doc URLs."""
    urls = []
    try:
        root = ET.fromstring(sitemap_content)
        # Handle sitemap namespace
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        for url_elem in root.findall(".//sm:url/sm:loc", ns):
            url = url_elem.text.strip()
            if "/api-" in url and url.endswith(".md"):
                urls.append(url)
    except ET.ParseError as e:
        print(f"Error parsing sitemap: {e}")
        sys.exit(1)
    return urls


def extract_endpoint_info(url: str, content: str) -> Optional[Dict[str, Any]]:
    """Extract endpoint information from API doc content."""
    info = {
        "url": url,
        "path": None,
        "method": None,
        "operationId": None,
        "summary": None,
        "tags": [],
        "doc_id": None,
    }

    # Extract doc ID from URL
    # Example: https://docs.csqaq.com/api-v1-current-data-get.md
    path = urlparse(url).path
    filename = path.split("/")[-1].replace(".md", "")
    info["doc_id"] = filename

    # Try to parse YAML front matter
    if content.startswith("---"):
        try:
            end_idx = content.index("---", 3)
            frontmatter = content[3:end_idx].strip()
            metadata = yaml.safe_load(frontmatter)
            if isinstance(metadata, dict):
                info["path"] = metadata.get("path")
                info["method"] = metadata.get("method", "GET").upper()
                info["operationId"] = metadata.get("operationId")
                info["summary"] = metadata.get("summary", "")
                info["tags"] = metadata.get("tags", [])
        except (ValueError, yaml.YAMLError):
            pass

    # Fallback: extract from content if not in frontmatter
    if not info["path"]:
        # Try to find path in content
        import re
        path_match = re.search(r"(?:path|endpoint|url):\s*[`\"']?(/[^\s`\"']+)", content, re.IGNORECASE)
        if path_match:
            info["path"] = path_match.group(1)

    if not info["method"]:
        import re
        method_match = re.search(r"(?:method|http_method):\s*(GET|POST|PUT|DELETE|PATCH)", content, re.IGNORECASE)
        if method_match:
            info["method"] = method_match.group(1).upper()

    if not info["operationId"]:
        import re
        op_match = re.search(r"operationId:\s*[`\"']?([^\s`\"']+)", content, re.IGNORECASE)
        if op_match:
            info["operationId"] = op_match.group(1)

    # Only return if we have at least path and method
    if info["path"] and info["method"]:
        return info
    return None


def cmd_sync(args):
    """Sync API docs from sitemap."""
    print(f"Fetching sitemap from {SITEMAP_URL}...")
    sitemap_content = fetch_url(SITEMAP_URL)
    urls = parse_sitemap(sitemap_content)
    print(f"Found {len(urls)} API doc URLs")

    endpoints = []
    merged_paths = {}

    for i, url in enumerate(urls, 1):
        print(f"  [{i}/{len(urls)}] Fetching {url}...")
        content = fetch_url(url)
        info = extract_endpoint_info(url, content)
        if info:
            endpoints.append(info)
            # Build merged OpenAPI paths
            path_key = f"{info['method']} {info['path']}"
            if path_key not in merged_paths:
                merged_paths[path_key] = {
                    "path": info["path"],
                    "method": info["method"],
                    "operationId": info["operationId"],
                    "summary": info["summary"],
                    "tags": info["tags"],
                    "doc_url": url,
                }

    # Save endpoints JSON
    REFERENCES_DIR.mkdir(parents=True, exist_ok=True)
    with open(ENDPOINTS_JSON, "w", encoding="utf-8") as f:
        json.dump(endpoints, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(endpoints)} endpoints to {ENDPOINTS_JSON}")

    # Save endpoints MD
    with open(ENDPOINTS_MD, "w", encoding="utf-8") as f:
        f.write("# CSQAQ API Endpoints\n\n")
        f.write(f"Total: {len(endpoints)} endpoints\n\n")
        for ep in sorted(endpoints, key=lambda x: (x["path"], x["method"])):
            f.write(f"- `{ep['method']}` `{ep['path']}`")
            if ep["summary"]:
                f.write(f" - {ep['summary']}")
            if ep["operationId"]:
                f.write(f" (`{ep['operationId']}`)")
            f.write("\n")
    print(f"Saved endpoints list to {ENDPOINTS_MD}")

    # Save merged OpenAPI
    with open(MERGED_OPENAPI, "w", encoding="utf-8") as f:
        json.dump({"paths": merged_paths}, f, indent=2, ensure_ascii=False)
    print(f"Saved merged OpenAPI to {MERGED_OPENAPI}")

    # Save sync metadata
    from datetime import datetime
    meta = {
        "synced_at": datetime.now().isoformat(),
        "sitemap_url": SITEMAP_URL,
        "total_urls": len(urls),
        "total_endpoints": len(endpoints),
    }
    with open(SYNC_META, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    print(f"\nSync complete! {len(endpoints)} endpoints discovered.")


def cmd_list(args):
    """List available endpoints."""
    if not ENDPOINTS_JSON.exists():
        print("Error: No endpoints found. Run 'sync' first.")
        sys.exit(1)

    with open(ENDPOINTS_JSON, "r", encoding="utf-8") as f:
        endpoints = json.load(f)

    limit = args.limit or len(endpoints)
    if limit > len(endpoints):
        limit = len(endpoints)

    print(f"Showing {limit} of {len(endpoints)} endpoints:\n")
    for ep in endpoints[:limit]:
        print(f"  {ep['method']:6} {ep['path']}")
        if ep.get("summary"):
            print(f"         Summary: {ep['summary']}")
        if ep.get("operationId"):
            print(f"         OperationId: {ep['operationId']}")
        print()


def cmd_call(args):
    """Call an API endpoint."""
    token = get_api_token()

    # Determine endpoint
    path = args.path
    method = args.method or "GET"

    if args.operation_id:
        # Find endpoint by operationId
        if not ENDPOINTS_JSON.exists():
            print("Error: No endpoints found. Run 'sync' first.")
            sys.exit(1)

        with open(ENDPOINTS_JSON, "r", encoding="utf-8") as f:
            endpoints = json.load(f)

        matches = [ep for ep in endpoints if ep["operationId"] == args.operation_id]
        if not matches:
            print(f"Error: No endpoint found with operationId '{args.operation_id}'")
            sys.exit(1)

        if len(matches) > 1:
            if not args.doc_id:
                print(f"Error: Multiple endpoints found with operationId '{args.operation_id}':")
                for ep in matches:
                    print(f"  - {ep['method']} {ep['path']} (doc_id: {ep['doc_id']})")
                print("\nUse --doc-id to specify which one.")
                sys.exit(1)
            else:
                matches = [ep for ep in matches if ep["doc_id"] == args.doc_id]
                if not matches:
                    print(f"Error: No endpoint found with doc_id '{args.doc_id}'")
                    sys.exit(1)

        endpoint = matches[0]
        path = endpoint["path"]
        method = endpoint["method"]

    if not path:
        print("Error: Either --path or --operation-id must be specified.")
        sys.exit(1)

    # Build request
    url = f"{CSQAQ_API_BASE}{path}"

    # Parse query parameters
    query_params = {}
    if args.query:
        for param in args.query:
            key, _, value = param.partition("=")
            query_params[key] = value

    # Build request body
    body = None
    if args.json_body:
        body = json.loads(args.json_body)
    elif args.body_file:
        with open(args.body_file, "r", encoding="utf-8") as f:
            body = json.load(f)
    elif args.raw_body:
        body = args.raw_body

    # Make request
    import urllib.request
    import urllib.parse

    if query_params:
        url = f"{url}?{urllib.parse.urlencode(query_params)}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "CSQAQ-Market-Lookup/1.0",
    }

    data = json.dumps(body).encode("utf-8") if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method.upper())

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            if args.pretty:
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print(json.dumps(result, ensure_ascii=False))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"HTTP Error {e.code}: {e.reason}")
        print(f"Response: {error_body}")
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Request Error: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="CSQAQ Market API CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # sync command
    sync_parser = subparsers.add_parser("sync", help="Sync API docs from sitemap")

    # list command
    list_parser = subparsers.add_parser("list", help="List available endpoints")
    list_parser.add_argument("--limit", type=int, help="Limit number of endpoints to show")

    # call command
    call_parser = subparsers.add_parser("call", help="Call an API endpoint")
    call_parser.add_argument("--operation-id", help="Operation ID to call")
    call_parser.add_argument("--path", help="API path to call")
    call_parser.add_argument("--method", default="GET", help="HTTP method (default: GET)")
    call_parser.add_argument("--doc-id", help="Document ID (when operationId is not unique)")
    call_parser.add_argument("--query", nargs="*", help="Query parameters (key=value)")
    call_parser.add_argument("--json-body", help="JSON body string")
    call_parser.add_argument("--body-file", help="Path to JSON body file")
    call_parser.add_argument("--raw-body", help="Raw body string")
    call_parser.add_argument("--pretty", action="store_true", help="Pretty print JSON output")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "sync":
        cmd_sync(args)
    elif args.command == "list":
        cmd_list(args)
    elif args.command == "call":
        cmd_call(args)


if __name__ == "__main__":
    main()
