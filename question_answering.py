from llama_index.core import VectorStoreIndex
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core import ChatPromptTemplate
from localisation import Localisation

class QAEngine:
    def __init__(self, data_index: VectorStoreIndex, locale: Localisation, send_k_most_likely_variants) -> None:
        chat_text_qa_msgs = [
            ChatMessage(
                role=MessageRole.SYSTEM,
                content=locale.getStr("chatgpt_qa_system_prompt"),
            ),
            ChatMessage(
                role=MessageRole.USER,
                content=locale.getStr("chatgpt_qa_user_prompt")
            ),
        ]
        text_qa_template = ChatPromptTemplate(chat_text_qa_msgs)

        self.query_engine = data_index.as_query_engine(
            text_qa_template=text_qa_template,
            similarity_top_k=send_k_most_likely_variants)
    
    def ask(self, question: str) -> str:
        if question is None or question is "":
            return ""
        response = str(self.query_engine.query(question))
        return response
