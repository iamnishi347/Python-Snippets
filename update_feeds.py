import os
import datetime

BASE_URL = "https://snippets.dft.codes"
SNIPPETS_DIR = "snippets"

def get_snippets():
    files = sorted(os.listdir(SNIPPETS_DIR))
    snippets = []
    for f in files:
        if f.endswith(".md"):
            date_str = f.replace(".md", "")
            url = f"{BASE_URL}/snippets/{f.replace('.md','.html')}"
            snippets.append((date_str, url))
    return snippets

def update_rss(snippets):
    now = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
    items = ""
    for date_str, url in snippets[::-1]:  # latest first
        pub_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").strftime("%a, %d %b %Y 00:00:00 GMT")
        items += f"""
    <item>
      <title>Snippet {date_str}</title>
      <link>{url}</link>
      <guid>{url}</guid>
      <pubDate>{pub_date}</pubDate>
      <description>Daily Python snippet for {date_str}</description>
    </item>"""
    rss = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
  <channel>
    <title>Python Snippets</title>
    <link>{BASE_URL}</link>
    <description>Daily Python snippets for learning and reference</description>
    <language>en-us</language>
    <lastBuildDate>{now}</lastBuildDate>
    {items}
  </channel>
</rss>"""
    with open("rss.xml", "w") as f:
        f.write(rss)

def update_sitemap(snippets):
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    urls = f"""
  <url>
    <loc>{BASE_URL}/</loc>
    <lastmod>{now}</lastmod>
    <changefreq>daily</changefreq>
  </url>"""
    for date_str, url in snippets:
        urls += f"""
  <url>
    <loc>{url}</loc>
    <lastmod>{date_str}</lastmod>
    <changefreq>daily</changefreq>
  </url>"""
    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}
</urlset>"""
    with open("sitemap.xml", "w") as f:
        f.write(sitemap)

if __name__ == "__main__":
    snippets = get_snippets()
    update_rss(snippets)
    update_sitemap(snippets)
