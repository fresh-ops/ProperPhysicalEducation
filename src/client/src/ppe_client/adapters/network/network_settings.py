from pydantic.v1 import BaseSettings


class NetworkSettings(BaseSettings):
    server_host: str = "172.20.10.2"
    http_port: int = 8000
    ws_port: int = 8000

    class Config:
        env_file = ".env"

    @property
    def base_http_url(self) -> str:
        return f"http://{self.server_host}:{self.http_port}"

    @property
    def base_ws_url(self) -> str:
        return f"ws://{self.server_host}:{self.ws_port}"

    @property
    def exercises_url(self) -> str:
        return f"{self.base_http_url}/exercises"

    @property
    def start_url(self) -> str:
        return f"{self.base_http_url}/start"

    def analyze_url(self, session_id: str) -> str:
        return f"{self.base_ws_url}/analyze/{session_id}"
