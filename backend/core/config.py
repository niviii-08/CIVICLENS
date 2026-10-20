import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Config:
    def __init__(self):
        self.APP_NAME: str = os.getenv("APP_NAME", "CivicLens TN")
        self.ENV: str = os.getenv("ENV", "development").lower()
        self.DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t", "yes")

        self.SECRET_KEY: str = os.getenv("SECRET_KEY", "")
        self.REVIEWER_API_KEY: str = os.getenv("REVIEWER_API_KEY", "")

        self.API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
        self.API_PORT: int = int(os.getenv("API_PORT", "5000"))
        self.FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
        self.ALLOWED_ORIGINS: list[str] = [
            origin.strip()
            for origin in os.getenv(
                "ALLOWED_ORIGINS",
                f"{self.FRONTEND_URL},http://localhost:3000,http://127.0.0.1:3000"
            ).split(",")
            if origin.strip()
        ]
        self.MAX_CONTENT_LENGTH: int = int(os.getenv("MAX_CONTENT_LENGTH", str(16 * 1024 * 1024)))

        self.DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/data/processed/civiclens.db")

        self.DATA_DIR: Path = Path(os.getenv("DATA_DIR", BASE_DIR / "data"))
        self.RAW_DATA_DIR: Path = Path(os.getenv("RAW_DATA_DIR", self.DATA_DIR / "raw"))
        self.PROCESSED_DATA_DIR: Path = Path(os.getenv("PROCESSED_DATA_DIR", self.DATA_DIR / "processed"))
        self.MODEL_DIR: Path = Path(os.getenv("MODEL_DIR", BASE_DIR / "ml" / "models"))

        self.LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

        self.X_CONSUMER_KEY: str = os.getenv("X_CONSUMER_KEY", "")
        self.X_CONSUMER_SECRET: str = os.getenv("X_CONSUMER_SECRET", "")
        self.X_BEARER_TOKEN: str = os.getenv("X_BEARER_TOKEN", "")

        self.YOUTUBE_API_KEY: str = os.getenv("YOUTUBE_API_KEY", "")

    def validate(self) -> None:
        """
        Validates critical configuration at startup.
        Produces clear, safe error diagnostics without leaking secret values.
        """
        errors: list[str] = []

        if self.ENV == "production":
            insecure_keys = {"", "change-me", "dev-secret", "secret", "insecure-key", "default"}
            if not self.SECRET_KEY or self.SECRET_KEY.lower() in insecure_keys:
                errors.append("SECRET_KEY must be configured with a strong, non-default string when ENV=production.")

            if self.DEBUG:
                errors.append("DEBUG mode must not be enabled when ENV=production.")

            if not self.DATABASE_URL:
                errors.append("DATABASE_URL must be specified.")

            if not self.REVIEWER_API_KEY or self.REVIEWER_API_KEY.lower() in insecure_keys:
                errors.append("REVIEWER_API_KEY must be configured with a non-default string when ENV=production.")

        if self.API_PORT < 1 or self.API_PORT > 65535:
            errors.append(f"API_PORT must be a valid port number between 1 and 65535, received {self.API_PORT}.")

        if errors:
            diagnostic_msg = "Application configuration validation failed at startup:\n  - " + "\n  - ".join(errors)
            raise ValueError(diagnostic_msg)

    def __repr__(self) -> str:
        """Safe string representation that masks secret values."""
        sensitive_fields = {
            "SECRET_KEY", "REVIEWER_API_KEY", "X_CONSUMER_SECRET",
            "X_BEARER_TOKEN", "YOUTUBE_API_KEY"
        }
        safe_dict = {}
        for k, v in self.__dict__.items():
            if k in sensitive_fields:
                safe_dict[k] = "***REDACTED***" if v else ""
            else:
                safe_dict[k] = v
        return f"<Config {safe_dict}>"

config = Config()
