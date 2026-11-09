# Model storage policy

Model weights are intentionally not stored in this Git repository. Many model files are several gigabytes, may have separate licenses and can exceed Git hosting limits.

## Recommended approach

1. Keep model files in Google Drive or another storage location you control.
2. In workflow documentation, list the exact model filename, source page and license.
3. Download only the models required by the workflow into the runtime.
4. Keep credentials and private download links out of committed notebooks and scripts.

## Typical ComfyUI locations

- Checkpoints: `ComfyUI/models/checkpoints/`
- LoRAs: `ComfyUI/models/loras/`
- VAE: `ComfyUI/models/vae/`
- ControlNet: `ComfyUI/models/controlnet/`
- CLIP / text encoders: `ComfyUI/models/clip/`

Folder requirements may differ by model and custom node. Follow the model publisher's instructions.
