from .nodes.openai_client import OpenAIClientNode
from .nodes.openai_chat_completion import OpenAIChatCompletionNode
from .api import fetch_sg_openai_models
from server import PromptServer
from aiohttp import web

NODE_CLASS_MAPPINGS = {
    "OpenAIClient": OpenAIClientNode,
    "OpenAIChatCompletion": OpenAIChatCompletionNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "OpenAIClient": "OpenAI Client",
    "OpenAIChatCompletion": "OpenAI Chat Completion",
}

WEB_DIRECTORY = "./web"
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]

route = web.RouteDef('POST', '/sg_openai_models', fetch_sg_openai_models, {})
PromptServer.instance.routes._items.append(route)
