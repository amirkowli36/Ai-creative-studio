# Architecture

## Components and responsibilities

- **ChatGPT:** helps design workflows, explain errors, draft helper code and review configuration.
- **GitHub:** stores source code, documentation, notebooks and tested ComfyUI workflow exports.
- **ComfyUI:** provides the node-based generation and editing interface.
- **Google Colab:** optional hosted runtime for users without a local GPU.
- **Google Drive:** optional persistent storage for model weights and generated files.

## Data flow

1. Open the Colab notebook stored in this repository.
2. Start ComfyUI in the hosted runtime.
3. Open the temporary HTTPS tunnel URL on the iPhone.
4. Load a workflow JSON into ComfyUI.
5. Keep large models in Drive or download them into the temporary runtime when needed.
6. Export tested workflow JSON files back into the repository.

## Repository rules

- Store code, documentation, notebooks and workflow definitions in Git.
- Do not store model weights, private photos, generated output folders, API keys or access tokens in Git.
- Record the ComfyUI version, custom-node dependencies, model names and tested settings for each workflow.
- A workflow is not considered ready until it has been imported and run successfully in a clean, documented environment.

## Security

The starter notebook opens ComfyUI through a temporary Cloudflare Quick Tunnel without an application login layer. Treat the generated URL as a secret access link. Anyone who obtains it may reach the session. Do not use this setup for sensitive images or confidential work. Stop the tunnel when finished.

For private or production use, replace the quick tunnel with an authenticated access method and review the provider's security model.

## Compute and storage constraints

Colab free resources are best-effort and can be unavailable, limited or terminated. Runtime disk is temporary. Large models should be stored separately, and the notebook should be treated as a launcher rather than permanent hosting.

## Planned stages

1. Basic ComfyUI runtime
2. Text-to-image and image-to-image
3. Face/identity preservation
4. ControlNet pose and composition
5. Image-to-video
6. 3D generation
