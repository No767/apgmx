import json
import os
from pathlib import Path
from typing import Any, Dict


class ConfigLoader:
    def __init__(self, filename: str = "apgmx_config.json"):
        self.filename: str = filename
        self.root: Path = Path(filename).parent
        self.load()

    def __repr__(self) -> str:
        return f"<ConfigLoader database_uri={self.database_uri}>"

    def ensure_config(self) -> None:
        if not self.root.joinpath(self.filename).exists():
            baseConf = {"database_uri": None}
            with open(self.root.joinpath(self.filename), "w") as f:
                json.dump(baseConf, f)

    def load_data(self) -> Dict[str, Any]:
        try:
            with open(self.filename, "r") as fp:
                return json.load(fp)
        except FileNotFoundError:
            return {"database_uri": None}

    def loadEnv(self) -> bool:
        dbEnv = os.getenv("DATABASE_URI")
        if dbEnv is not None:
            self.database_uri = dbEnv
            return True
        return False

    def load(self) -> None:
        self.ensure_config()
        data = self.load_data()

        loadFromEnv = self.loadEnv()

        if loadFromEnv is False:
            self.database_uri = data["database_uri"]

    def get_database_uri(self) -> str:
        return self.database_uri
