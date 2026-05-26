# from langchain_groq import ChatGroq
# from dotenv import load_dotenv
# import os

# load_dotenv()


# MODEL_PRIORITY = [

#     "qwen/qwen3-32b",

#     "llama-3.3-70b-versatile",

#     "deepseek-r1-distill-llama-70b"

# ]


# class LLMManager:

#     """
#     Groq model manager

#     Features:

#     - automatic fallback
#     - rate limit handling
#     - streaming support
#     - agent support
#     - tool support
#     - structured output support
#     """

#     def __init__(

#         self,

#         max_tokens=500,

#         temperature=0,

#         streaming=True

#     ):

#         self.max_tokens = max_tokens

#         self.temperature = temperature

#         self.streaming = streaming

#         self.current = 0

#         self.model = self._create_model(

#             MODEL_PRIORITY[
#                 self.current
#             ]

#         )

#     def _create_model(
#         self,
#         model_name
#     ):

#         kwargs = {

#             "model":
#             model_name,

#             "api_key":
#             os.getenv(
#                 "GROQ_API_KEY"
#             ),

#             "max_tokens":
#             self.max_tokens,

#             "temperature":
#             self.temperature,

#             "streaming":
#             self.streaming

#         }

#         # qwen only

#         if "qwen" in model_name.lower():

#             kwargs[
#                 "reasoning_format"
#             ] = "hidden"

#         print(
#             f"Loading model: {model_name}"
#         )

#         return ChatGroq(
#             **kwargs
#         )

#     def switch_model(
#         self
#     ):

#         self.current += 1

#         if self.current >= len(
#             MODEL_PRIORITY
#         ):

#             raise Exception(
#                 "All models exhausted"
#             )

#         next_model = MODEL_PRIORITY[
#             self.current
#         ]

#         print(
#             f"Switching -> {next_model}"
#         )

#         self.model = self._create_model(
#             next_model
#         )

#     def _should_switch(
#         self,
#         error
#     ):

#         text = str(
#             error
#         ).lower()

#         triggers = [

#             "429",

#             "rate_limit",

#             "tokens per day",

#             "tokens per minute",

#             "request too large",

#             "413"

#         ]

#         return any(

#             t in text

#             for t in triggers

#         )

#     def invoke(

#         self,

#         *args,

#         **kwargs

#     ):

#         last_error = None

#         while True:

#             try:

#                 return self.model.invoke(

#                     *args,

#                     **kwargs

#                 )

#             except Exception as e:

#                 last_error = e

#                 print(
#                     e
#                 )

#                 if self._should_switch(
#                     e
#                 ):

#                     self.switch_model()

#                     continue

#                 raise e

#         raise last_error

#     def stream(

#         self,

#         *args,

#         **kwargs

#     ):

#         last_error = None

#         while True:

#             try:

#                 yield from self.model.stream(

#                     *args,

#                     **kwargs

#                 )

#                 return

#             except Exception as e:

#                 last_error = e

#                 print(
#                     e
#                 )

#                 if self._should_switch(
#                     e
#                 ):

#                     self.switch_model()

#                     continue

#                 raise e

#         raise last_error

#     def bind(

#         self,

#         *args,

#         **kwargs

#     ):

#         return self.model.bind(

#             *args,

#             **kwargs

#         )

#     def bind_tools(

#         self,

#         *args,

#         **kwargs

#     ):

#         return self.model.bind_tools(

#             *args,

#             **kwargs

#         )

#     def with_structured_output(

#         self,

#         *args,

#         **kwargs

#     ):

#         return self.model.with_structured_output(

#             *args,

#             **kwargs

#         )

#     def reset_model(
#         self
#     ):

#         self.current = 0

#         self.model = self._create_model(

#             MODEL_PRIORITY[0]

#         )

#     def __getattr__(
#         self,
#         name
#     ):

#         return getattr(
#             self.model,
#             name
#         )
    
# llm = LLMManager()

from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()


MODEL_PRIORITY = [

    "qwen/qwen3-32b",

    "llama-3.3-70b-versatile",

    "llama-3.1-8b-instant"

]


class BoundLLM:

    """
    Dynamic wrapper.

    Always uses latest active model.
    """

    def __init__(

        self,

        manager,

        mode,

        *args,

        **kwargs

    ):

        self.manager = manager

        self.mode = mode

        self.args = args

        self.kwargs = kwargs

    def _build(self):

        fn = getattr(

            self.manager.model,

            self.mode

        )

        return fn(

            *self.args,

            **self.kwargs

        )

    def invoke(

        self,

        *args,

        **kwargs

    ):

        obj = self._build()

        return obj.invoke(

            *args,

            **kwargs

        )

    def stream(

        self,

        *args,

        **kwargs

    ):

        obj = self._build()

        yield from obj.stream(

            *args,

            **kwargs

        )

    def __getattr__(

        self,

        name

    ):

        obj = self._build()

        return getattr(

            obj,

            name

        )


class LLMManager:

    def __init__(

        self,

        max_tokens=500,

        temperature=0,

        streaming=True

    ):

        self.max_tokens = max_tokens

        self.temperature = temperature

        self.streaming = streaming

        self.current = 0

        self.model = self._create_model(

            MODEL_PRIORITY[0]

        )

    def _create_model(

        self,

        model_name

    ):

        kwargs = {

            "model":
            model_name,

            "api_key":
            os.getenv(
                "GROQ_API_KEY"
            ),

            "max_tokens":
            self.max_tokens,

            "temperature":
            self.temperature,

            "streaming":
            self.streaming

        }

        if "qwen" in model_name.lower():

            kwargs[
                "reasoning_format"
            ] = "hidden"

        print(
            f"Loading model: {model_name}"
        )

        return ChatGroq(
            **kwargs
        )

    def switch_model(
        self
    ):

        while True:

            self.current += 1

            if self.current >= len(
                MODEL_PRIORITY
            ):

                raise Exception(
                    "All fallback models exhausted"
                )

            next_model = MODEL_PRIORITY[
                self.current
            ]

            print(
                f"Switching -> {next_model}"
            )

            try:

                self.model = self._create_model(
                    next_model
                )

                return

            except Exception as e:

                print(
                    "Model load failed:",
                    e
                )

                continue
    def _should_switch(
        self,
        error
    ):

        text = str(
            error
        ).lower()

        triggers = [

            "429",

            "rate_limit",

            "tokens per day",

            "tokens per minute",

            "413",

            "request too large",

            "model_decommissioned",

            "no longer supported",

            "invalid_request_error"

        ]

        return any(

            x in text

            for x in triggers

        )

    def invoke(

        self,

        *args,

        **kwargs

    ):

        while True:

            try:

                return self.model.invoke(

                    *args,

                    **kwargs

                )

            except Exception as e:

                print(e)

                if self._should_switch(
                    e
                ):

                    self.switch_model()

                    continue

                raise

    def stream(

        self,

        *args,

        **kwargs

    ):

        while True:

            try:

                yield from self.model.stream(

                    *args,

                    **kwargs

                )

                return

            except Exception as e:

                print(e)

                if self._should_switch(
                    e
                ):

                    self.switch_model()

                    continue

                raise

    # IMPORTANT

    def bind(

        self,

        *args,

        **kwargs

    ):

        return BoundLLM(

            self,

            "bind",

            *args,

            **kwargs

        )

    def bind_tools(

        self,

        *args,

        **kwargs

    ):

        return BoundLLM(

            self,

            "bind_tools",

            *args,

            **kwargs

        )

    def with_structured_output(

        self,

        *args,

        **kwargs

    ):

        return BoundLLM(

            self,

            "with_structured_output",

            *args,

            **kwargs

        )

    def reset_model(
        self
    ):

        self.current = 0

        self.model = self._create_model(

            MODEL_PRIORITY[0]

        )

    def __getattr__(

        self,

        name

    ):

        return getattr(

            self.model,

            name

        )


# GLOBAL INSTANCE

llm = LLMManager()