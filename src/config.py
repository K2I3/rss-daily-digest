import os
from dataclasses import dataclass

import yaml
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    db_path: str
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    mail_to: list


def load_settings() -> Settings:
    """環境変数(.env または GitHub Actions の Secrets)から設定を読み込む"""
    return Settings(
        db_path=os.environ.get("DB_PATH", "data/rss_digest.db"),
        smtp_host=os.environ.get("SMTP_HOST", "smtp.gmail.com"),
        smtp_port=int(os.environ.get("SMTP_PORT", "587")),
        smtp_user=os.environ["SMTP_USER"],
        smtp_password=os.environ["SMTP_PASSWORD"],
        mail_to=[addr.strip() for addr in os.environ["MAIL_TO"].split(",")],
    )


def load_feeds(path: str = "feeds.yaml") -> list:
    """収集対象のRSSフィード一覧を読み込む"""
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data["feeds"]
