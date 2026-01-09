from typing import TypedDict, List, Annotated
from langchain_core import BaseMessage
import operator

class TutorState(TypedDict):
    question: str
    chat_history: Annotated[List[BaseMessage], operator.add]
    retrieved_docs: List
    answer: str
    user_feedback: str

