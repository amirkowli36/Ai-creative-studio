# AI Creative Studio

A mobile-first creative studio built around **ChatGPT + GitHub + ComfyUI**, with Google Colab as an optional cloud runtime.

The goal is to create a practical, repeatable image and video workflow that can be operated from an iPhone without owning a GPU.

## Start here

1. Open the [ComfyUI Colab starter notebook](https://colab.research.google.com/github/amirkowli36/Ai-creative-studio/blob/main/notebooks/ComfyUI_Colab_Starter.ipynb).
2. In Colab, select a GPU runtime when one is available.
3. Run the notebook cells in order.
4. Open the temporary HTTPS URL printed by the tunnel cell in your iPhone browser.
5. Keep the Colab session running while using ComfyUI.

Colab free GPU access is not guaranteed. Sessions can be interrupted and their local files are temporary.

## What each component does

| Component | Responsibility |
|---|---|
| ChatGPT | Plan workflows, explain errors, draft and review code |
| GitHub | Version-control notebooks, scripts, docs and tested workflow exports |
| ComfyUI | Run node-based image generation and editing |
| Google Colab | Optional hosted runtime when no local GPU is available |
| Google Drive | Optional storage for large model files and outputs |

## Repository layout

- `notebooks/`: cloud setup notebooks
- `workflows/image/`: image generation and image-to-image
- `workflows/face/`: identity-preservation workflow notes
- `workflows/controlnet/`: pose and composition control
- `workflows/video/`: image-to-video and video workflows
- `workflows/3d/`: 3D generation workflow notes
- `models/`: model storage guidance; weights are not committed
- `docs/`: architecture and operating guides
- `scripts/`: validation and runtime diagnostics
- `.github/workflows/`: automatic repository checks

## Build sequence

1. Get ComfyUI running from the iPhone through Colab.
2. Add and test image-generation and image-to-image workflows.
3. Add identity-preservation workflows.
4. Add ControlNet pose and composition control.
5. Add image-to-video workflows.
6. Add 3D generation workflows.

## Important limitations and safety

- Model weights are large and must not be committed to Git. Keep them in Drive or download them into a temporary runtime.
- The starter notebook uses a temporary Cloudflare Quick Tunnel. Anyone who obtains its URL may reach the ComfyUI session. Do not share the URL or use it for private/sensitive images.
- Free cloud GPU capacity and session duration are controlled by the provider and are not guaranteed.
- Workflow JSON files will be added only after testing with the required ComfyUI version, custom nodes and models.
- Check the license and usage terms of every model and custom node before using or distributing it.
- Use face-reference workflows only with appropriate permission from the people depicted.

## Guides

- [Architecture](docs/ARCHITECTURE.md)
- [iPhone setup](docs/IPHONE_SETUP.md)
- [Workflow contribution and testing](docs/WORKFLOW_GUIDE.md)
- [Model storage](models/README.md)

## License

The repository's original scripts, documentation and configuration are provided under the MIT License. Third-party models, custom nodes and dependencies keep their own licenses.
