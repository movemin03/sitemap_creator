import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
import xml.etree.ElementTree as ET

class Sitemap:
    def __init__(self):
        self.urls = []

    def add_url(self, loc, lastmod=None, changefreq='daily', priority=0.5):
        url_data = {
            'loc': loc,
            'lastmod': lastmod,
            'changefreq': changefreq,
            'priority': str(priority)
        }
        self.urls.append(url_data)

    def write_xml(self, filename='sitemap.xml'):
        root = ET.Element('urlset')
        root.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')

        for url_data in self.urls:
            url_element = ET.SubElement(root, 'url')

            loc_element = ET.SubElement(url_element, 'loc')
            loc_element.text = url_data['loc']

            if url_data['lastmod']:
                lastmod_element = ET.SubElement(url_element, 'lastmod')
                lastmod_element.text = url_data['lastmod']

            changefreq_element = ET.SubElement(url_element, 'changefreq')
            changefreq_element.text = url_data['changefreq']

            priority_element = ET.SubElement(url_element, 'priority')
            priority_element.text = url_data['priority']

        tree = ET.ElementTree(root)
        tree.write(filename, encoding='utf-8', xml_declaration=True)

def crawl(url, sitemap, visited_urls, max_depth):
    if max_depth == 0:
        return

    if url in visited_urls:
        return

    visited_urls.add(url)

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        print(f"Failed to crawl: {url}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')

    lastmod = datetime.now().isoformat()

    sitemap.add_url(url, lastmod=lastmod)

    for link in soup.find_all('a', href=True):
        next_url = urljoin(url, link['href'])
        crawl(next_url, sitemap, visited_urls, max_depth - 1)

def create_sitemap(base_url, max_depth=2):
    sitemap = Sitemap()
    visited_urls = set()
    crawl(base_url, sitemap, visited_urls, max_depth)
    sitemap.write_xml()

if __name__ == "__main__":
    base_url = input("사이트 도메인 URL을 입력하세요: ")
    max_depth = int(input("최대 크롤링 깊이를 입력하세요 (기본값 2): ") or 2)
    create_sitemap(base_url, max_depth)
    print("사이트맵 생성이 완료되었습니다.")
