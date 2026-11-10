#!/usr/bin/env python3
"""Run the AI Creative Studio OpenAI + ComfyUI pipeline."""

import argparse
import json
import os
import re
import secrets
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path


class StudioError(RuntimeError):
    pass


def request(url, method="GET", payload=None, headers=None, timeout=30):
    request_headers = {"User-Agent": "AI-Creative-Studio/0.1"}
    if headers:
        request_headers.update(headers)
    client_id = os.getenv("COMFYUI_CF_ACCESS_CLIENT_ID", "").strip()
    client_secret = os.getenv("COMFYUI_CF_ACCESS_CLIENT_SECRET", "").strip()
    if bool(client_id) != bool(client_secret):
        raise StudioError("Cloudflare Access needs both service-token secrets, or neither.")
    if client_id:
        request_headers["CF-Access-Client-Id"] = client_id
        request_headers["CF-Access-Client-Secret"] = client_secret
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        request_headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=request_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read(1500).decode("utf-8", errors="replace")
        raise StudioError(f"HTTP {exc.code} from {urllib.parse.urlsplit(url).hostname}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise StudioError(
            f"Cannot reach {urllib.parse.urlsplit(url).hostname}: {exc.reason}. "
            "Check that the ComfyUI runtime is running and its URL is current."
        ) from exc


def request_json(url, **kwargs):
    try:
        result = json.loads(request(url, **kwargs).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise StudioError(f"Invalid JSON response from {urllib.parse.urlsplit(url).hostname}.") from exc
    if not isinstance(result, (dict, list)):
        raise StudioError("Unexpected JSON response.")
    return result


def comfy_url():
    value = os.getenv("COMFYUI_BASE_URL", "").strip().rstrip("/")
    parsed = urllib.parse.urlsplit(value)
    if not value or parsed.scheme not in ("https", "http") or not parsed.netloc:
        raise StudioError("Add a valid COMFYUI_BASE_URL as a GitHub Actions secret.")
    if parsed.scheme != "https" and parsed.hostname not in ("localhost", "127.0.0.1"):
        raise StudioError("Remote ComfyUI URLs must use HTTPS.")
    if parsed.query or parsed.fragment:
        raise StudioError("COMFYUI_BASE_URL must not include a query string or fragment.")
    return value


def openai_headers():
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        raise StudioError("Add OPENAI_API_KEY as a GitHub Actions secret. Never commit or paste it into chat.")
    return {"Authorization": f"Bearer {key}"}


def check_openai():
    models = request_json("https://api.openai.com/v1/models", headers=openai_headers(), timeout=30)
    return len(models.get("data", [])) if isinstance(models, dict) else 0


def health_check():
    base = comfy_url()
    host = urllib.parse.urlsplit(base).hostname or "unknown"
    stats = request_json(f"{base}/system_stats", timeout=30)
    nodes = request_json(f"{base}/object_info", timeout=60)
    if not isinstance(stats, dict) or not isinstance(nodes, dict):
        raise StudioError("ComfyUI returned an unexpected health-check response.")
    try:
        inventory = request_json(f"{base}/models/checkpoints", timeout=30)
        count = len(inventory) if isinstance(inventory, list) else 0
    except StudioError:
        count = 0
    print("ComfyUI: connected")
    print(f"Endpoint host: {host}")
    print(f"Node types: {len(nodes)}")
    print(f"Checkpoint files: {count}")
    print(f"OpenAI API models visible: {check_openai()}")
    if count == 0:
        print("Warning: no checkpoint inventory was returned. Generation may need a model filename.")
    return 0


def response_text(result):
    text = result.get("output_text")
    if isinstance(text, str) and text.strip():
        return text.strip()
    parts = []
    for item in result.get("output", []):
        if isinstance(item, dict):
            for part in item.get("content", []):
                if isinstance(part, dict) and part.get("type") in ("output_text", "text"):
                    if isinstance(part.get("text"), str):
                        parts.append(part["text"])
    value = "\n".join(parts).strip()
    if not value:
        raise StudioError("OpenAI returned no prompt text. Check model access and API billing.")
    return value


def enhance_prompt(user_prompt):
    model = os.getenv("OPENAI_MODEL", "").strip() or "gpt-6-luna"
    payload = {
        "model": model,
        "input": [
            {
                "role": "system",
                "content": (
                    "Rewrite the user's request as one precise, high-quality image-generation "
                    "prompt for ComfyUI. Preserve the subject, composition, visual style, "
                    "lighting, materials, and all explicit constraints. Do not invent text, "
                    "logos, people, or scene changes. Return only the prompt."
                ),
            },
            {"role": "user", "content": user_prompt},
        ],
        "max_output_tokens": 350,
    }
    result = request_json(
        "https://api.openai.com/v1/responses",
        method="POST",
        payload=payload,
        headers=openai_headers(),
        timeout=90,
    )
    if not isinstance(result, dict):
        raise StudioError("OpenAI returned an unexpected response.")
    return response_text(result)


def load_workflow(path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise StudioError(f"Cannot read workflow JSON file: {path}") from exc
    if not isinstance(data, dict) or not data:
        raise StudioError("Workflow must be a non-empty ComfyUI API-format JSON object.")
    for node_id, node in data.items():
        if not isinstance(node, dict) or not isinstance(node.get("class_type"), str):
            raise StudioError(
                f"Node {node_id} is missing class_type. Export API-format JSON from ComfyUI."
            )
        if not isinstance(node.get("inputs"), dict):
            raise StudioError(f"Node {node_id} is missing its inputs object.")
    return data


def replace_tokens(value, replacements):
    if isinstance(value, dict):
        return {k: replace_tokens(v, replacements) for k, v in value.items()}
    if isinstance(value, list):
        return [replace_tokens(v, replacements) for v in value]
    if isinstance(value, str):
        for key, replacement in replacements.items():
            value = value.replace(key, replacement)
    return value


def choose_checkpoint(base):
    configured = os.getenv("COMFYUI_CHECKPOINT", "").strip()
    if configured:
        return configured
    models = request_json(f"{base}/models/checkpoints", timeout=30)
    if isinstance(models, list) and models:
        first = models[0]
        if isinstance(first, str):
            return first
        if isinstance(first, dict):
            return first.get("name") or first.get("filename")
    raise StudioError(
        "No checkpoint model found. Add COMFYUI_CHECKPOINT as an Actions variable "
        "with the exact filename shown in ComfyUI."
    )


def generate(prompt, workflow_path, width, height, steps):
    if not prompt.strip():
        raise StudioError("Enter a prompt to generate an image.")
    if width < 256 or width > 2048 or width % 64 or height < 256 or height > 2048 or height % 64:
        raise StudioError("Width and height must be multiples of 64 between 256 and 2048.")
    if steps < 1 or steps > 60:
        raise StudioError("Steps must be between 1 and 60.")
    base = comfy_url()
    improved = enhance_prompt(prompt)
    checkpoint = choose_checkpoint(base)
    seed = secrets.randbelow(2**32 - 1)
    workflow = replace_tokens(
        load_workflow(workflow_path),
        {
            "{{PROMPT}}": improved,
            "{{NEGATIVE_PROMPT}}": "low quality, blurry, distorted anatomy, artifacts, watermark, text",
            "{{CHECKPOINT}}": checkpoint,
            "{{WIDTH}}": str(width),
            "{{HEIGHT}}": str(height),
            "{{STEPS}}": str(steps),
            "{{SEED}}": str(seed),
        },
    )
    if "{{" in json.dumps(workflow):
        raise StudioError("Workflow contains unresolved template placeholders.")
    prompt_id = str(uuid.uuid4())
    queued = request_json(
        f"{base}/prompt",
        method="POST",
        payload={"prompt": workflow, "client_id": str(uuid.uuid4()), "prompt_id": prompt_id},
        timeout=90,
    )
    if not isinstance(queued, dict):
        raise StudioError("ComfyUI returned an unexpected queue response.")
    if queued.get("error") or queued.get("node_errors"):
        raise StudioError("ComfyUI rejected the workflow. Check installed nodes and checkpoint model.")
    prompt_id = str(queued.get("prompt_id") or prompt_id)
    print(f"ComfyUI accepted job {prompt_id}")
    deadline = time.monotonic() + 1800
    completed = None
    while time.monotonic() < deadline:
        history = request_json(f"{base}/history/{urllib.parse.quote(prompt_id, safe='')}", timeout=30)
        if isinstance(history, dict) and isinstance(history.get(prompt_id), dict):
            completed = history[prompt_id]
            status = completed.get("status", {})
            if isinstance(status, dict) and status.get("status_str") == "error":
                raise StudioError("ComfyUI reported an execution error. Inspect the run logs.")
            if isinstance(completed.get("outputs"), dict) and completed["outputs"]:
                break
        time.sleep(5)
    if not completed or not isinstance(completed.get("outputs"), dict):
        raise StudioError("Timed out waiting for ComfyUI (30-minute limit).")
    image_items = []
    for output in completed["outputs"].values():
        if isinstance(output, dict):
            image_items.extend(x for x in output.get("images", []) if isinstance(x, dict))
    if not image_items:
        raise StudioError("Workflow finished without images. It needs a SaveImage output node.")
    out_dir = Path("studio-output")
    out_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    for number, image in enumerate(image_items, start=1):
        query = urllib.parse.urlencode(
            {"filename": image["filename"], "subfolder": image.get("subfolder", ""), "type": image.get("type", "output")}
        )
        content = request(f"{base}/view?{query}", timeout=120)
        filename = re.sub(r"[^A-Za-z0-9_.-]+", "_", Path(image["filename"]).name)
        path = out_dir / f"{number:02d}_{filename}"
        path.write_bytes(content)
        saved.append(path.name)
    metadata = {
        "prompt_id": prompt_id,
        "checkpoint": checkpoint,
        "seed": seed,
        "width": width,
        "height": height,
        "steps": steps,
        "files": saved,
    }
    (out_dir / "run-metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Generation complete: {len(saved)} image(s) saved.")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("health-check", "generate-image"), required=True)
    parser.add_argument("--prompt", default="")
    parser.add_argument("--workflow-path", default="workflows/image/txt2img_api.template.json")
    parser.add_argument("--width", type=int, default=768)
    parser.add_argument("--height", type=int, default=768)
    parser.add_argument("--steps", type=int, default=20)
    args = parser.parse_args()
    try:
        return health_check() if args.mode == "health-check" else generate(
            args.prompt, args.workflow_path, args.width, args.height, args.steps
        )
    except StudioError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
