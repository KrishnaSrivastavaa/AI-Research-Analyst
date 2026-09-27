from openai import OpenAI
from typing import List

async def get_chat_response(query: str, history: List[dict], context: List[dict]):

    client = OpenAI()


    SYSTEM_PROMPT = """You are a research analyst, for each response you have to anayse the chunks given to you and respond only on the basis of that." \
    You don't have to take any external reference to answer any question. If you don't have the information in the chunks, you have to say 'I don't know'.
    You are also allowed to reply to the greeting messages, and should respond carefully and respectfully."""

    context_text = "\n\n".join(
        f"""
        SOURCE {i+1}
        Document ID: {chunk["document_id"]}
        Pages: {chunk["page_start"]}-{chunk["page_end"]}

        {chunk["text"]}
        """
        for i, chunk in enumerate(context)
    )
    
    input_messages = [
        *history,
        {
            "role": "user",
            "content": f"""
            Use the following retrieved sources to answer my question.

            {context_text}

            Question:
            {query}
            """
        }
    ]


    response = client.responses.create(
        model="gpt-4o-mini",
        instructions=SYSTEM_PROMPT,
        input=input_messages
        
    )

    return response.output_text
