import base64
import json
import os
from typing import Dict, List, Union
from dotenv import find_dotenv, load_dotenv
from langfuse import Langfuse
from openai import AsyncAzureOpenAI, AzureOpenAI, AsyncOpenAI, OpenAI

status = load_dotenv(find_dotenv())
assert status, "Failed to load .env file"

# Constants for environment variable keys
API_TYPE = "API_TYPE"
API_KEY_ENV = "API_KEY"
API_BASE_ENV = "API_BASE_URL"
MODEL_ENV = "MODEL_NAME"

# Model constants
DEFAULT_TEMPERATURE = 0.0
DEFAULT_PRESENCE_PENALTY = 0.0
DEFAULT_FREQUENCY_PENALTY = 0.0


class Langfuse_Morph:
    def __call__(self, *args, **kwargs):
        return self

    def __getattr__(self, *args, **kwargs):
        return self


class LLMClient:
    """
    A client for interacting with the LLM model.
    """

    def __init__(
        self,
        temperature: float = DEFAULT_TEMPERATURE,
        presence_penalty: float = DEFAULT_PRESENCE_PENALTY,
        frequency_penalty: float = DEFAULT_FREQUENCY_PENALTY,
        langfuse_enable: bool = False,
        trace_id: Union[str, None] = None,
        trace_name: Union[str, None] = None,
        track_model_name: str = None,
    ) -> None:
        """
        Initialize the LLMClient instance.

        Args:
            temperature (float): Sampling temperature for the model.
            presence_penalty (float): Penalty for presence of certain tokens.
            frequency_penalty (float): Penalty for frequency of certain tokens.
            langfuse_enable (bool): Whether to enable Langfuse tracing.
            trace_id (Union[str, None]): ID for the trace in Langfuse.
            trace_name (Union[str, None]): Name for the trace in Langfuse.
            track_model_name (str): Name of the model to track in Langfuse.
        """
        self.temperature = temperature
        self.presence_penalty = presence_penalty
        self.frequency_penalty = frequency_penalty
        self.langfuse_enable = langfuse_enable
        self.track_model_name = track_model_name
        self.async_client, self.client = self._create_client()

        if self.langfuse_enable:
            self.langfuse_client = Langfuse()
            self.trace = self.langfuse_client.trace(
                id=trace_id, name=trace_name, metadata=self._prepare_metadata()
            )
        else:
            self.langfuse_client = Langfuse_Morph()
            self.trace = self.langfuse_client.trace(
                id=trace_id, name=trace_name, metadata=self._prepare_metadata()
            )

    def _create_client(self) -> tuple:
        """Create the LLM client.

        Returns:
            tuple: A tuple containing the async client and sync client.
        """
        if os.getenv(API_TYPE) == "azure":
            async_client = AsyncAzureOpenAI(
                api_key=os.getenv(API_KEY_ENV),
                azure_endpoint=os.getenv(API_BASE_ENV),
            )
            client = AzureOpenAI(
                api_key=os.getenv(API_KEY_ENV),
                azure_endpoint=os.getenv(API_BASE_ENV),
            )
        else:
            async_client = AsyncOpenAI(
                api_key=os.getenv(API_KEY_ENV),
                base_url=os.getenv(API_BASE_ENV),
            )
            client = OpenAI(
                api_key=os.getenv(API_KEY_ENV),
                base_url=os.getenv(API_BASE_ENV),
            )
        return async_client, client

    @staticmethod
    def _encode_image(img_path: str) -> str:
        """
        Encode an image file to a base64 string.

        Args:
            img_path (str): Path to the image file.

        Returns:
            str: Base64 encoded string of the image.
        """
        with open(img_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    @staticmethod
    def _is_base64_encoded(input_string: str) -> bool:
        """
        Check if a string is base64 encoded.

        Args:
            input_string (str): The input string to check.

        Returns:
            bool: Whether the string is base64 encoded (True or False).
        """
        try:
            decoded_bytes = base64.b64decode(input_string, validate=True)
            if base64.b64encode(decoded_bytes).decode("utf-8") == input_string:
                return True
            return False
        except (base64.binascii.Error, ValueError):
            return False

    def _format_image_message(self, image_path: str) -> Dict:
        """
        Format an image message for the API.

        Args:
            image_path (str): Path or URL to the image.

        Returns:
            Dict: Formatted image message.
        """
        if self._is_base64_encoded(image_path):
            url = f"data:image/jpeg;base64,{image_path}"
        elif "http" in image_path:
            url = image_path
        else:
            assert os.path.exists(image_path), f"Image {image_path} not found"
            url = f"data:image/jpeg;base64,{self._encode_image(image_path)}"
        return {
            "type": "image_url",
            "image_url": {"url": url},
        }

    def create_messages(
        self,
        input_message: Dict,
        system_message: str,
        human_message: str,
        image_path: Union[str, List[str]],
    ) -> List[Dict]:
        """
        Create a list of messages for the API.

        Args:
            input_message (Dict): Input message dictionary.
            system_message (str): Template for the system message.
            human_message (str): Template for the human message.
            image_path (Union[str, List[str]]): Path(s) to the image(s).

        Returns:
            List[Dict]: List of formatted messages.
        """
        system_message = system_message.format(**input_message)
        human_message = human_message.format(**input_message)

        if system_message:
            messages = [
                {"role": "system", "content": system_message},
            ]
        else:
            messages = []

        if image_path:
            content = [{"type": "text", "text": human_message}]
            if isinstance(image_path, str):
                content.append(self._format_image_message(image_path))
            elif isinstance(image_path, list):
                for img in image_path:
                    content.append(self._format_image_message(img))
            else:
                raise TypeError(
                    "image_path must be a string or a list of strings"
                )

            messages.append({"role": "user", "content": content})
        else:
            messages.append({"role": "user", "content": human_message})

        return messages

    def _prepare_metadata(self, **kwargs) -> Dict:
        """
        Prepare metadata for the API request.

        Args:
            **kwargs: Additional metadata parameters.

        Returns:
            Dict: Metadata dictionary.
        """
        return {
            "model": self.track_model_name,
            "response_format": {"type": kwargs.get("response_format", "text")},
            "temperature": kwargs.get("temperature", self.temperature),
            "presence_penalty": kwargs.get(
                "presence_penalty", self.presence_penalty
            ),
            "frequency_penalty": kwargs.get(
                "frequency_penalty", self.frequency_penalty
            ),
        }

    async def arun(
        self,
        prompt_name: Union[str, None] = None,
        input_message: Dict = {},
        system_message: str = "",
        human_message: str = "",
        image_path: Union[str, List[str]] = "",
        generation_name: Union[str, None] = None,
        **kwargs,
    ) -> str:
        """
        Asynchronously get a result from the LLM model.

        Args:
            prompt_name (Union[str, None]): Name of the prompt.
            input_message (Dict): Input message dictionary.
            system_message (str): Template for the system message.
            human_message (str): Template for the human message.
            image_path (Union[str, List[str]]): Path(s) to the image(s).
            generation_name (Union[str, None]): Name for the generation trace.
            **kwargs: Additional arguments for the API request.

        Returns:
            str: The model's response.
        """
        messages, prompt = self._get_prompt_and_messages(
            prompt_name,
            input_message,
            system_message,
            human_message,
            image_path,
        )

        metadata = self._prepare_metadata(**kwargs)
        gen_obj = self.trace.generation(
            name=generation_name,
            prompt=prompt,
            input=input_message,
            model=metadata["model"],
            metadata=metadata,
        )
        try:
            response_content = await self._get_response_content_async(
                messages, metadata, gen_obj
            )

            self._update_trace(gen_obj, response_content)
        except Exception as e:
            response_content = ""
            self._update_trace(
                gen_obj, response_content, status_message=str(e), level="ERROR"
            )
        return response_content

    def run(
        self,
        prompt_name: Union[str, None] = None,
        input_message: Dict = {},
        system_message: str = "",
        human_message: str = "",
        image_path: Union[str, List[str]] = "",
        generation_name: Union[str, None] = None,
        **kwargs,
    ) -> str:
        """
        Get a result from the LLM model.

        Args:
            prompt_name (Union[str, None]): Name of the prompt.
            input_message (Dict): Input message dictionary.
            system_message (str): Template for the system message.
            human_message (str): Template for the human message.
            image_path (Union[str, List[str]]): Path(s) to the image(s).
            generation_name (Union[str, None]): Name for the generation trace.
            **kwargs: Additional arguments for the API request.

        Returns:
            str: The model's response.
        """
        messages, prompt = self._get_prompt_and_messages(
            prompt_name,
            input_message,
            system_message,
            human_message,
            image_path,
        )
        metadata = self._prepare_metadata(**kwargs)
        gen_obj = self.trace.generation(
            name=generation_name,
            prompt=prompt,
            input=input_message,
            model=metadata["model"],
            metadata=metadata,
            status_message="Generating response...",
        )
        try:
            response_content = self._get_response_content(
                messages, metadata, gen_obj
            )
            self._update_trace(gen_obj, response_content)

        except Exception as e:
            response_content = ""
            self._update_trace(
                gen_obj, response_content, status_message=str(e), level="ERROR"
            )
        return response_content

    def _get_prompt_and_messages(
        self,
        prompt_name,
        input_message,
        system_message,
        human_message,
        image_path,
    ):
        """
        Get the prompt and messages for the API request.

        Args:
            prompt_name (str): Name of the prompt.
            input_message (Dict): Input message dictionary.
            system_message (str): Template for the system message.
            human_message (str): Template for the human message.
            image_path (str | List[str]): Path(s) to the image(s).

        Returns:
            Tuple: (messages, prompt)
        """
        if not prompt_name:
            prompt_name = "Unnamed"
            assert (
                human_message
            ), "Human message must be provided if prompt name is not provided."
            messages = self.create_messages(
                input_message, system_message, human_message, image_path
            )
            prompt = None
            input_message.update({"messages": messages})
        else:
            prompt_version_label = prompt_name.split(":")
            if len(prompt_version_label) == 2:
                prompt_name, version_label = prompt_version_label
            else:
                prompt_name = prompt_version_label[0]
                version_label = "production"

            try:
                version_label = {"version": int(version_label)}
            except ValueError:
                version_label = {"label": version_label}

            prompt = self.langfuse_client.get_prompt(
                prompt_name, **version_label
            )
            assert prompt is not None, "Prompt not found"

            messages = prompt.compile(**input_message)

            sys_message = (
                messages[0]["content"]
                if messages[0]["role"] == "system"
                else ""
            )
            usr_message = messages[-1]["content"]

            messages = self.create_messages(
                {},
                system_message=sys_message,
                human_message=usr_message,
                image_path=image_path,
            )

        return messages, prompt

    async def _get_response_content_async(self, messages, metadata, gen_obj):
        """
        Asynchronously get the response content from the API.

        Args:
            messages (List[Dict]): List of messages for the API.
            metadata (Dict): Metadata for the API request.

        Returns:
            str: The response content from the API.
        """
        metadata.pop("model", None)
        response = await self.async_client.chat.completions.create(
            messages=messages, model=self.getenv(MODEL_ENV), **metadata
        )
        response_content = response.choices[0].message.content
        response_format = metadata.get("response_format", {}).get(
            "type", "text"
        )
        if response_format == "json_object":
            span_obj = gen_obj.span(name="Json Parse", input=response_content)
            try:
                response_content = self.json_parse(response_content)
                span_obj.end(output=response_content)
            except Exception as e:
                span_obj.end(status_message=str(e), level="ERROR")
        return response_content

    def _get_response_content(self, messages, metadata, gen_obj):
        """
        Get the response content from the API.

        Args:
            messages (List[Dict]): List of messages for the API.
            metadata (Dict): Metadata for the API request.

        Returns:
            str: The response content from the API.
        """
        metadata.pop("model", None)
        response = self.client.chat.completions.create(
            messages=messages, model=os.getenv(MODEL_ENV), **metadata
        )
        response_content = response.choices[0].message.content
        response_format = metadata.get("response_format", {}).get(
            "type", "text"
        )
        if response_format == "json_object":
            span_obj = gen_obj.span(name="Json Parse", input=response_content)
            try:
                response_content = self.json_parse(response_content)
                span_obj.end(output=response_content)
            except Exception as e:
                span_obj.end(status_message=str(e), level="ERROR")
        return response_content

    def _update_trace(self, gen_obj, response_content, **kwargs):
        """
        Update the trace with the response content and usage.

        Args:
            gen_obj: The generation object.
            response_content (str): The response content from the API.
        """
        gen_obj.end(
            output=response_content, status_message="Success", **kwargs
        )
        self.trace.update(output=response_content, **kwargs)

    @staticmethod
    def json_parse(content: str, strict: bool = False, **kwargs) -> Dict:
        """
        Parse JSON content.

        Args:
            content (str): The JSON content to parse.
            strict (bool): Whether to use strict parsing.
            **kwargs: Additional arguments for JSON parsing.

        Returns:
            Dict: The parsed JSON content.
        """
        return json.loads(content.strip("```json\n"), strict=strict, **kwargs)

    def __repr__(self) -> str:
        """
        Return a string representation of the LLMClient instance.

        Returns:
            str: String representation of the instance.
        """
        return (
            f"LLMClient(temperature={self.temperature}, "
            f"presence_penalty={self.presence_penalty}, "
            f"frequency_penalty={self.frequency_penalty})"
        )

    def __str__(self) -> str:
        """
        Return a string description of the LLMClient instance.

        Returns:
            str: Description of the instance.
        """
        return (
            "LLMClient for calling the LLM model client with params: "
            f"temperature={self.temperature},"
            f"presence_penalty={self.presence_penalty}, "
            f"frequency_penalty={self.frequency_penalty}"
        )

    def __del__(self):
        self.langfuse_client.shutdown()
