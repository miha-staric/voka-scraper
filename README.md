# 🗑️🪰 voka-scraper

![GitHub release (latest by tag)](https://img.shields.io/github/v/release/miha-staric/voka-scraper)
![Language](https://img.shields.io/badge/language-Python-blue)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-blue)
![License](https://img.shields.io/github/license/miha-staric/voka-scraper)

Scraper for VoKa underground garbage cans

![VoKa Scraper in Action](https://github.com/user-attachments/assets/788511e0-59e0-4036-8ca6-dfe36d173e47)


## 📘 Background

Ljubljana, the capital of Slovenia, has recently built a network of underground garbage bins, managed by the city's waste disposal company VoKa Snaga. These bins are aimed at enhancing urban cleanliness and sustainability and are installed primarily in the city center. The units replace traditional street-level bins, reducing visual clutter and improving public space aesthetics. The system comprises numerous underground collection units, each serving multiple waste categories, including glass, paper, and packaging, which are free to use, while biological and residual waste need to be charged for.

Residents and businesses access the units for mixed and biological trash using a special RFID card. Each of these cards has its own `chip card number` and a `password` which one can use to check the number of disposals that have been made on their account. The official website for checking the disposal data leaves much to be desired. This is why the author of `voka-scraper` decided to take the matter in his own hands and build this user-friendly script to skip the not-so-pleasant web interface.

![VoKa Underground Bins With Trash Around](https://github.com/user-attachments/assets/500d6110-6a88-46d7-af7b-dd0d9505556a)

## 🗑️ Disposals

To quote the VoKa's webpage at <https://www.mojiodpadki.si/odpadki/podzemne-zbiralnice>, the fixed disposals included in the price are:

BIO: 8x
MKO: 6x

The price for extra BIO disposal is 0.1335 EUR and for MKO disposal 2.4809 EUR.

Note that BIO is Biological trash and MKO is Residual trash (mešani komunalni odpadki).

The following was taken from the website on 2. 6. 2025, so the current prices may be higher!

```txt
Cena enega vnosa preostanka odpadkov je 2,4809 €, cena enega vnosa BIO odpadkov pa 0,1335 €.
Mesečni strošek za ravnanje z odpadki za štirinajst minimalnih vnosov (šestkrat preostanek
odpadkov in osemkrat BIO odpadki) skupaj z DDV znaša 15,95 €.
```

Here's a funny ChatGPT translation for your enjoyment as well:

```txt
The thrilling price for one entry of leftover trash is a whopping €2.4809 — truly a bargain!
Meanwhile, the oh-so-precious BIO waste will only set you back €0.1335 per entry.
Now, if you’re feeling extra generous and go for fourteen minimum entries a month (six times
the glamorous leftover trash and eight times the fabulous BIO waste), your grand total
with VAT will be a mere €15.95. What a steal for dealing with your garbage royalty-style!
```

## 🐳 Running the app using Docker

Create a docker container using:

```bash
docker build -t voka-scraper .
```

Then simply run the container using this command:

```bash
docker run --rm voka-scraper
```

You should, of course, override individual config settings using the following command syntax:

```bash
docker run --rm \
  -e date_from='01.01.2025' \
  -e date_to='31.01.2025' \
  -e chip_card_number='{your_chip_card_number}' \
  -e password='{your_chip_card_password}' \
  -e mode='default' \
  -e min_bio=1.068 \
  -e min_mko=14.8854 \
  voka-scraper
```
