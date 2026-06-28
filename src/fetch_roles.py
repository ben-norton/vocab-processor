"""Fetch and parse CI_RoleCode entries from ISO 19115-3 CIT codelist HTML."""

import urllib.request
import re

url = 'https://standards.iso.org/iso/19115/-3/cit/1.0/codelists.html'
with urllib.request.urlopen(url, timeout=20) as resp:
    html = resp.read().decode('utf-8', errors='replace')

# Find the CI_RoleCode anchor and extract everything up to the next top-link
start = html.find('CI_RoleCode')
# Find the table that follows
table_start = html.find('<table', start)
table_end   = html.find('</table>', table_start) + len('</table>')
table_html  = html[table_start:table_end]

# Pull out all <td> text content (strip tags and whitespace)
tds = re.findall(r'<td[^>]*>(.*?)</td>', table_html, re.DOTALL)
tds = [re.sub(r'<[^>]+>', '', td).strip() for td in tds]
tds = [t for t in tds if t]

# Pair them up: (entry, definition)
roles = []
for i in range(0, len(tds) - 1, 2):
    roles.append((tds[i], tds[i+1]))

print(f"Found {len(roles)} CI_RoleCode entries:\n")
for entry, defn in roles:
    print(f"  {entry!r}: {defn!r}")
