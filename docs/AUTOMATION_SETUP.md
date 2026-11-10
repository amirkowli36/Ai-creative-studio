# Automation setup

This repository contains a manually triggered GitHub Actions workflow that connects OpenAI's Responses API to a ComfyUI server.

## What the workflow does

- Checks ComfyUI health through /system_stats and /object_info.
- Checks OpenAI API credentials without printing them.
- Refines an image request through the Responses API.
- Submits an API-format graph to ComfyUI at /prompt.
- Polls /history/{prompt_id}, downloads outputs from /view, and attaches results to the GitHub Actions run.
- Keeps generated images out of Git; output artifacts are retained for seven days.

The workflow is manual-only. It does not run on pull requests or arbitrary incoming webhooks, so untrusted events cannot consume paid API credits or reach the ComfyUI endpoint.

## Required GitHub Actions secrets

Open the repository Settings → Secrets and variables → Actions → New repository secret.

| Secret name | Value |
|---|---|
| OPENAI_API_KEY | Project API key from OpenAI Platform |
| COMFYUI_BASE_URL | Current HTTPS base URL for ComfyUI, without a trailing slash |

Optional secrets for a Cloudflare Access-protected endpoint:

| Secret name | Value |
|---|---|
| COMFYUI_CF_ACCESS_CLIENT_ID | Cloudflare Access service-token client ID |
| COMFYUI_CF_ACCESS_CLIENT_SECRET | Cloudflare Access service-token client secret |

If Cloudflare Access is enabled, add both optional secrets. Do not add only one.

## Optional Actions variables

Under Settings → Secrets and variables → Actions → Variables:

| Variable | Purpose |
|---|---|
| OPENAI_MODEL | Defaults to gpt-6-luna. Change it to a model enabled for your OpenAI project. |
| COMFYUI_CHECKPOINT | Exact checkpoint filename. When omitted, the first available checkpoint is selected. |

## Run it from an iPhone

1. Start the ComfyUI Colab notebook and keep its runtime running.
2. Copy the newest HTTPS URL printed by the notebook. Do not post it in chat or commit it.
3. Open GitHub → Actions → AI Creative Studio Orchestrator → Run workflow.
4. First select health-check. Only after it passes, select generate-image and enter a prompt.
5. Open the finished run and download its ai-creative-studio-output artifact.

The current Colab notebook uses a Cloudflare Quick Tunnel without a ComfyUI login. Anyone who gets the URL may be able to reach that session. Use only non-sensitive test images with this temporary endpoint. For private work, use an authenticated HTTPS gateway such as Cloudflare Access and configure the service-token secrets above.

## Workflow format

The default image graph is an API-format ComfyUI workflow using built-in CheckpointLoaderSimple, CLIPTextEncode, EmptyLatentImage, KSampler, VAEDecode, and SaveImage nodes. The script substitutes these tokens:

- {{PROMPT}}
- {{NEGATIVE_PROMPT}}
- {{CHECKPOINT}}
- {{WIDTH}}
- {{HEIGHT}}
- {{STEPS}}
- {{SEED}}

ComfyUI validates the graph when submitted. Missing nodes, missing models or incompatible checkpoint families will fail with a clear run error. For SDXL or custom-node pipelines, replace the template with an API-format workflow exported from the running ComfyUI instance and document its dependencies.

## Important limits

- GitHub Actions is an on-demand runner, not a permanent server.
- Free Colab runtimes can disconnect; Quick Tunnel URLs change after a restart.
- OpenAI API usage is billed separately from a ChatGPT subscription.
- Images are stored as workflow run artifacts, not committed to Git.
- The workflow has read-only repository permissions.

## API references

- OpenAI Responses API: https://platform.openai.com/docs/api-reference/responses
- GitHub Actions secrets: https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets
- GitHub manual workflow runs: https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow
- ComfyUI server routes: https://github.com/Comfy-Org/docs/blob/main/development/comfyui-server/comms_routes.mdx
