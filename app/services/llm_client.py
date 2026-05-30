import re
from dataclasses import dataclass
from typing import Optional

@dataclass
class FakeLLMResponse:
    tool_name: Optional[str] = None
    tool_args: Optional[dict] = None
    direct_response: Optional[str] = None

class FakeLLMClient:
    def handle_message(self, content: str, last_order_id: Optional[int] = None) -> FakeLLMResponse:
        # 1. Явный запрос статуса с номером заказа
        m = re.search(r'статус заказа\s*(\d+)', content, re.IGNORECASE)
        if m:
            return FakeLLMResponse(tool_name="get_order_status", tool_args={"order_id": int(m.group(1))})

        # 2. Проблема / жалоба (до проверки общих слов "заказ")
        if re.search(r'проблема|не пришел|сломался|жалоба', content, re.IGNORECASE):
            order_id = None
            m = re.search(r'заказ[а-я]*\s*(\d+)', content, re.IGNORECASE)
            if m:
                order_id = int(m.group(1))
            return FakeLLMResponse(tool_name="create_support_ticket",
                                   tool_args={"text": content, "order_id": order_id})

        # 3. FAQ (возврат, доставка, оплата, вернуть, обмен)
        if re.search(r'доставка|возврат|оплата|вернуть|обмен', content, re.IGNORECASE):
            return FakeLLMResponse(tool_name="search_faq", tool_args={"query": content})

        # 4. Follow‑up / уточнение по заказу (если есть контекст)
        if last_order_id is not None and re.search(r'когда|создан|статус|какой|что с', content, re.IGNORECASE):
            return FakeLLMResponse(tool_name="get_order_status", tool_args={"order_id": last_order_id})

        # 5. Общий запрос о заказе без номера и без контекста → просим уточнить
        if re.search(r'статус заказа|заказ\b', content, re.IGNORECASE):
            return FakeLLMResponse(direct_response="Пожалуйста, укажите номер заказа.")

        # 6. Обычное сообщение
        return FakeLLMResponse(direct_response=f"Echo: {content}")