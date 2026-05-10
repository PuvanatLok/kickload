from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Environment
    env: str = "dev"

    # Database
    database_url: str

    # Pub/Sub
    pubsub_project_id: str = "kickload-local"
    pubsub_topic: str = "kickload-app-events-dev"
    pubsub_emulator_host: str | None = None
    # When PUBSUB_EMULATOR_HOST is set, the GCP client library automatically
    # routes to the local emulator instead of real GCP.
    # When it is unset (production), it routes to real GCP Pub/Sub.
    # Zero code changes needed — the SDK handles this transparently.

    # Auth
    supabase_url: str = ""
    supabase_service_key: str = ""

    # GCP
    gcp_project_id: str = ""
    gcs_bucket: str = ""

    @property
    def is_production(self) -> bool:
        return self.env == "prod"


settings = Settings()
