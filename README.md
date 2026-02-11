# LocalLink — local business browser

LocalLink is a small desktop app for discovering and bookmarking local businesses. It's a demo-style project built with Python and PySide6 that shows how a simple, offline-friendly business directory could work.

What you can do
- browse and search a list of sample businesses
- filter and sort results (by name, rating, reviews, or deals)
- open a business detail page with reviews and deals
- favorite/bookmark businesses and keep them between app runs (saved to `data/user_data.json`)
- leave reviews (your reviews can be removed by you)
- export all businesses or just your favorites as CSV
- view basic stats (counts and average ratings by category) and get simple recommendations

# Requirements
- Python 3.14 or later
- See `requirements.txt` for Python dependencies (includes `PySide6`)

# Quick install
1. make a virtual environment and activate it (recommended)

Windows (PowerShell):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install requirements:

```bash
python -m pip install -r requirements.txt
```

Run the app

```bash
python main.py
```

# How to use
- open the Search page to browse or search the sample businesses
- click a business to see details, reviews, and deals
- click the star on a business page to add or remove it from Favorites
- favorites are saved in `data/user_data.json` so they persist between runs
- use Settings to switch theme (dark/light), toggle recommendations, turn off animations (reduce motion), require confirmation before removing favorites, or set the menu to always on top.
- export businesses or favorites to CSV from Settings

# Project layout
- `main.py` — application entry point and window setup
- `ui/` — UI widgets and window pages (captcha, sidebar, business views)
- `data/` — sample data (`businesses.json`) and the data handler (`data_handler.py`)
- `assets/` — static assets (captcha images, icons)


# Business image credits:

La Boqueria — Author: Jordiferrer — CC BY-SA 3.0
https://commons.wikimedia.org/wiki/File:La_Boqueria.JPG

Tacos de carnitas, carne asada y al pastor — Author: AlejandroLinaresGarcia — CC BY-SA 4.0
https://commons.wikimedia.org/wiki/File:001_Tacos_de_carnitas,_carne_asada_y_al_pastor.jpg

Steak dinner in France — Author: Ɱ — CC BY-SA 4.0
https://commons.wikimedia.org/wiki/File:Steak_dinner_in_France.jpg

Bakery sales counter in Paris — Author: THOR — CC BY 2.0
https://commons.wikimedia.org/wiki/File:Bakery_sales_counter_in_Paris.jpg

Café con leche — Author: Tamorlan — CC BY-SA 3.0
https://commons.wikimedia.org/wiki/File:Café_con_leche.jpg (commons.wikimedia.org in Bing)

Tacos al Pastor — Author: AlejandroLinaresGarcia — CC BY-SA 4.0
https://commons.wikimedia.org/wiki/File:01_Tacos_al_Pastor.jpg

Pastrami grinder (2012) — Author: jeffreyw — CC BY 2.0
https://commons.wikimedia.org/wiki/File:Pastrami_grinder_(2012).jpg

Eataly Las Vegas (Feb 2019) — Author: Sarah Stierch — CC BY 4.0
https://commons.wikimedia.org/wiki/File:Eataly_Las_Vegas_-Feb_2019-_Sarah_Stierch_12.jpg

Zabo Fashion Boutique in Linz — Author: Uoaei1 — CC BY-SA 4.0
https://commons.wikimedia.org/wiki/File:Zabo_Fashion_Boutique_in_Linz.jpg

Arduino FTDI chip — Author: DustyDingo — Public Domain
https://commons.wikimedia.org/wiki/File:Arduino_ftdi_chip-1.jpg

Burlington Arcade — Author: Diliff — CC BY-SA 3.0
https://commons.wikimedia.org/wiki/File:Burlington_Arcade_2444.JPG

Hockey jerseys in a store — Author: GoToVan — CC BY 2.0
https://commons.wikimedia.org/wiki/File:Hockey_Jerseys_in_a_store.jpg

Nike Dunk — Author: Chabe01 — CC BY-SA 4.0
https://commons.wikimedia.org/wiki/File:Nike_dunk.jpg

PICKNWEIGHT – Vintage Kilo Store — Author: Uoaei1 — CC BY-SA 4.0
https://commons.wikimedia.org/wiki/File:PICKNWEIGHT_-_VINTAGE_KILO_STORE.jpg

Tent camping along the Sulayr trail — Author: Jebulon — CC0 (Public Domain)
https://commons.wikimedia.org/wiki/File:Tent_camping_along_the_Sulayr_trail_in_La_Taha,Sierra_Nevada_National_Park(DSCF5147).jpg

Ilmakuva1 (Aerial view of Autoliike Miettinen) — Author: Octaviars — CC BY-SA 4.0
https://commons.wikimedia.org/wiki/File:Ilmakuva1_(Large).png

Doctors Hospital from the Southwest — Author: WhisperToMe — CC BY-SA 3.0
https://commons.wikimedia.org/wiki/File:Doctors_Hospital_from_the_Southwest_1.jpg

Diamonds Thudufushi Beach & Water Villas (2017) — Author: Ibrahim Asad — CC BY-SA 4.0
https://commons.wikimedia.org/wiki/File:Diamonds_Thudufushi_Beach_and_Water_Villas,May_2017-08.jpg

Speedboat Near Newport Beach — Author: Don Ramey Logan — CC BY-SA 3.0
https://commons.wikimedia.org/wiki/File:Speedboat_Near_Newport_Beach.jpg

Wegner House — Galveston — Author: Jim Evans — CC BY-SA 4.0
https://commons.wikimedia.org/wiki/File:Wegner_House_--_Galveston.jpg

Plumbing and Gas Technician — Author: ThisisEngineering RAEng — CC BY-SA 4.0
https://commons.wikimedia.org/wiki/File:Plumbing_and_Gas_Technician.jpg

Dentist (gd569d444b) — Author: Darkmoon_Art — Pixabay License (Free for commercial use, no attribution required)
https://commons.wikimedia.org/wiki/File:Dentist-gd569d444b_1920.jpg

Computer repair in progress — Author: Marco Verch — CC BY 2.0
https://commons.wikimedia.org/wiki/File:Computer_repair_in_progress.jpg

Over $1,000,000 in USD $100 bill stacks — Author: Nick Youngson / Alpha Stock Images — CC BY-SA 3.0
https://commons.wikimedia.org/wiki/File:Over_$1,000,000_dollars_in_USD_$100_bill_stacks.png

Tutoring Center, Tulane University (2009) — Author: Tulane Public Relations — CC BY 2.0
https://commons.wikimedia.org/wiki/File:Tutoring_Center,_Tulane_University_2009.jpg

Bookshelf with ancient philosophers — Author: Elrond — CC BY-SA 4.0
https://commons.wikimedia.org/wiki/File:Part_of_a_bookshelf_containing_books_by_ancient_philosophers_(1.1).jpg

Peugeot 205 cabrio with open hood in auto repair shop — Author: Alf van Beem — CC0 (Public Domain)
https://commons.wikimedia.org/wiki/File:Peugeot_205_cabrio_with_open_hood_in_auto_repair_shop.jpg

Cycle Class at a Gym — Author: U.S. Air Force photo / Senior Airman Christopher Gross — Public Domain (U.S. Government)
https://commons.wikimedia.org/wiki/File:Cycle_Class_at_a_Gym.JPG

Computer lab cubicles - Author: Jarmoluk — Pixabay License (Free for commercial use, no attribution required)
https://commons.wikimedia.org/wiki/File:Computer_lab_cubicles.webp

Inside T.P. Smith’s Pub, Dublin - Author: Kenneth C. - CC BY-SA 4.0
https://commons.wikimedia.org/wiki/File:Inside_T.P._Smith's_Pub,_Dublin,_Ireland.jpg


# Captcha Image Credits:

“A beautiful landscape of nature.jpg” - Author: RyanPhotography — CC BY-SA 4.0
https://commons.wikimedia.org/wiki/File:A_beautiful_landscape_of_nature.jpg

"Blackbird-sunset-03.jpg" - Author: Jerry Segraves - (Public domain)
https://commons.wikimedia.org/wiki/File:Blackbird-sunset-03.jpg

"Viaduc Saillard.jpg" - Author: FrancoisFC — CC BY-SA 3.0
https://commons.wikimedia.org/wiki/File:Viaduc_Saillard.jpg

"Cat_November_2010-1a.jpg" - Author: Alvesgaspar - CC BY-SA 3.0
https://commons.wikimedia.org/wiki/File:Cat_November_2010-1a.jpg

"Rose Garden - NATO Vista Bridge 3 NBG LR.jpg" - Author: PumpkinSky - CC BY-SA 4.0
https://commons.wikimedia.org/wiki/File:Rose_Garden_-_NATO_Vista_Bridge_3_NBG_LR.jpg

"Cute dog.jpg" - Author: leisergu - CC BY-SA 2.0
https://commons.wikimedia.org/wiki/File:Cute_dog.jpg
