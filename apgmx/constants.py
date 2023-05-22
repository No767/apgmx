import re
import os

REVISION_FILE = re.compile(r"(?P<kind>V|U)(?P<version>[0-9]+)__(?P<description>.+).sql")
POSTGRES_URL = os.getenv("DATABASE_URL_PG")