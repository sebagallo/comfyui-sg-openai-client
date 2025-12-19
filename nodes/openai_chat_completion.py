from .utils import image_to_data_uri

class OpenAIChatCompletionNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "client": ("OPENAI_CLIENT",),
                "system_prompt": ("STRING", {"multiline": True}),
                "user_prompt": ("STRING", {"multiline": True}),
                "model": ("COMBO", {"choices": []}),
            },
            "optional": {
                "image": ("IMAGE",),
                "temperature": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.1}),
                "top_p": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "max_tokens": ("INT", {"default": 1000, "min": 1, "max": 4096}),
                "frequency_penalty": ("FLOAT", {"default": 0.0, "min": -2.0, "max": 2.0, "step": 0.1}),
                "presence_penalty": ("FLOAT", {"default": 0.0, "min": -2.0, "max": 2.0, "step": 0.1}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "generate_completion"
    CATEGORY = "OpenAI"

    def generate_completion(self, client, system_prompt, user_prompt, model, image=None, temperature=1.0, top_p=1.0, max_tokens=1000, frequency_penalty=0.0, presence_penalty=0.0):
        openai_client = client["client"]

        # Prepare user message content
        user_content = [{"type": "text", "text": user_prompt}]

        if image is not None:
            B = image.shape[0]
            for i in range(B):
                img_tensor = image[i]  # (H, W, C)
                data_uri = image_to_data_uri(img_tensor)
                user_content.append({
                    "type": "image_url",
                    "image_url": {"url": data_uri}
                })

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]

        response = openai_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
        )
        completion = response.choices[0].message.content

        # Clean up memory
        del user_content
        del messages
        del response

        return (completion,)
