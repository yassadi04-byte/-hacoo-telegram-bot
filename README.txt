# Bot Telegram Hacoo

Le code promo est déjà configuré : `yass69`.

## Ce que fait le bot
- Tu lui envoies un lien Hacoo/OnlyAff.
- Il tente de récupérer automatiquement le nom et l'image via les métadonnées de la page.
- Il publie dans ton canal avec :
  - photo
  - nom
  - lien
  - code promo `yass69`
- Tu peux aussi programmer une publication.

## Installation
1. Crée un bot avec @BotFather et récupère le token.
2. Ajoute le bot comme administrateur de ton canal avec le droit de publier.
3. Configure les variables `BOT_TOKEN` et `CHANNEL_ID`.
4. Installe les dépendances :
   `pip install -r requirements.txt`
5. Lance :
   `python bot.py`

## Commandes
- `/publier LIEN`
- `/programmer 2026-09-04 18:30 LIEN`

Tu peux aussi envoyer directement un lien Hacoo au bot.

Remarque : Hacoo/OnlyAff peut parfois empêcher la récupération automatique de certaines informations. Dans ce cas, le bot ne peut pas garantir qu'il récupérera la photo ou le nom depuis la page.
