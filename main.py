from rss_fetch import fetch_rss_feeds
from filter import filter_items


def main():
    feeds = [
        ("The Hacker News", "https://feeds.feedburner.com/TheHackersNews"),
        ("Krebs on Security", "https://krebsonsecurity.com/feed/"),
        ("CISA", "https://www.cisa.gov/cybersecurity-advisories/all.xml"),
        ("BleepingComputer", "https://www.bleepingcomputer.com/feed/"),
        ("Dark Reading", "https://www.darkreading.com/rss.xml"),
        ("Google Security Blog", "https://security.googleblog.com/feeds/posts/default"),
        ("Schneier on Security", "https://www.schneier.com/feed/atom/"),
    ]    
    items = fetch_rss_feeds(feeds)
    items = filter_items(items)
    for item in items:
        print(f"- [{item['source']}] {item['title']}\n  \nSummary: {item['summary']} \n\nFull article: {item['link']}\n")

if __name__ == "__main__":
    main()