import json
import re
from sqlalchemy.orm import Session
from app.models import Message, AgentEvent
from app.services.llm_client import FakeLLMClient
from app.services.tools import get_order_status, create_support_ticket, search_faq

client = FakeLLMClient()

def get_last_order_id_from_history(db: Session, chat_id: int) -> int | None:
    """Извлекает последний order_id из истории сообщений пользователя в чате."""
    user_messages = db.query(Message).filter(
        Message.chat_id == chat_id,
        Message.role == "user"
    ).order_by(Message.created_at.desc()).all()
    for msg in user_messages:
        # Ищем число из 3 и более цифр – предполагаем номер заказа
        m = re.search(r'\b(\d{3,})\b', msg.content)
        if m:
            return int(m.group(1))
    return None

def process_message(db: Session, chat_id: int, content: str) -> str:
    # 1. Сохраняем сообщение пользователя
    user_msg = Message(chat_id=chat_id, role="user", content=content)
    db.add(user_msg)
    db.commit()

    # 2. Получаем контекст (последний order_id)
    last_order_id = get_last_order_id_from_history(db, chat_id)

    # 3. Получаем решение от LLM
    try:
        llm_resp = client.handle_message(content, last_order_id)
    except Exception as e:
        # Ошибка в логике клиента – отвечаем общим сообщением
        assistant_content = "Извините, произошла внутренняя ошибка."
        assistant_msg = Message(chat_id=chat_id, role="assistant", content=assistant_content)
        db.add(assistant_msg)
        db.commit()
        return assistant_content

    # 4. Обрабатываем tool call или прямой ответ
    if llm_resp.tool_name:
        tool_name = llm_resp.tool_name
        tool_args = llm_resp.tool_args or {}

        # Сохраняем событие tool_call
        event_call = AgentEvent(
            chat_id=chat_id,
            event_type="tool_call",
            tool_name=tool_name,
            payload=json.dumps(tool_args, ensure_ascii=False)
        )
        db.add(event_call)

        try:
            if tool_name == "get_order_status":
                order_id = tool_args["order_id"]
                tool_result = get_order_status(db, order_id)
            elif tool_name == "create_support_ticket":
                ticket_text = tool_args.get("text", content)
                order_id = tool_args.get("order_id")
                tool_result = create_support_ticket(db, chat_id, ticket_text, order_id)
            elif tool_name == "search_faq":
                tool_result = search_faq(db, tool_args.get("query", content))
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
        except Exception as e:
            # Инструмент упал – логируем ошибку и формируем ответ
            tool_result = {"error": str(e)}
            assistant_content = "Извините, не удалось выполнить запрошенное действие."
        else:
            # Формируем ответ ассистента на основе результата инструмента
            if tool_name == "get_order_status":
                if tool_result.get("found"):
                    assistant_content = f"Заказ {tool_result['order_id']} сейчас в статусе: {tool_result['status']}"
                else:
                    assistant_content = "Не нашел заказ с таким id."
            elif tool_name == "create_support_ticket":
                assistant_content = f"Создал обращение #{tool_result['id']}. Мы проверим проблему и вернемся с ответом."
            elif tool_name == "search_faq":
                if tool_result.get("found"):
                    assistant_content = f"{tool_result['answer']} Источник: {tool_result['source']}"
                else:
                    assistant_content = "Извините, я не нашел информацию в FAQ."
            else:
                assistant_content = "Неизвестная команда."

        # Сохраняем результат инструмента как сообщение роли tool
        tool_msg = Message(chat_id=chat_id, role="tool", content=json.dumps(tool_result, ensure_ascii=False))
        db.add(tool_msg)

        # Сохраняем событие tool_result
        event_result = AgentEvent(
            chat_id=chat_id,
            event_type="tool_result",
            tool_name=tool_name,
            payload=json.dumps(tool_result, ensure_ascii=False)
        )
        db.add(event_result)
    else:
        # Прямой ответ без вызова инструментов
        assistant_content = llm_resp.direct_response or "Не понял."

    # Сохраняем ответ ассистента
    assistant_msg = Message(chat_id=chat_id, role="assistant", content=assistant_content)
    db.add(assistant_msg)
    db.commit()

    return assistant_content