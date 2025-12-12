import http.client
import json
import time
import random
import ssl
import certifi
from pathlib import Path

# =====================================================================
# PATH CONFIG FIX (GUI + MAIN pakai lokasi yang sama)
# =====================================================================
CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "config.json"

HEADER = {
    "Content-Type": "application/json",
    "User-Agent": "DiscordBot"
}

# =====================================================================
# LOAD CONFIG
# =====================================================================
def load_config():
    try:
        cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))

        if "Config" not in cfg:
            cfg["Config"] = []
        if "RUN" not in cfg:
            cfg["RUN"] = False

        return cfg

    except Exception as e:
        print("Config error / missing:", e)
        return None


# =====================================================================
# DISCORD CONNECTION
# =====================================================================
def get_connection():
    ctx = ssl.create_default_context(cafile=certifi.where())
    return http.client.HTTPSConnection("discord.com", 443, context=ctx)


# =====================================================================
# SEND MESSAGE
# =====================================================================
def send_message(channel_id, message, token):
    try:
        conn = get_connection()
        head = HEADER.copy()
        # Authorization header — token is passed as-is. If you're using Bot tokens,
        # prefix with "Bot " in your config or here: head["Authorization"] = f"Bot {token}"
        head["Authorization"] = token
        payload = json.dumps({"content": message, "tts": False})

        conn.request("POST", f"/api/v10/channels/{channel_id}/messages", payload, head)
        resp = conn.getresponse()
        resp.read()
        conn.close()

        return 199 < resp.status < 300

    except Exception as e:
        print(f"[SEND ERROR] {e}")
        return False


# =====================================================================
# SEND WEBHOOK (start / error / finish)
# =====================================================================
def send_webhook(event, detail, webhook_url):
    embed = {
        "title": "",
        "description": "",
        "color": 0,
        "fields": [],
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

    if event == "start":
        embed["title"] = "🚀 Bot Dimulai"
        embed["description"] = "Bot sudah mulai bekerja."
        embed["color"] = 3066993

    elif event == "error":
        embed["title"] = "❌ Error"
        embed["description"] = detail.get("error", "Unknown error")
        embed["color"] = 15158332
        embed["fields"] = [
            {"name": "Akun", "value": detail.get("account", "-"), "inline": True},
            {"name": "Channel", "value": detail.get("channel", "-"), "inline": True}
        ]

    elif event == "finish":
        embed["title"] = "✅ Bot Selesai"
        total = detail.get("total_sent", 0)
        embed["description"] = f"Semua tugas selesai.\nTotal pesan terkirim: **{total}**"
        embed["color"] = 8311585

    data = {
        "username": "Bot Monitor",
        "embeds": [embed]
    }

    try:
        conn = get_connection()
        endpoint = webhook_url.replace(
            "https://discord.com/api/webhooks/",
            "/api/webhooks/"
        )
        conn.request("POST", endpoint, json.dumps(data), HEADER)
        r = conn.getresponse()
        r.read()
        conn.close()

    except Exception as e:
        print(f"[WEBHOOK ERROR] {e}")


# =====================================================================
# INTERRUPTIBLE SLEEP (GUI bisa STOP)
# =====================================================================
def interruptible_sleep(seconds):
    # check RUN flag every second
    for _ in range(seconds):
        cfg = load_config()
        if not cfg or not cfg.get("RUN", False):
            return False
        time.sleep(1)
    return True


# =====================================================================
# HELPER: build world list (compatible GUI <-> older formats)
# =====================================================================
def build_world_list_from_account(acc):
    """
    Return a list of world names that are active.
    Accepts both:
      - acc["world"] = [ {"name":"x","active":True}, ... ]
      - acc["worlds"] = ["x", "y", ...] (legacy)
      - acc["worlds"] = [{"name":"x"}, ...] (also supported)
    """
    raw = None
    if isinstance(acc.get("world"), list):
        raw = acc.get("world")
    elif isinstance(acc.get("worlds"), list):
        raw = acc.get("worlds")
    else:
        raw = []

    result = []
    for item in raw:
        # dict style (GUI)
        if isinstance(item, dict):
            name = str(item.get("name", "")).strip()
            active = item.get("active", True)
            if name and active:
                result.append(name)
        else:
            # assume string-like
            name = str(item).strip()
            if name:
                result.append(name)

    return result


# =====================================================================
# MAIN BOT LOGIC
# =====================================================================
def main():
    base_cfg = load_config()
    if not base_cfg:
        print("Config invalid")
        return

    if not base_cfg.get("RUN", False):
        print("RUN = false → bot tidak berjalan.")
        return

    # Only include accounts that are selected in config
    accounts_all = base_cfg.get("Config", [])
    accounts = [acc for acc in accounts_all if acc.get("selected", False)]

    if not accounts:
        print("Tidak ada akun yang dipilih (selected=True). Bot stop.")
        return

    # Ambil webhook dari akun pertama yang punya
    webhook_url = ""
    for acc in accounts:
        if acc.get("webhook"):
            webhook_url = acc["webhook"]
            break

    total_sent = 0

    # Webhook Start
    if webhook_url:
        send_webhook("start", {}, webhook_url)

    # Internal counter (per-channel) — use index mapping to current accounts list
    counters = {}
    for ai, acc in enumerate(accounts):
        for ci, ch in enumerate(acc.get("channels", [])):
            try:
                cnt = int(ch.get("count", 0))
            except Exception:
                cnt = 0
            # cnt > 0 => limited (will decrement)
            # cnt == 0 => unlimited
            # we'll mark finished channels with -1
            counters[(ai, ci)] = cnt if cnt > 0 else (0 if cnt == 0 else -1)

    print("BOT STARTED.")

    while True:
        cfg_now = load_config()
        if not cfg_now or not cfg_now.get("RUN", False):
            print("Bot dihentikan oleh GUI.")
            break

        all_done = True

        # reload accounts (in case config changed selected tokens etc)
        accounts_all = cfg_now.get("Config", [])
        accounts = [acc for acc in accounts_all if acc.get("selected", False)]

        # rebuild counters mapping if number of accounts / channels changed
        for ai, acc in enumerate(accounts):
            for ci, ch in enumerate(acc.get("channels", [])):
                if (ai, ci) not in counters:
                    try:
                        cnt = int(ch.get("count", 0))
                    except Exception:
                        cnt = 0
                    counters[(ai, ci)] = cnt if cnt > 0 else (0 if cnt == 0 else -1)

        for ai, acc in enumerate(accounts):
            token = acc.get("token", "")

            # Build the world list from account (only active worlds)
            world_list = build_world_list_from_account(acc)

            for ci, ch in enumerate(acc.get("channels", [])):
                cnt = counters.get((ai, ci), -1)

                if cnt == -1:
                    continue

                if cnt > 0:
                    all_done = False

                # Pilih world (random dari world_list, fallback "DEFAULT")
                world = random.choice(world_list) if world_list else "DEFAULT"
                msg = ch.get("message", "").replace("{world}", world)
                chid = ch.get("channelid", "")

                # Kirim pesan
                ok = send_message(chid, msg, token)
                if ok:
                    total_sent += 1
                    print(f"[SENT] {chid} -> {msg[:40]}...")
                else:
                    print(f"[FAILED] {chid}")
                    if webhook_url:
                        send_webhook("error", {
                            "account": acc.get("name", "-"),
                            "channel": chid,
                            "error": "Gagal mengirim pesan"
                        }, webhook_url)

                # Update counter
                if cnt > 0:
                    counters[(ai, ci)] -= 1
                    if counters[(ai, ci)] == 0:
                        counters[(ai, ci)] = -1
                        print(f"[DONE] Channel {chid} selesai.")

                # Delay
                d = ch.get("delay", [40, 60])
                try:
                    delay = random.randint(int(d[0]), int(d[1]))
                except Exception:
                    delay = 40

                if not interruptible_sleep(delay):
                    print("Bot dihentikan saat delay.")
                    return

        if all_done:
            print("SEMUA SELESAI. BOT STOP.")

            if webhook_url:
                send_webhook("finish", {"total_sent": total_sent}, webhook_url)

            break


if __name__ == "__main__":
    main()
