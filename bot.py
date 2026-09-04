import asyncio
import os
from datetime import datetime
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

PROMO_CODE = "yass69"
CHANNEL_ID = os.getenv("CHANNEL_ID", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Version/17.0 Mobile/15E148 Safari/604.1"
})


def is_hacoo_url(text: str) -> bool:
    try:
        host = urlparse(text).netloc.lower()
        return "hacoo" in host or "onlyaff.app" in host
    except Exception:
        return False


def get_product_info(url: str):
    r = session.get(url, timeout=20, allow_redirects=True)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    def meta(prop):
        tag = soup.find("meta", attrs={"property": prop}) or soup.find(
            "meta", attrs={"name": prop}
        )
        return tag.get("content", "").strip() if tag else ""

    title = meta("og:title") or (
        soup.title.string.strip() if soup.title and soup.title.string else ""
    )
    image = meta("og:image")
    return title or "Article Hacoo", image


def make_caption(title: str, url: str) -> str:
    return (
        f"🛍️ <b>{title}</b>\n\n"
        f"🔗 <b>Lien :</b> {url}\n\n"
        f"🎟️ <b>Code promo :</b> <code>{PROMO_CODE}</code>"
    )


async def publish(url: str, bot):
    title, image = await asyncio.to_thread(get_product_info, url)
    caption = make_caption(title, url)

    if image:
        try:
            await bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=image,
                caption=caption,
                parse_mode="HTML",
            )
            return
        except Exception:
            pass

    await bot.send_message(
        chat_id=CHANNEL_ID,
        text=caption,
        parse_mode="HTML",
        disable_web_page_preview=False,
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot Hacoo prêt.\n\n"
        "Envoie simplement un lien Hacoo/OnlyAff et je le publie dans le canal.\n\n"
        "Commande immédiate : /publier <lien>\n"
        "Commande programmée : /programmer <AAAA-MM-JJ HH:MM> <lien>"
    )


async def publier(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Utilisation : /publier <lien>")
        return

    url = context.args[0].strip()
    if not is_hacoo_url(url):
        await update.message.reply_text("❌ Envoie un lien Hacoo ou OnlyAff valide.")
        return

    try:
        await publish(url, context.bot)
        await update.message.reply_text("✅ Publication envoyée sur le canal.")
    except Exception as e:
        await update.message.reply_text(
            "⚠️ Je n'arrive pas à récupérer automatiquement les infos de cet article. "
            "Le site peut bloquer l'accès automatique.\n"
            f"Détail technique : {type(e).__name__}"
        )


async def scheduled_job(url: str, bot, delay: float):
    await asyncio.sleep(delay)
    try:
        await publish(url, bot)
        print("Publication programmée envoyée.")
    except Exception as e:
        print("Erreur publication programmée:", e)


async def programmer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 3:
        await update.message.reply_text(
            "Utilisation : /programmer 2026-09-04 18:30 <lien>"
        )
        return

    date_str = f"{context.args[0]} {context.args[1]}"
    url = context.args[2].strip()

    if not is_hacoo_url(url):
        await update.message.reply_text("❌ Envoie un lien Hacoo ou OnlyAff valide.")
        return

    try:
        when = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
    except ValueError:
        await update.message.reply_text("❌ Date invalide. Exemple : 2026-09-04 18:30")
        return

    delay = (when - datetime.now()).total_seconds()
    if delay <= 0:
        await update.message.reply_text("❌ Cette heure est déjà passée.")
        return

    # The task runs inside the bot's active asyncio event loop.
    context.application.create_task(
        scheduled_job(url, context.bot, delay),
        update=update,
        name=f"scheduled-{when.isoformat()}"
    )
    await update.message.reply_text(
        f"⏰ Article programmé pour {when.strftime('%d/%m/%Y à %H:%M')}."
    )


async def plain_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    if is_hacoo_url(text):
        await update.message.reply_text("⏳ Je prépare la publication…")
        try:
            await publish(text, context.bot)
            await update.message.reply_text("✅ Article publié.")
        except Exception as e:
            await update.message.reply_text(
                "⚠️ Je n'ai pas pu récupérer automatiquement la photo/nom. "
                "Utilise /publier <lien> pour réessayer."
            )


def main():
    if not BOT_TOKEN or not CHANNEL_ID:
        raise SystemExit("Configure BOT_TOKEN et CHANNEL_ID avant de lancer le bot.")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("publier", publier))
    app.add_handler(CommandHandler("programmer", programmer))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, plain_link))

    print("Bot Hacoo démarré.")
    app.run_polling()


if __name__ == "__main__":
    main()
