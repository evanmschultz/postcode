import logging

from openai import OpenAI
from openai.types.chat.chat_completion_system_message_param import (
    ChatCompletionSystemMessageParam,
)
from openai.types.chat.chat_completion_user_message_param import (
    ChatCompletionUserMessageParam,
)
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from openai.types.chat.chat_completion import ChatCompletion

from ai_services.temp import code_example
from ai_services.prompt_creator import PromptCreator
import ai_services.summarizer_configs as configs
import ai_services.summarizer_context as context


class OpenAISummarizer:
    """
    A class for summarizing code snippets using the OpenAI API.

    Args:
        - client (OpenAI): The OpenAI client used for making API requests.

    Attributes:
        - client (OpenAI): The OpenAI client used for making API requests.
        - prompt_list (list[str]): A list of summary prompts.
        - default_prompt (str): The default summary prompt.

    Methods:
        summarize_code(code: str, configs: SummaryCompletionConfigs = SummaryCompletionConfigs()) -> str:
            Summarizes the provided code snippet using the OpenAI API.

    Examples:
        >>> client = OpenAI()
        >>> summarizer = Summarizer(client=client)
        >>> code_example = "print('Hello, world')"
        >>> summary = summarizer.summarize_code(code_example)
        >>> print(summary)
    """

    def __init__(
        self,
        client: OpenAI,
        # *, summary_prompt_list: list[str] = summary_prompt_list
    ) -> None:
        self.client: OpenAI = client
        # self.prompt_list: list[str] = summary_prompt_list
        # self.default_prompt: str = self.prompt_list[0]

    def _create_system_message(self, content: str) -> ChatCompletionSystemMessageParam:
        """Creates a system message for chat completion using OpenAi's ChatCompletionSystemMessageParam class."""
        return ChatCompletionSystemMessageParam(content=content, role="system")

    def _create_user_message(self, content: str) -> ChatCompletionUserMessageParam:
        """Creates a user message for chat completion using OpenAi's ChatCompletionUserMessageParam class."""
        return ChatCompletionUserMessageParam(content=content, role="user")

    def _create_messages_list(
        self,
        system_message: str,
        user_message: str,
    ) -> list[ChatCompletionMessageParam]:
        """
        Creates a list of messages for chat completion, including both system and user messages.

        Args:
            system_message (str): The system message content.
            user_message (str): The user message content.

        Returns:
            list[ChatCompletionMessageParam]: A list containing the system and user messages as OpenAI's
                ChatCompletionMessageParam classes.
        """

        return [
            self._create_system_message(system_message),
            self._create_user_message(user_message),
        ]

    def _create_prompt(
        self,
        code: str,
        children_summaries: str | None,
        dependency_summaries: str | None,
        import_details: str | None,
    ) -> str:
        prompt_creator: PromptCreator = PromptCreator()
        prompt: str | None = prompt_creator.create_prompt(
            code,
            children_summaries,
            dependency_summaries,
            import_details,
        )

        if prompt:
            return prompt
        else:
            raise Exception("Prompt creation failed.")

    def _get_summary(
        self,
        messages: list[ChatCompletionMessageParam],
        *,
        configs: configs.SummaryCompletionConfigs,
    ) -> context.OpenAIReturnContext | str:
        """
        Retrieves the summary from the OpenAI API based on the provided messages and configuration settings.

        Args:
            messages (list[ChatCompletionMessageParam]): A list of messages for chat completion.
            configs (SummaryCompletionConfigs): Configuration settings for the summarization completion.

        Returns:
            str | None: The summary generated by the OpenAI API, or None if no summary is found.
        """

        try:
            response: ChatCompletion = self.client.chat.completions.create(
                messages=messages,
                model=configs.model,
                max_tokens=configs.max_tokens,
                temperature=configs.temperature,
            )
            prompt_tokens: int = 0
            completion_tokens: int = 0
            summary: str | None = response.choices[0].message.content
            if response.usage:
                prompt_tokens = response.usage.prompt_tokens
                completion_tokens = response.usage.completion_tokens

            return context.OpenAIReturnContext(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                summary=summary,
            )

        except Exception as e:
            logging.error(e)
            return "Summarization failed."

    def summarize_code(
        self,
        code: str,
        *,
        builder_id: str,
        children_summaries: str | None,
        dependency_summaries: str | None,
        import_details: str | None,
        configs: configs.SummaryCompletionConfigs = configs.SummaryCompletionConfigs(),
    ) -> context.OpenAIReturnContext | str:
        """
        Summarizes the provided code snippet using the OpenAI API.

        Args:
            code (str): The code snippet to summarize.
            configs (SummaryCompletionConfigs, optional): Configuration settings for the summarization.
                Defaults to SummaryCompletionConfigs().

        Returns:
            str: The summary of the provided code snippet.

        Examples:
            >>> client = OpenAI()
            >>> summarizer = Summarizer(client=client)
            >>> code_example = "print('Hello, world')"
            >>> summary = summarizer.summarize_code(code_example)
            >>> print(summary)
        """

        logging.info(f"Summarizing code for builder: {builder_id}")
        prompt: str = self._create_prompt(
            code, children_summaries, dependency_summaries, import_details
        )
        messages: list[ChatCompletionMessageParam] = self._create_messages_list(
            system_message=configs.system_message, user_message=prompt
        )

        final_summary: str | None = None
        if summary_context := self._get_summary(messages, configs=configs):
            # print("Full Summary:\n", summary)
            if isinstance(summary_context, context.OpenAIReturnContext):
                if summary_context.summary:
                    final_summary = summary_context.summary.split("FINAL SUMMARY:")[-1]
                    logging.info(f"Full Summary:\n")
                    print(final_summary)
                    print(f"Prompt tokens: {summary_context.prompt_tokens}")
                    print(f"Completion tokens: {summary_context.completion_tokens}")

        return summary_context if summary_context else "Summary not found."

    def test_summarize_code(
        self,
        code: str,
        *,
        builder_id: str,
        children_summaries: str | None,
        dependency_summaries: str | None,
        import_details: str | None,
        configs: configs.SummaryCompletionConfigs = configs.SummaryCompletionConfigs(),
    ) -> context.OpenAIReturnContext | str:
        """
        Summarizes the provided code snippet using the OpenAI API.

        Args:
            code (str): The code snippet to summarize.
            configs (SummaryCompletionConfigs, optional): Configuration settings for the summarization.
                Defaults to SummaryCompletionConfigs().

        Returns:
            str: The summary of the provided code snippet.

        Examples:
            >>> client = OpenAI()
            >>> summarizer = Summarizer(client=client)
            >>> code_example = "print('Hello, world')"
            >>> summary = summarizer.summarize_code(code_example)
            >>> print(summary)
        """

        logging.info(f"Summarizing code for builder: {builder_id}")
        prompt: str = self._create_prompt(
            code, children_summaries, dependency_summaries, import_details
        )
        messages: list[ChatCompletionMessageParam] = self._create_messages_list(
            system_message=configs.system_message, user_message=prompt
        )

        summary: str = f"""Summary:\n
        {messages}\n 
        """
        summary_context = context.OpenAIReturnContext(
            summary=summary,
            prompt_tokens=1,
            completion_tokens=1,
        )
        logging.info(f"Full Summary:\n")
        print(summary)

        return summary_context


if __name__ == "__main__":
    client = OpenAI()
    summarizer = OpenAISummarizer(client=client)
    children_summaries = ""
    dependency_summaries = ""
    summary = summarizer.summarize_code(
        code_example,
        builder_id="test",
        children_summaries=children_summaries,
        dependency_summaries=dependency_summaries,
        import_details=None,
    )
    print(summary)
