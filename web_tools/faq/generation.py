import openai
from openai import AsyncOpenAI

from typing import Dict, Optional
from openai import OpenAI

from web_tools.faq.prompts import DEFAULT_SYSTEM_PROMPT, DEFAULT_USER_PROMPT_TEMPLATE
from web_tools.faq.models import FAQSection


class FAQGenerator:
    def __init__(self, client: OpenAI, default_model: str = "gpt-4o-2024-08-06"):
        self.client = client
        self.default_model = default_model

    def generate_faq_section(
        self,
        topic: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        user_prompt: Optional[str] = None,
    ) -> Dict:
        selected_model = model or self.default_model
        system_message = system_prompt or DEFAULT_SYSTEM_PROMPT
        user_message = user_prompt or DEFAULT_USER_PROMPT_TEMPLATE.format(content=topic)

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ]

        completion = self.client.beta.chat.completions.parse(
            model=selected_model,
            messages=messages,
            tools=[
                openai.pydantic_function_tool(FAQSection),
            ],
        )

        return completion.choices[0].message.tool_calls[0].function.parsed_arguments


class AsyncFAQGenerator:
    def __init__(self, client: AsyncOpenAI, default_model: str = "gpt-4o-2024-08-06"):
        self.client = client
        self.default_model = default_model

    async def generate_faq_section(
        self,
        topic: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        user_prompt: Optional[str] = None,
    ) -> Dict:
        selected_model = model or self.default_model
        system_message = system_prompt or DEFAULT_SYSTEM_PROMPT
        user_message = user_prompt or DEFAULT_USER_PROMPT_TEMPLATE.format(content=topic)

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ]

        completion = await self.client.beta.chat.completions.parse(
            model=selected_model,
            messages=messages,
            tools=[
                openai.pydantic_function_tool(FAQSection),
            ],
        )

        return completion.choices[0].message.tool_calls[0].function.parsed_arguments
