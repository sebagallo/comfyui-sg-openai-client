import torch
import json
from .utils import image_to_data_uri
from comfy_api.latest import IO

class OpenAIChatCompletionNode(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="OpenAIChatCompletion",
            display_name="OpenAI Chat Completion",
            category="OpenAI",
            inputs=[
                IO.Custom("OPENAI_CLIENT").Input("client", tooltip="The OpenAI client to use for the request."),
                IO.String.Input("system_prompt", multiline=True, tooltip="The system prompt to set the context for the model."),
                IO.String.Input("user_prompt", multiline=True, tooltip="The user prompt to generate a response for."),
                IO.String.Input("model", extra_dict={"widgetType": "COMBO", "options": []}, tooltip="The model used to generate the response."),
                IO.Image.Input(
                    "images",
                    tooltip="Optional image(s) to use as context for the model. To include multiple images, you can use the Batch Images node.",
                    optional=True
                ),
                IO.Float.Input("temperature", default=1.0, min=0.0, max=10.0, step=0.01, optional=True, tooltip="Controls the randomness of the output. Higher values (e.g., 1.2) make the output more random, while lower values (e.g., 0.2) make it more focused and deterministic."),
                IO.Float.Input("top_p", default=1.0, min=0.0, max=1.0, step=0.01, optional=True, tooltip="An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass."),
                IO.Int.Input("top_k", default=None, min=0, max=100, optional=True, tooltip="A sampling technique that limits the number of most likely next tokens to k. (Unofficial parameter, may be ignored by official OpenAI API)"),
                IO.Float.Input("min_p", default=None, min=0.0, max=1.0, step=0.01, optional=True, tooltip="A sampling technique that ensures only tokens with a probability greater than min_p times the probability of the most likely token are considered. (Unofficial parameter, may be ignored by official OpenAI API)"),
                IO.Int.Input("max_tokens", default=1000, min=1, max=32768, optional=True, tooltip="The maximum number of tokens to generate in the completion."),
                IO.Float.Input("frequency_penalty", default=0.0, min=-2.0, max=2.0, step=0.01, optional=True, tooltip="Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim."),
                IO.Float.Input("presence_penalty", default=0.0, min=-2.0, max=2.0, step=0.01, optional=True, tooltip="Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics."),
                IO.Int.Input("seed", default=-1, min=-1, max=0xffffffffffffffff, optional=True, extra_dict={"control_after_generate": True}, tooltip="If specified, our system will make a best effort to sample deterministically. Use -1 for random (default behavior)."),
                IO.String.Input("extra_parameters", default="", multiline=True, optional=True, tooltip="Custom JSON string for any additional parameters to send to the API (e.g. {'logit_bias': {...}})."),
            ],
            outputs=[
                IO.String.Output(),
            ],
        )

    @classmethod
    async def execute(
        cls,
        client,
        system_prompt: str,
        user_prompt: str,
        model: str,
        images: torch.Tensor | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        top_k: int | None = None,
        min_p: float | None = None,
        max_tokens: int | None = None,
        frequency_penalty: float | None = None,
        presence_penalty: float | None = None,
        seed: int | None = None,
        extra_parameters: str = ""
    ) -> IO.NodeOutput:
        openai_client = client["client"]

        # Prepare user message content
        user_content = [{"type": "text", "text": user_prompt}]

        if images is not None:
            B = images.shape[0]
            for i in range(B):
                img_tensor = images[i]  # (H, W, C)
                data_uri = image_to_data_uri(img_tensor)
                user_content.append({
                    "type": "image_url",
                    "image_url": {"url": data_uri}
                })

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]

        # Use kwargs for optional parameters to avoid sending defaults if not provided
        api_kwargs = {
            "model": model,
            "messages": messages,
        }
        if temperature is not None: api_kwargs["temperature"] = temperature
        if top_p is not None: api_kwargs["top_p"] = top_p
        if top_k is not None: api_kwargs["top_k"] = top_k
        if min_p is not None: api_kwargs["min_p"] = min_p
        if max_tokens is not None: api_kwargs["max_tokens"] = max_tokens
        if frequency_penalty is not None: api_kwargs["frequency_penalty"] = frequency_penalty
        if presence_penalty is not None: api_kwargs["presence_penalty"] = presence_penalty
        if seed is not None and seed != -1: api_kwargs["seed"] = seed

        # Merge extra parameters from JSON if provided
        if extra_parameters.strip():
            try:
                extra_data = json.loads(extra_parameters)
                if isinstance(extra_data, dict):
                    api_kwargs.update(extra_data)
                else:
                    print(f"Warning: extra_parameters JSON must be a dictionary. Got: {type(extra_data)}")
            except json.JSONDecodeError as e:
                print(f"Error parsing extra_parameters JSON: {e}")

        response = openai_client.chat.completions.create(**api_kwargs)
        completion = response.choices[0].message.content

        # Clean up memory
        del user_content
        del messages

        return IO.NodeOutput(completion)
