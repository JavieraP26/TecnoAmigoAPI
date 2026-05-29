from abc import ABC, abstractmethod


class SmsService(ABC):
    """Contrato para cualquier proveedor de SMS."""

    @abstractmethod
    async def send_verification_code(self, phone_number: str, code: str) -> None:
        """Envía el código OTP al número indicado."""
        raise NotImplementedError


class TwilioSmsService(SmsService):
    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        from twilio.rest import Client
        self._client = Client(account_sid, auth_token)
        self._from_number = from_number

    async def send_verification_code(self, phone_number: str, code: str) -> None:
        # Twilio SDK es síncrono; se ejecuta en un thread para no bloquear el event loop
        import asyncio
        await asyncio.to_thread(
            self._client.messages.create,
            body=f"Tu código TecnoAmigo es: {code}. Válido por 10 minutos.",
            from_=self._from_number,
            to=phone_number,
        )


def get_sms_service() -> SmsService:
    """Factory usada como dependencia FastAPI. Retorna la implementación configurada."""
    from app.config import settings

    return TwilioSmsService(
        account_sid=settings.twilio_account_sid,
        auth_token=settings.twilio_auth_token,
        from_number=settings.twilio_phone_number,
    )
