#!/usr/bin/env python3
"""Display DNS records for a domain or URL and query crt.sh for certificate hostnames.

Usage: run the script and enter a domain or URL when prompted.
Requires: dnspython (pip3 install dnspython)
"""
import sys
from urllib.parse import urlparse
import urllib.request
import urllib.parse
import json
import webbrowser

try:
    import dns.resolver
    import dns.exception
except Exception:
    print("Missing dnspython. Install with: python3 -m pip install --user dnspython")
    sys.exit(1)

RESOLVER = dns.resolver.Resolver()
RESOLVER.lifetime = 5
RESOLVER.timeout = 3

# Common DNS types to query
RECORD_TYPES = [
    "A", "AAAA", "CNAME", "MX", "NS", "TXT", "SOA", "SRV",
    "NAPTR", "PTR", "CERT", "TLSA", "DS", "DNSKEY", "RRSIG", "SMIMEA", "SPF", "ANY"
]

def extract_domain(input_text: str) -> str:
    if not input_text:
        return ""
    text = input_text.strip()
    if "://" not in text:
        text = "http://" + text
    parsed = urlparse(text)
    return parsed.hostname or input_text

def query_record(domain: str, rtype: str):
    try:
        answers = RESOLVER.resolve(domain, rtype)
        return [a.to_text() for a in answers]
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
        return []
    except dns.exception.Timeout:
        return [f"<timeout querying {rtype}>"]
    except Exception as e:
        return [f"<error: {e}>"]

def print_records(domain: str, types=RECORD_TYPES):
    print(f"\nDNS records for: {domain}\n")
    for rtype in types:
        vals = query_record(domain, rtype)
        print(f"{rtype}:")
        if not vals:
            print("  (none)")
        else:
            for v in vals:
                print("  ", v)
    print()

def query_crtsh(domain: str, timeout: int = 10):
    """Query crt.sh (certificate transparency) and return a set of hostnames related to domain."""
    found = set()
    try:
        q = urllib.parse.quote(f"%.{domain}")
        url = f"https://crt.sh/?q={q}&output=json"
        req = urllib.request.Request(url, headers={"User-Agent": "curl/7.64"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = r.read()
        if not data:
            return found
        parsed = json.loads(data.decode("utf-8"))
        for entry in parsed:
            name_value = entry.get("name_value", "")
            for name in name_value.splitlines():
                name = name.strip().rstrip(".")
                if not name:
                    continue
                # include only names within the target domain
                if name == domain or name.endswith("." + domain):
                    found.add(name)
    except Exception:
        # ignore failures (network, rate-limit, parsing)
        pass
    return found

def open_host_tabs(names):
    """Open each discovered hostname directly (https://<hostname>) in new browser tabs."""
    for n in sorted(names):
        host = n.rstrip(".").rstrip("/")
        url = "https://" + host
        webbrowser.open_new_tab(url)

def main():
    try:
        user = input("Enter domain or URL: ").strip()
    except EOFError:
        return
    domain = extract_domain(user)
    if not domain:
        print("No domain parsed.")
        return
    print_records(domain)

    print("Querying crt.sh for certificate hostnames (passive)...")
    crt_names = query_crtsh(domain)
    if crt_names:
        print(f"\ncrt.sh results ({len(crt_names)} unique names):")
        for n in sorted(crt_names):
            print(" ", n)

        # Ask user whether to open each discovered hostname directly in browser tabs
        open_q = input("\nOpen these hostnames (https://<host>) in new browser tabs? [y/N]: ").strip().lower()
        if open_q == "y":
            open_host_tabs(crt_names)
            print("Opened host pages in the default browser.")
        else:
            print("Skipped opening host pages.")
    else:
        print("\ncrt.sh returned no names or the query failed/was rate-limited.")

if __name__ == "__main__":
    main()