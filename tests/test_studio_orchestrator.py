import unittest
from pathlib import Path

from scripts.studio_orchestrator import load_workflow, replace_tokens, StudioError


class OrchestratorTests(unittest.TestCase):
    def test_default_workflow_is_comfy_api_format(self):
        graph = load_workflow("workflows/image/txt2img_api.template.json")
        self.assertEqual(graph["1"]["class_type"], "CheckpointLoaderSimple")
        self.assertEqual(graph["7"]["class_type"], "SaveImage")

    def test_placeholder_replacement(self):
        value = replace_tokens({"prompt": "{{PROMPT}}", "dims": ["{{WIDTH}}"]},
                               {"{{PROMPT}}": "cinematic portrait", "{{WIDTH}}": "768"})
        self.assertEqual(value, {"prompt": "cinematic portrait", "dims": ["768"]})

    def test_ui_workflow_is_rejected(self):
        with self.assertRaises(StudioError):
            load_workflow("tests/invalid-workflow.json")


if __name__ == "__main__":
    unittest.main()
