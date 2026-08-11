from datetime import datetime, timezone

import feedparser


def fetch_new_entries(feed_url: str, window_start: datetime, window_end: datetime) -> list:
    """
    指定したRSSフィードから window_start <= 公開日時 < window_end
    に該当する記事のみを抽出する。(window_start / window_end はUTCのdatetime)
    """
    parsed = feedparser.parse(feed_url)
    results = []

    for entry in parsed.entries:
        published_struct = entry.get("published_parsed") or entry.get("updated_parsed")
        if not published_struct:
            # 公開日時が取得できないエントリはスキップ
            continue

        published_dt = datetime(*published_struct[:6], tzinfo=timezone.utc)

        if window_start <= published_dt < window_end:
            results.append({
                "title": entry.get("title", "(タイトルなし)"),
                "link": entry.get("link"),
                "published": published_dt.isoformat(),
            })

    return results
