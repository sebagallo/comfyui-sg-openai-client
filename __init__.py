from .nodes.openai_client import OpenAIClientNode
from .nodes.openai_chat_completion import OpenAIChatCompletionNode
from .api import fetch_sg_openai_models
from server import PromptServer
from aiohttp import web
from comfy_api.latest import ComfyExtension
from typing_extensions import override

class SgOpenaiClientExtension(ComfyExtension):
    @override
    async def get_node_list(self) -> list[type]:
        return [
            OpenAIClientNode,
            OpenAIChatCompletionNode,
        ]

async def comfy_entrypoint() -> SgOpenaiClientExtension:
    return SgOpenaiClientExtension()

NODE_CLASS_MAPPINGS = {
    "OpenAIClient": OpenAIClientNode,
    "OpenAIChatCompletion": OpenAIChatCompletionNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "OpenAIClient": "OpenAI Client",
    "OpenAIChatCompletion": "OpenAI Chat Completion",
}

WEB_DIRECTORY = "./web"
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY", "comfy_entrypoint"]

route = web.RouteDef('POST', '/sg_openai_models', fetch_sg_openai_models, {})
PromptServer.instance.routes._items.append(route)
