from rss_fetch import fetch_rss_feeds
from filter import filter_items
from summarize import format_summaries, ai_daily_digest
from dedup import load_posted_links, save_posted_links

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
    
    posted_links = load_posted_links()
    
    items = fetch_rss_feeds(feeds)
    items = filter_items(items)

    fresh_items = [
    item for item in items
    if item.get("link") and item["link"] not in posted_links
    ]

    if not fresh_items:
        print("No new articles to post.")
        return

    ai_content = ai_daily_digest(fresh_items)

    if ai_content:
        post_content = ai_content
    else:
        post_content = format_summaries(fresh_items)    
    print(post_content)

    new_links = [item["link"] for item in fresh_items]
    posted_links.update(new_links)
    save_posted_links(posted_links)

if __name__ == "__main__":
    main()