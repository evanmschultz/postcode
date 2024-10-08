import logging
from typing import Any, Mapping

from rich import print
from ollama import Client

from fenec.ai_services.summarizer.prompts.prompt_creator import (
    SummarizationPromptCreator,
)
from fenec.configs import (
    OllamaSummarizationConfigs,
    OpenAIReturnContext,
)
from fenec.types.ollama import OllamaMessage


class OllamaSummarizer:
    """
    A class for summarizing code snippets using the Ollama API.

    This class provides functionality to generate summaries of code snippets using Ollama's language models.
    It supports multi-pass summarization, allowing for more comprehensive and context-aware summaries.

    Args:
        - `configs` (OllamaConfigs, optional): Configuration settings for the Ollama summarizer.

    Attributes:
        - `client` (Ollama): The Ollama client instance.
        - `configs` (OllamaConfigs): Configuration settings for the summarizer.

    Methods:
        - `summarize_code`: Summarizes the provided code snippet using the Ollama API.
        - `test_summarize_code`: A method for testing the summarization functionality.

    Example:
        ```Python
        summarizer = OllamaSummarizer()
        summary = summarizer.summarize_code(
            code="def hello_world():\n    print('Hello, world!')",
            model_id="function_1",
            children_summaries="No child functions.",
            dependency_summaries="No dependencies.",
            import_details="No imports.",
            parent_summary="Module containing greeting functions.",
            pass_number=1
        )
        print(summary.summary if summary else "Summarization failed")
        ```
    """

    def __init__(
        self,
        configs: OllamaSummarizationConfigs = OllamaSummarizationConfigs(),
    ) -> None:
        self.configs: OllamaSummarizationConfigs = configs
        self.client: Client = Client()

    def _create_system_message(self, content: str) -> OllamaMessage:
        """Creates a system message for chat completion using Ollama's Message TypedDict class."""
        return OllamaMessage(content=content, role="system")

    def _create_user_message(self, content: str) -> OllamaMessage:
        """Creates a user message for chat completion using Ollama's Message TypedDict class."""
        return OllamaMessage(content=content, role="user")

    def _create_messages_list(
        self,
        system_message: str,
        user_message: str,
    ) -> list[OllamaMessage]:
        """
        Creates a list of messages for chat completion, including both system and user messages.

        Args:
            - system_message (str): The system message content.
            - user_message (str): The user message content.

        Returns:
            - list[ChatCompletionMessageParam]: A list containing the system and user messages as OpenAI's
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
        parent_summary: str | None,
        pass_number: int,
        previous_summary: str | None,
    ) -> str:
        """
        Creates a prompt for code summarization.

        Args:
            - `code` (str): The code to summarize.
            - `children_summaries` (str | None): Summaries of child elements.
            - `dependency_summaries` (str | None): Summaries of dependencies.
            - `import_details` (str | None): Details of imports.
            - `parent_summary` (str | None): Summary of the parent element.
            - `pass_number` (int): The current pass number in multi-pass summarization.
            - `previous_summary` (str | None): The summary from the previous pass.

        Returns:
            - `str`: The created prompt.

        Raises:
            - `Exception`: If prompt creation fails.
        """
        prompt_creator: SummarizationPromptCreator = SummarizationPromptCreator()
        prompt: str | None = prompt_creator.create_prompt(
            code,
            children_summaries,
            dependency_summaries,
            import_details,
            parent_summary,
            pass_number,
            previous_summary,
        )

        if prompt:
            # print(f"[blue]Prompt:[/blue] {prompt}")
            return prompt
        else:
            raise Exception("Prompt creation failed.")

    def _get_summary(
        self,
        messages: list[OllamaMessage],
    ) -> str | None:
        """
        Retrieves the summary from the OpenAI API based on the provided messages and configuration settings.

        Args:
            - messages (list[ChatCompletionMessageParam]): A list of messages for chat completion.

        Returns:
            str | None: The summary generated by the OpenAI API, or None if no summary is found.
        """

        try:
            response: Mapping[str, Any] = self.client.chat(
                model=self.configs.model,
                messages=messages,
                format="json",
            )
            print(f"[green]Response:[/green] {response}")
            message_dict: dict | None = response.get("message")
            if message_dict:
                return message_dict.get("content")
            return None

        except Exception as e:
            logging.error(e)
            return None

    def summarize_code(
        self,
        code: str,
        *,
        model_id: str,
        children_summaries: str | None,
        dependency_summaries: str | None,
        import_details: str | None,
        parent_summary: str | None = None,
        pass_number: int = 1,
        previous_summary: str | None = None,
    ) -> str | None:
        """
        Summarizes the provided code snippet using the OpenAI API.

        This method generates a summary of the given code, taking into account various contextual
        information such as children summaries, dependencies, imports, and parent summaries.
        It supports multi-pass summarization, allowing for refinement of summaries over multiple passes.

        Args:
            - `code` (str): The code snippet to summarize.
            - `model_id` (str): The identifier of the model being summarized.
            - `children_summaries` (str | None): Summaries of child elements, if any.
            - `dependency_summaries` (str | None): Summaries of dependencies, if any.
            - `import_details` (str | None): Details of imports used in the code.
            - `parent_summary` (str | None): Summary of the parent element, if applicable.
            - `pass_number` (int): The current pass number in multi-pass summarization. Default is 1.

        Returns:
            - `str | None`: A context object containing the summary and token usage information,
                                          or None if summarization fails.

        Example:
            ```Python
            summarizer = OpenAISummarizer()
            summary_context = summarizer.summarize_code(
                code="def greet(name):\n    return f'Hello, {name}!'",
                model_id="function_greet",
                children_summaries=None,
                dependency_summaries=None,
                import_details=None,
                parent_summary="Module with greeting functions",
                pass_number=2
            )
            if summary_context:
                print(f"Summary: {summary_context.summary}")
                print(f"Tokens used: {summary_context.prompt_tokens + summary_context.completion_tokens}")
            ```
        """

        logging.info(
            f"([blue]Pass {pass_number}[/blue]) - [green]Summarizing code for model:[/green] {model_id}"
        )
        prompt: str = self._create_prompt(
            code,
            children_summaries,
            dependency_summaries,
            import_details,
            parent_summary,
            pass_number,
            previous_summary,
        )
        messages: list[OllamaMessage] = self._create_messages_list(
            system_message=self.configs.system_message, user_message=prompt
        )

        summary: str | None = self._get_summary(messages)
        return summary

    def test_summarize_code(
        self,
        code: str,
        *,
        model_id: str,
        children_summaries: str | None,
        dependency_summaries: str | None,
        import_details: str | None,
        parent_summary: str | None = None,
        pass_number: int = 1,
    ) -> OpenAIReturnContext | None:
        """
        A method for testing the summarize_code functionality without making API calls.

        This method mimics the behavior of summarize_code but returns a predefined summary instead of
        making an actual API call. It's useful for testing the summarization pipeline without incurring
        API costs or when you want to test the surrounding logic.

        Args:
            - `code` (str): The code snippet to summarize (not used in the test method).
            - `model_id` (str): The identifier of the model being summarized.
            - `children_summaries` (str | None): Summaries of child elements, if any.
            - `dependency_summaries` (str | None): Summaries of dependencies, if any.
            - `import_details` (str | None): Details of imports used in the code.
            - `parent_summary` (str | None): Summary of the parent element, if applicable.
            - `pass_number` (int): The current pass number in multi-pass summarization. Default is 1.

        Returns:
            - OpenAIReturnContext | None: A context object containing a test summary and token usage information.

        Example:
            ```Python
            summarizer = OpenAISummarizer()
            test_summary = summarizer.test_summarize_code(
                code="print('Hello, World!')",
                model_id="test_function",
                children_summaries=None,
                dependency_summaries=None,
                import_details=None,
                parent_summary="Test Module",
                pass_number=1
            )
            print(test_summary.summary if test_summary else "Test summarization failed")
            ```
        """

        summary = f"""\nTest Summary for {model_id}:\n
        Pass Number: {pass_number}
        Parent Summary: {parent_summary}
        Children Summaries: {children_summaries}
        Dependency Summaries: {dependency_summaries}
        Import Details: {import_details}
        """
        summary_context = OpenAIReturnContext(
            summary=summary,
            prompt_tokens=1,
            completion_tokens=1,
        )

        return summary_context
