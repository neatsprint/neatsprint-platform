from neatsprint_lib.settings import ServiceSettings


class Settings(ServiceSettings):
    service_name: str = "__SERVICE__"
    api_prefix: str = "__SERVICE__"


settings = Settings()
