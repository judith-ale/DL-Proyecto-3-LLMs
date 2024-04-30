import mwclient
import wikitextparser
import re
from slugify import slugify
import uuid
import time
import random
import os

DATA_PATH = os.environ.get("DATA_PATH")
SITE_HOST = os.environ.get("SITE_HOST")
SITE_PATH = os.environ.get("SITE_PATH")

site = mwclient.Site(SITE_HOST, path=SITE_PATH)


for page in site.pages:
    text = page.text()
    text = wikitextparser.parse(text).plain_text()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'==Gallery==.*', '', text)

    if text.upper().startswith("#REDIRECT"):
        continue

    filename = slugify(f"{page.page_title}_{uuid.uuid4()}") + ".txt"

    file_path = os.path.join(DATA_PATH, filename)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(text)

    time.sleep(random.randint(0, 3))

