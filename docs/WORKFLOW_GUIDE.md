# Workflow contribution and testing guide

A workflow should be reproducible, not merely a JSON file that happens to exist.

## Required information for every workflow

Add a README beside each exported workflow JSON containing:

- What the workflow does
- ComfyUI version or commit tested
- Required custom nodes and their source repositories
- Model names, file formats and expected locations
- Input image/video requirements
- Resolution, steps, sampler, frame count and other important settings
- Approximate VRAM/RAM requirements, when known
- Exact steps used to test it
- Known limitations and license notes

## Validation checklist

- [ ] Workflow JSON parses successfully.
- [ ] All required nodes are available in a clean ComfyUI environment.
- [ ] Model files and their expected paths are documented.
- [ ] The workflow runs from start to finish.
- [ ] Output quality and failure cases have been inspected.
- [ ] No private input images, credentials or model weights are included in the commit.
- [ ] Model and custom-node licenses have been reviewed.

## Exporting from ComfyUI

Export the workflow in the format supported by the intended import path. ComfyUI has both UI workflow exports and API prompt representations; do not assume they are interchangeable. Keep the original export and document which format it uses.

## Custom nodes

Install only the custom nodes required by the workflow. Record their repository URL and a tested commit or release when possible. Avoid unpinned "install everything" scripts because they make the environment harder to reproduce.
