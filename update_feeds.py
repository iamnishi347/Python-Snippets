import os
import re
import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString

SNIPPETS_DIR = "snippets"
README_FILE = "README.md"
SITE_URL = "https://snippets.dft.codes"
SITEMAP_FILE = "sitemap.xml"
RSS_FILE = "rss.xml"


def get_snippets():
    snippets = []
    for fname in sorted(os.listdir(SNIPPETS_DIR), reverse=True):
        if fname.endswith((".html", ".md")):
            fpath = os.path.join(SNIPPETS_DIR, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()

                title = None
                if fname.endswith(".html"):
                    # Look for <h1>Title</h1>
                    match = re.search(r"<h1[^>]*>(.*?)</h1>", content, re.IGNORECASE)
                    if match:
                        title = match.group(1).strip()
                elif fname.endswith(".md"):
                    # Look for Markdown "# Title"
                    match = re.search(r"^#\s+(.+)", content, re.MULTILINE)
                    if match:
                        title = match.group(1).strip()

                if not title:
                    # Fallback to filename
                    title = fname.replace(".html", "").replace(".md", "")

            snippets.append((fname, title))
    return snippets


def update_readme(snippets):
    with open(README_FILE, "r", encoding="utf-8") as f:
        readme = f.read()

    snippet_lines = [f"* [{title}]({SNIPPETS_DIR}/{fname})" for fname, title in snippets]
    new_list = "\n".join(snippet_lines)

    new_readme = re.sub(
        r"(<!-- SNIPPETS:LIST -->)(.*?)(<!-- SNIPPETS:LIST-END -->)",
        f"\\1\n{new_list}\n\\3",
        readme,
        flags=re.S
    )

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(new_readme)


def generate_sitemap(snippets):
    urlset = Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for fname, _ in snippets:
        url = SubElement(urlset, "url")
        loc = SubElement(url, "loc")
        loc.text = f"{SITE_URL}/{SNIPPETS_DIR}/{fname}"
        lastmod = SubElement(url, "lastmod")
        lastmod.text = datetime.date.today().isoformat()
    xml_str = parseString(tostring(urlset)).toprettyxml(indent="  ")
    with open(SITEMAP_FILE, "w", encoding="utf-8") as f:
        f.write(xml_str)


def generate_rss(snippets):
    rss = Element("rss", version="2.0")
    channel = SubElement(rss, "channel")
    SubElement(channel, "title").text = "Python Snippets"
    SubElement(channel, "link").text = SITE_URL
    SubElement(channel, "description").text = "Daily AI-generated Python snippets"

    for fname, title in snippets:
        item = SubElement(channel, "item")
        SubElement(item, "title").text = title
        SubElement(item, "link").text = f"{SITE_URL}/{SNIPPETS_DIR}/{fname}"
        SubElement(item, "guid").text = f"{SITE_URL}/{SNIPPETS_DIR}/{fname}"
        SubElement(item, "pubDate").text = datetime.datetime.now().strftime(
            "%a, %d %b %Y %H:%M:%S +0000"
        )

    xml_str = parseString(tostring(rss)).toprettyxml(indent="  ")
    with open(RSS_FILE, "w", encoding="utf-8") as f:
        f.write(xml_str)


if __name__ == "__main__":
    snippets = get_snippets()
    update_readme(snippets)
    generate_sitemap(snippets)
    generate_rss(snippets)
    print("✅ Feeds and README updated successfully.")
