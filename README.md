# SubdomainTabber

Small utility to display DNS records for a domain or URL and to query crt.sh for certificate-related hostnames.

crt.sh is used because many subdomains only become discoverable when they appear in certificate transparency logs; there are few reliable alternatives for finding leaked subdomains beyond certificate records :)

Prerequisites
- Python 3.8+ (or any modern Python 3)
- `dnspython` package

Quick install

```bash
python3 -m pip install --user -r requirements.txt
```

Run

```bash
python3 run.py
# or make it executable and run
./run.py
```

Usage
- Enter a domain or URL when prompted (e.g. `example.com` or `https://example.com`).
- The script prints common DNS records and performs a passive `crt.sh` lookup for certificate names.
- If `crt.sh` returns hostnames, you'll be offered the option to open them as `https://<host>` in new browser tabs.

Privacy & safety
- The `crt.sh` query is passive (public certificate transparency logs).
- Opening many discovered hosts in browser tabs may be noisy — use the prompt to opt out.

License

This repository is released under the MIT License. See [LICENSE](LICENSE) for details.
