import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from html import escape


def build_html_body(entries: list, distribution_date: str) -> str:
    if not entries:
        content = '<p>本日は対象期間内に新着記事がありませんでした。</p>'
    else:
        rows = []
        for e in entries:
            rows.append(f"""
            <li style="margin-bottom:10px;">
                <a href="{escape(e['link'])}">{escape(e['title'])}</a>
                <span style="color:#888; font-size:12px;"> ({escape(e['feed_name'])})</span>
            </li>
            """)
        content = f'<ul style="padding-left:20px;">{"".join(rows)}</ul>'

    return f"""
    <html><body style="font-family: sans-serif; color:#222;">
        <h2>{escape(distribution_date)} 新着RSS一覧({len(entries)}件)</h2>
        {content}
    </body></html>
    """


def send_digest_email(entries: list, distribution_date: str, settings):
    body = build_html_body(entries, distribution_date)
    subject_count = f"新着{len(entries)}件" if entries else "配信なし"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"【RSS日次配信】{distribution_date} {subject_count}"
    msg["From"] = settings.smtp_user
    msg["To"] = ", ".join(settings.mail_to)
    msg.attach(MIMEText(body, "html", "utf-8"))

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        server.login(settings.smtp_user, settings.smtp_password)
        server.sendmail(settings.smtp_user, settings.mail_to, msg.as_string())
