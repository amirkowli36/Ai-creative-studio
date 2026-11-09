# Using AI Creative Studio from an iPhone

## You need

- Safari or another modern mobile browser
- A Google account for Colab
- Access to this GitHub repository
- A stable internet connection

## First launch

1. Open the [starter notebook in Google Colab](https://colab.research.google.com/github/amirkowli36/Ai-creative-studio/blob/main/notebooks/ComfyUI_Colab_Starter.ipynb).
2. In Colab, choose **Runtime → Change runtime type**.
3. Select a GPU runtime if one is offered. Availability is not guaranteed.
4. Run the cells from top to bottom.
5. When the tunnel cell prints a `trycloudflare.com` URL, open that URL in a new Safari tab.
6. Keep the Colab tab and running session active while using ComfyUI.

## iPhone tips

- Rotate to landscape orientation for the node editor.
- Safari's **Request Desktop Website** option may make node editing easier.
- Save workflow JSON files to Files or Drive before the runtime ends.
- Keep the original source image backed up separately.
- If the Colab session disconnects, restart the runtime and rerun the notebook.

## Troubleshooting

**No GPU is available:** Colab may not offer a free GPU at that moment. CPU execution is possible for some tasks but usually much slower.

**The tunnel URL does not open:** confirm that the ComfyUI and tunnel cells are still running. Use the newest URL printed by the current session.

**The session ended:** restart the runtime and rerun the notebook. Files stored only in the runtime may be lost.

**Out of memory:** start with a smaller model, lower resolution, fewer frames or a lighter workflow.

## Security warning

The quick-tunnel URL is not protected by a ComfyUI login in this starter setup. Do not share it. Do not upload private or sensitive photos. Stop the tunnel when you finish.
