import logging
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from config import load_feeds, load_settings
from rss_fetcher import fetch_new_entries
from database import init_db, is_url_processed, save_entry
from mailer import send_digest_email

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

JST = ZoneInfo("Asia/Tokyo")


def get_time_window():
    """
    「前日8:00(JST)〜当日8:00(JST)」の範囲をUTCのdatetimeで返す。
    実行が多少ずれても(例: 8:05実行など)正しく当日8:00を境界として計算する。
    """
    now_jst = datetime.now(JST)
    window_end_jst = now_jst.replace(hour=8, minute=0, second=0, microsecond=0)

    # まだ当日8:00になっていない時刻に実行された場合は、前日8:00を終端とする
    if now_jst < window_end_jst:
        window_end_jst -= timedelta(days=1)

    window_start_jst = window_end_jst - timedelta(days=1)

    return (
        window_start_jst.astimezone(timezone.utc),
        window_end_jst.astimezone(timezone.utc),
        window_end_jst,  # メール件名・DB用にJSTの日付も返す
    )


def main():
    settings = load_settings()
    feeds = load_feeds()
    init_db(settings.db_path)

    window_start, window_end, window_end_jst = get_time_window()
    distribution_date = window_end_jst.strftime("%Y-%m-%d")

    logger.info(f"収集対象期間(UTC): {window_start} 〜 {window_end}")
    logger.info(f"配信日(JST): {distribution_date}")

    collected = []

    for feed in feeds:
        logger.info(f"フィード取得中: {feed['name']} ({feed['url']})")
        try:
            entries = fetch_new_entries(feed["url"], window_start, window_end)
        except Exception as e:
            logger.error(f"フィード取得失敗: {feed['url']} - {e}")
            continue

        for entry in entries:
            if not entry["link"]:
                continue

            if is_url_processed(settings.db_path, entry["link"]):
                logger.info(f"既存記事のためスキップ: {entry['link']}")
                continue

            record = {
                "distribution_date": distribution_date,
                "feed_name": feed["name"],
                "title": entry["title"],
                "link": entry["link"],
            }
            save_entry(settings.db_path, record)
            collected.append(record)

    logger.info(f"新規記事件数: {len(collected)}")

    if not collected:
        logger.info("新着記事がないため、配信なし通知メールを送信します")
    send_digest_email(entries=collected, distribution_date=distribution_date, settings=settings)
    logger.info("メール送信完了")


if __name__ == "__main__":
    main()
