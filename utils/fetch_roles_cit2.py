"""Fetch CI_RoleCode entries from both ISO 19115-3 CIT 1.0 and CIT 2.0 codelists."""
import urllib.request
import re


def fetch_roles(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=20) as resp:
        html = resp.read().decode('utf-8', errors='replace')
    start = html.find('CI_RoleCode')
    table_start = html.find('<table', start)
    table_end   = html.find('</table>', table_start) + len('</table>')
    table_html  = html[table_start:table_end]
    tds = re.findall(r'<td[^>]*>(.*?)</td>', table_html, re.DOTALL)
    tds = [re.sub(r'<[^>]+>', '', td).strip() for td in tds]
    tds = [re.sub(r'\s+', ' ', t) for t in tds if t]
    roles = []
    for i in range(0, len(tds) - 1, 2):
        roles.append((tds[i], tds[i+1]))
    return roles


v1 = fetch_roles('https://standards.iso.org/iso/19115/-3/cit/1.0/codelists.html')
v2 = fetch_roles('https://standards.iso.org/iso/19115/-3/cit/2.0/codelists.html')

v1_names = {r[0] for r in v1}
v2_names = {r[0] for r in v2}

print(f"CIT 1.0: {len(v1)} roles")
print(f"CIT 2.0: {len(v2)} roles")
print(f"In 2.0 but NOT 1.0: {v2_names - v1_names}")
print(f"In 1.0 but NOT 2.0: {v1_names - v2_names}")

print("\n=== CIT 2.0 full list ===")
for entry, defn in v2:
    marker = " [NEW]" if entry not in v1_names else ""
    print(f"  {entry!r}{marker}: {defn!r}")
