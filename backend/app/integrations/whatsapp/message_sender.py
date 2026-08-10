from app.integrations.whatsapp.client import EvolutionAPIClient

class WhatsAppMessageSender:
    def __init__(self, evolution_client: EvolutionAPIClient):
        self.client = evolution_client
    
    async def send_response(
        self,
        instance_name: str,
        to_phone: str,
        text: str,
        buttons: list[str] | None = None,
    ) -> bool:
        """Send a response message. If buttons provided, send as button message."""
        try:
            if buttons:
                formatted_buttons = [{"buttonId": f"btn_{i}", "buttonText": {"displayText": btn}, "type": 1} for i, btn in enumerate(buttons)]
                await self.client.send_buttons(instance_name, to_phone, text, formatted_buttons)
            else:
                await self.client.send_text(instance_name, to_phone, text)
            return True
        except Exception as e:
            print(f"Error sending WhatsApp message: {e}")
            return False
            
    async def send_appointment_confirmation(
        self,
        instance_name: str,
        to_phone: str,
        service_name: str,
        staff_name: str,
        date: str,
        time: str,
    ) -> bool:
        """Send a formatted appointment confirmation message."""
        text = (
            f"✅ *Appointment Confirmed!*\n\n"
            f"Service: {service_name}\n"
            f"Professional: {staff_name}\n"
            f"Date: {date}\n"
            f"Time: {time}\n\n"
            f"Thank you for booking with us! We look forward to seeing you."
        )
        return await self.send_response(instance_name, to_phone, text)
