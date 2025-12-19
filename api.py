from aiohttp import web
import aiohttp

async def fetch_sg_openai_models(request):
    data = await request.json()
    api_key = data.get('api_key')
    base_url = data.get('base_url') or 'https://api.openai.com/v1'
    if not api_key:
        return web.json_response([])
    async with aiohttp.ClientSession() as session:
        headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
        try:
            async with session.get(f'{base_url}/models', headers=headers) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    models = [m['id'] for m in result.get('data', [])]
                    return web.json_response(models)
                else:
                    print(f"Failed to fetch models: {resp.status}")
                    return web.json_response([])
        except Exception as e:
            print(f"Error fetching models: {e}")
            return web.json_response([])
