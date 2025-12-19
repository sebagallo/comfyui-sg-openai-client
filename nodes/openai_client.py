from openai import OpenAI

class OpenAIClientNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"multiline": False}),
            },
            "optional": {
                "base_url": ("STRING", {"multiline": False, "default": ""}),
            }
        }

    RETURN_TYPES = ("OPENAI_CLIENT",)
    FUNCTION = "create_client"
    CATEGORY = "OpenAI"

    def create_client(self, api_key, base_url=""):
        if base_url:
            client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            client = OpenAI(api_key=api_key)
        return ({"client": client},)
