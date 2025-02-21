from uuid6 import uuid7
from dataclasses import dataclass


@dataclass
class LLMConfig:
    """
    A configuration class for language model settings.

    Attributes:
        temperature (float): The temperature setting for the language model,
        which controls the randomness of the output.
        langfuse_enable (bool): A flag to enable or disable LangFuse
                                integration.
        trace_id (str): A unique identifier for tracing purposes
        trace_name (str): The name assigned to the trace.
        track_model_name (str): The name of the model being tracked.
    """

    temperature: float = 0.0
    langfuse_enable: bool = True
    trace_id: str = str(uuid7())
    trace_name: str = "Air Q&A"
    track_model_name: str = "gpt4o"  # llama-3.3-70b-versatile
