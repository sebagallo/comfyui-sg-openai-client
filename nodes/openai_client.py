from openai import OpenAI
from comfy_api.latest import IO

class OpenAIClientNode(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="OpenAIClient",
            display_name="OpenAI Client",
            category="OpenAI",
            inputs=[
                IO.String.Input("api_key", multiline=False),
                IO.String.Input("base_url", multiline=False, default="", optional=True),
            ],
            outputs=[
                IO.Custom("OPENAI_CLIENT").Output(),
            ],
        )

    @classmethod
    async def execute(cls, api_key: str, base_url: str | None = None) -> IO.NodeOutput:
        if base_url:
            client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            client = OpenAI(api_key=api_key)
        return IO.NodeOutput({"client": client})
