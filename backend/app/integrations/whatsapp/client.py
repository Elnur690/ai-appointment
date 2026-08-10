import httpx

class EvolutionAPIClient:
    """Async HTTP client for Evolution API."""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self._client: httpx.AsyncClient | None = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={'apikey': self.api_key},
                timeout=30.0,
            )
        return self._client
    
    async def send_text(self, instance_name: str, to_number: str, text: str) -> dict:
        client = await self._get_client()
        response = await client.post(
            f"/message/sendText/{instance_name}",
            json={
                "number": to_number,
                "text": text
            }
        )
        response.raise_for_status()
        return response.json()
        
    async def send_buttons(self, instance_name: str, to_number: str, text: str, buttons: list[dict]) -> dict:
        client = await self._get_client()
        response = await client.post(
            f"/message/sendButtons/{instance_name}",
            json={
                "number": to_number,
                "text": text,
                "buttons": buttons
            }
        )
        response.raise_for_status()
        return response.json()
        
    async def get_instance_status(self, instance_name: str) -> dict:
        client = await self._get_client()
        response = await client.get(f"/instance/connectionState/{instance_name}")
        response.raise_for_status()
        return response.json()
        
    async def create_instance(self, instance_name: str, webhook_url: str | None = None) -> dict:
        client = await self._get_client()
        data = {
            "instanceName": instance_name,
            "token": instance_name,
            "qrcode": True
        }
        if webhook_url:
            data["webhook"] = webhook_url
            
        response = await client.post("/instance/create", json=data)
        response.raise_for_status()
        return response.json()
        
    async def connect_instance(self, instance_name: str) -> dict:
        client = await self._get_client()
        response = await client.get(f"/instance/connect/{instance_name}")
        response.raise_for_status()
        return response.json()
        
    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()
