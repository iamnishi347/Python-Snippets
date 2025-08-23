import os
import datetime
import subprocess

BASE_URL = "https://snippets.dft.codes"
SNIPPETS_DIR = "snippets"

def get_last_modified(file_path):
    """Get last modified date from git log (fallback: filesystem mtime)."""
    try:
        timestamp = subprocess.check_output(
            ["git", "log", "-1", "--format=%ct", file_path],
            text=True
        ).strip()
        return datetime.datetime.utcfromtimestamp(int(timestamp)).strftime("%a, %d %b %Y %H:%M:%S GMT")
    except Exception:
        mtime = os.path.getmtime(file_path)
        return datetime.datetime.utcfromtimestamp(mtime).strftime("%a, %d %b %Y %H:%M:%S GMT")

def generate_sitemap(snippets):
    urls = ""
    for slug, date in snippets:
        urls += f"""
  <url>
    <loc>{BASE_URL}/snippets/{slug}</loc>
    <lastmod>{date.split()[0]}</lastmod>
    <priority>0.8</priority>
  </url>"""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{BASE_URL}/</loc>
    <priority>1.0</priority>
  </url>{urls}
</urlset>"""

def generate_rss(snippets):
    items = ""
    for slug, date in snippets:
        items += f"""
    <item>
      <title>{slug}</title>
      <link>{BASE_URL}/snippets/{slug}</link>
      <guid>{BASE_URL}/snippets/{slug}</guid>
      <pubDate>{date}</pubDate>
      <description><![CDATA[ Python snippet: {slug} ]]></description>
    </item>"""
    lastBuildDate = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
    return f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
  <channel>
    <title>Python Snippets</title>
    <link>{BASE_URL}/</link>
    <description>Daily updated Python code snippets</description>
    <language>en-us</language>
    <lastBuildDate>{lastBuildDate}</lastBuildDate>{items}
  </channel>
</rss>"""

def main():
    snippets = []
    for fname in os.listdir(SNIPPETS_DIR):
        if fname.endswith((".py", ".md")):
            path = os.path.join(SNIPPETS_DIR, fname)
            slug = os.path.splitext(fname)[0]
            date = get_last_modified(path)
            snippets.append((slug, date))

    # Sort by last modified date (latest first)
    snippets.sort(key=lambda x: x[1], reverse=True)

    # Write files
    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write(generate_sitemap(snippets))

    with open("rss.xml", "w", encoding="utf-8") as f:
        f.write(generate_rss(snippets))

if __name__ == "__main__":
    main()
