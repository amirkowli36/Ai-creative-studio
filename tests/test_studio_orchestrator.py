import tempfile
import unittest
from pathlib import Path

from scripts.studio_orchestrator import load_workflow, replace_tokens, StudioError


class OrchestratorTests(unittest.TestCase):
    def test_default_workflow_is_comfy_api_format(self):
        graph = load_workflow("workflows/image/txt2img_api.template.json")
        self.assertEqual(graph["1"]["class_type"], "CheckpointLoaderSimple")
        self.assertEqual(graph["7"]["class_type"], "SaveImage")

    def test_placeholder_replacement_preserves_numeric_types(self):
        value = replace_tokens(
            {
                "prompt": "{{PROMPT}}",
                "width": "{{WIDTH}}",
                "height": "{{HEIGHT}}",
                "steps": "{{STEPS}}",
                "seed": "{{SEED}}",
            },
            {
                "{{PROMPT}}": "cinematic portrait",
                "{{WIDTH}}": 768,
                "{{HEIGHT}}": 768,
                "{{STEPS}}": 20,
                "{{SEED}}": 12345,
            },
        )
        self.assertEqual(value["prompt"], "cinematic portrait")
        self.assertIsInstance(value["width"], int)
        self.assertIsInstance(value["height"], int)
        self.assertIsInstance(value["steps"], int)
        self.assertIsInstance(value["seed"], int)

    def test_regular_ui_workflow_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "ui-workflow.json"
            path.write_text('{"nodes": []}', encoding="utf-8")
            with self.assertRaises(StudioError):
                load_workflow(path)


if __name__ == "__main__":
    unittest.main()
