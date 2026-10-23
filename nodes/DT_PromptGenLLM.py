# Prompt expansion via any OpenAI-compatible endpoint.
# Config: copy config.llm.example.json -> config.llm.local.json (gitignored)
# or env VEXTRA_LLM_URL / VEXTRA_LLM_TOKEN / VEXTRA_LLM_MODEL.
import os, json, urllib.request

CONF = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'config.llm.local.json')

def _cfg():
    c = {'url': 'http://127.0.0.1:7070/v1', 'token': '', 'model': ''}
    try:
        c.update(json.load(open(CONF)))
    except Exception:
        pass
    c['url'] = os.environ.get('VEXTRA_LLM_URL', c['url']).rstrip('/')
    c['token'] = os.environ.get('VEXTRA_LLM_TOKEN', c['token'])
    c['model'] = os.environ.get('VEXTRA_LLM_MODEL', c['model'])
    return c

class PromptGenLLM:
    CATEGORY = "VextraNodes"
    RETURN_TYPES = ("STRING",)
    FUNCTION = "expand"

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "prompt": ("STRING", {"multiline": True, "default": ""}),
            "style": (["sd-tags", "natural", "detailed"],),
            "max_tokens": ("INT", {"default": 120, "min": 16, "max": 2048}),
            "temperature": ("FLOAT", {"default": 0.8, "min": 0.0, "max": 2.0, "step": 0.05}),
        }}

    def expand(self, prompt, style, max_tokens, temperature):
        c = _cfg()
        if not c['model']:
            raise RuntimeError(f"Vextra LLM node: set model in {CONF} or VEXTRA_LLM_MODEL")
        sys_prompt = {
            'sd-tags': "Expand into a Stable Diffusion tag prompt. Comma-separated tags only, no prose.",
            'natural': "Expand into a detailed image-generation prompt. One paragraph, vivid and concrete.",
            'detailed': "Expand into a rich cinematic prompt: subject, composition, lighting, palette. One paragraph.",
        }[style]
        body = {"model": c['model'], "max_tokens": max_tokens, "temperature": temperature,
                "messages": [{"role": "system", "content": sys_prompt},
                             {"role": "user", "content": prompt}]}
        req = urllib.request.Request(c['url'] + '/chat/completions', data=json.dumps(body).encode(),
            headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {c['token']}"})
        with urllib.request.urlopen(req, timeout=300) as r:
            return (json.load(r)['choices'][0]['message']['content'].strip(),)

NODE_CLASS_MAPPINGS = {"Prompt Expand LLM (Vextra)": PromptGenLLM}
NODE_DISPLAY_NAME_MAPPINGS = {"Prompt Expand LLM (Vextra)": "Prompt Expand (LLM)"}
