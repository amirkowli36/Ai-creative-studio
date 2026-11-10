# Architecture

## Components and responsibilities

- **ChatGPT:** interprets requests, selects workflows, reviews results and helps troubleshoot.
- **OpenAI Platform API (optional):** refines natural-language image prompts through the Responses API. It is disabled when no API key is configured, preserving a zero-cost prompt path.
- **GitHub:** stores source code, documentation, notebooks, validated workflow exports and automation definitions.
- **GitHub Actions:** runs the orchestrator on demand with read-only repository permissions and credentials supplied through Actions secrets.
- **ComfyUI:** validates and executes node-based image generation and editing graphs.
- **Google Colab:** optional hosted runtime for users without a local GPU.
- **Google Drive:** optional persistent storage for large model files and generated files.

## Main data flow

1. Start the ComfyUI Colab notebook and keep its runtime active.
2. Store the current ComfyUI HTTPS endpoint as the repository secret COMFYUI_BASE_URL.
3. Start the AI Creative Studio Orchestrator from GitHub Actions.
4. The orchestrator checks ComfyUI, prepares the image prompt, and submits the API-format workflow to ComfyUI.
5. The orchestrator polls execution history and downloads generated images from ComfyUI.
6. GitHub Actions stores the images as a short-lived workflow artifact; outputs are not committed to Git.

## Optional OpenAI path

When OPENAI_API_KEY is present, the orchestrator calls the OpenAI Responses API to refine the user's prompt. Without the key, it sends the original prompt directly to ComfyUI. OpenAI API usage is billed separately from a ChatGPT subscription. The selected API model can be changed with the OPENAI_MODEL Actions variable.

## Repository rules

- Store code, documentation, notebooks and workflow definitions in Git.
- Do not store model weights, private photos, generated output folders, API keys or access tokens in Git.
- Use GitHub Actions secrets for all credentials and variables only for non-sensitive configuration.
- Keep workflow permissions read-only unless a specific task proves a write permission is needed.
- Record the ComfyUI version, custom-node dependencies, model names and tested settings for each workflow.
- A workflow is not considered ready until it has been imported and run successfully in a documented environment.

## Security

The starter notebook currently opens ComfyUI through a temporary Cloudflare Quick Tunnel without an application login layer. Treat the current URL as a bearer secret: anyone who obtains it may reach the running ComfyUI session. Do not use this setup for private or sensitive images.

For private work, put the server behind an authenticated HTTPS gateway such as Cloudflare Access and configure the matching service-token secrets in GitHub Actions. Never print credentials or tunnel URLs into workflow logs.

The GitHub Actions workflow is intentionally manual-only. It does not trigger on pull requests, issues, or untrusted webhooks, preventing external events from consuming API credits or reaching the ComfyUI endpoint.

## Compute and storage constraints

Colab free resources are best-effort and can be unavailable, limited or terminated. Runtime disk is temporary. Large models should be stored separately, and the notebook should be treated as a launcher rather than permanent hosting. GitHub Actions runners are also temporary and only exist while a job runs.

## Planned stages

1. Basic ComfyUI runtime
2. Text-to-image and image-to-image
3. Face/identity preservation
4. ControlNet pose and composition
5. Image-to-video
6. 3D generation
7. Authenticated long-lived ComfyUI endpoint and optional email reporting
