from celery import shared_task
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from datetime import timedelta
from jobs_sync.sync_jobs import run_all_syncs
from jobs_sync.models import JobSyncLog

# -------------------------
# existing auto_sync_jobs (keep as-is)
# -------------------------
@shared_task
def auto_sync_jobs():
    recipient = "Artisanrevsuretechnology@gmail.com"
    site_name = "Spectrum Arena"
    logo_url = "https://res.cloudinary.com/drfiqlo5s/image/upload/v1762974116/logo_fu1xqv.png"
    start_time = timezone.now()
    try:
        print("🔁 Running scheduled job sync...")
        run_all_syncs()
        log = JobSyncLog.objects.create(
            source="All",
            status="SUCCESS",
            new_jobs=0,
            message="All job sources synced successfully.",
            run_time=start_time,
        )
        html_content = f"""<html>...SUCCESS HTML (same as your current version)...</html>"""
        # Use the EmailMultiAlternatives version you already have
        msg = EmailMultiAlternatives(
            subject=f"✅ {site_name} Job Sync Report",
            body=f"{site_name} job sync completed successfully at {start_time}.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        print("✅ HTML report with logo sent successfully.")
    except Exception as e:
        log = JobSyncLog.objects.create(
            source="All",
            status="FAILED",
            new_jobs=0,
            message=str(e),
            run_time=start_time,
        )
        html_content = f"""<html>...FAIL HTML (same as your current version)...</html>"""
        msg = EmailMultiAlternatives(
            subject=f"❌ {site_name} Job Sync Failed",
            body=f"{site_name} job sync failed: {e}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        print(f"❌ Job sync failed and failure report email sent: {e}")


# -------------------------
# NEW: Daily Summary Digest
# -------------------------
@shared_task
def daily_sync_summary():
    """
    Compile JobSyncLog entries from the past 24 hours and email a summarized report.
    Scheduled by Celery Beat (once daily, shortly after midnight).
    """
    recipient = "Artisanrevsuretechnology@gmail.com"
    site_name = "Spectrum Arena"
    logo_url = "https://res.cloudinary.com/drfiqlo5s/image/upload/v1762974116/logo_fu1xqv.png"
    now = timezone.now()
    since = now - timedelta(days=1)

    # Gather logs for past 24 hours
    qs = JobSyncLog.objects.filter(run_time__gte=since)
    total_runs = qs.count()
    successes = qs.filter(status="SUCCESS").count()
    failures = qs.filter(status="FAILED").count()
    new_jobs_total = sum(qs.values_list("new_jobs", flat=True)) if total_runs else 0
    last_run = qs.order_by("-run_time").first()
    last_run_str = last_run.run_time.strftime("%Y-%m-%d %H:%M:%S") if last_run else "N/A"

    # Build a clean HTML summary table
    html_rows = ""
    # add each log row (optional - comment out if you want compact summary)
    for log in qs.order_by("-run_time"):
        html_rows += f"""
        <tr style="background:#1b1b1b;">
            <td style="padding:8px;border:1px solid #333;">{log.run_time.strftime('%Y-%m-%d %H:%M:%S')}</td>
            <td style="padding:8px;border:1px solid #333;">{log.source}</td>
            <td style="padding:8px;border:1px solid #333;color:{'#00ff99' if log.status=='SUCCESS' else '#ff6b6b'};">{log.status}</td>
            <td style="padding:8px;border:1px solid #333;">{log.new_jobs}</td>
            <td style="padding:8px;border:1px solid #333;">{(log.message[:120] + '...') if log.message and len(log.message) > 120 else (log.message or '')}</td>
        </tr>
        """

    # Compose HTML body (branded)
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"><meta name="viewport" content="width=device-width"></head>
    <body style="margin:0;background:#0a0a0a;font-family:Arial,color:#e0e0e0">
      <div style="max-width:700px;margin:20px auto;background:#111;border-radius:12px;overflow:hidden;border:1px solid #222;">
        <div style="background:linear-gradient(90deg,#00ff99,#0088ff);padding:18px;text-align:center;">
          <img src="{logo_url}" alt="{site_name}" style="width:72px;border-radius:10px;margin-bottom:8px;">
          <h2 style="color:#fff;margin:0;">{site_name} — Daily Sync Summary</h2>
        </div>

        <div style="padding:20px;">
          <p style="color:#ccc;font-size:14px;">
            Summary for the last 24 hours (since {since.strftime('%Y-%m-%d %H:%M:%S')}).
          </p>

          <table style="width:100%;border-collapse:collapse;margin-top:12px;">
            <tr><td style="padding:10px;border:1px solid #333;">Total Sync Runs</td><td style="padding:10px;border:1px solid #333;">{total_runs}</td></tr>
            <tr style="background:#1b1b1b;"><td style="padding:10px;border:1px solid #333;">Successful</td><td style="padding:10px;border:1px solid #333;color:#00ff99;">{successes}</td></tr>
            <tr><td style="padding:10px;border:1px solid #333;">Failed</td><td style="padding:10px;border:1px solid #333;color:#ff6b6b;">{failures}</td></tr>
            <tr style="background:#1b1b1b;"><td style="padding:10px;border:1px solid #333;">New Jobs Added</td><td style="padding:10px;border:1px solid #333;">{new_jobs_total}</td></tr>
            <tr><td style="padding:10px;border:1px solid #333;">Last Run</td><td style="padding:10px;border:1px solid #333;">{last_run_str}</td></tr>
          </table>

          <h3 style="color:#00ff99;margin-top:20px;">Recent Runs</h3>
          <table style="width:100%;border-collapse:collapse;margin-top:8px;">
            <thead>
              <tr style="background:#0f0f0f;color:#bbb;">
                <th style="padding:8px;border:1px solid #333;text-align:left;">Run Time</th>
                <th style="padding:8px;border:1px solid #333;text-align:left;">Source</th>
                <th style="padding:8px;border:1px solid #333;text-align:left;">Status</th>
                <th style="padding:8px;border:1px solid #333;text-align:left;">New Jobs</th>
                <th style="padding:8px;border:1px solid #333;text-align:left;">Message</th>
              </tr>
            </thead>
            <tbody>
              {html_rows if html_rows else '<tr><td colspan="5" style="padding:12px;border:1px solid #333;">No runs in the last 24 hours.</td></tr>'}
            </tbody>
          </table>

          <div style="text-align:center;margin-top:18px;">
            <a href="https://spectrumarena.io" style="display:inline-block;padding:10px 20px;border-radius:8px;background:linear-gradient(90deg,#00ff99,#00aaff);color:#000;font-weight:bold;text-decoration:none;">Open Dashboard</a>
          </div>
        </div>

        <div style="background:#0d0d0d;padding:14px;text-align:center;color:#666;font-size:12px;border-top:1px solid #222;">
          &copy; {now.year} {site_name} — Sent automatically by the backend.
        </div>
      </div>
    </body>
    </html>
    """

    # Subject and send
    subject = f"📊 {site_name} Daily Sync Summary — {now.strftime('%Y-%m-%d')}"
    msg = EmailMultiAlternatives(
        subject=subject,
        body=f"{site_name} daily sync summary for {now.strftime('%Y-%m-%d')}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient],
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()

    print(f"✅ Daily summary email sent: runs={total_runs} successes={successes} failures={failures} new_jobs={new_jobs_total}")

