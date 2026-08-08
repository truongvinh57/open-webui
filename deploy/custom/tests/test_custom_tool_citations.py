from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).parent
# Patch against the fork's own 0.11.0 backend source, not an external checkout.
FORK_MIDDLEWARE = ROOT.parents[2] / 'backend/open_webui/utils/middleware.py'
PATCHES = [
    ROOT.parent / 'patches/open_webui/utils/middleware-terminal-result.patch',
    ROOT.parent / 'patches/open_webui/utils/middleware-nonterminal-next-call.patch',
]


def patched_middleware_source() -> str:
    with tempfile.TemporaryDirectory() as directory:
        target = Path(directory) / 'middleware.py'
        target.write_bytes(FORK_MIDDLEWARE.read_bytes())
        for patch_path in PATCHES:
            subprocess.run(
                ['patch', '--batch', '--forward', str(target), str(patch_path)],
                check=True,
                capture_output=True,
                text=True,
            )
        return target.read_text(encoding='utf-8')


class CustomToolCitationPatchTest(unittest.TestCase):
    def test_internal_answer_citations_never_become_native_sources(self) -> None:
        source = patched_middleware_source()

        self.assertNotIn('get_citation_sources_from_custom_tool_result', source)
        self.assertNotIn('answer_citations[].citation_markdown payload opts in', source)
        self.assertNotIn('Error extracting custom-tool citation source', source)

    def test_builtin_web_and_knowledge_sources_remain_native(self) -> None:
        source = patched_middleware_source()

        self.assertIn("'search_web'", source)
        self.assertIn("'fetch_url'", source)
        self.assertIn("'query_knowledge_files'", source)
        self.assertIn('get_citation_source_from_tool_result(', source)
        self.assertIn("await event_emitter({'type': 'source', 'data': source})", source)

    def test_terminal_and_nonterminal_tool_contracts_remain_in_chain(self) -> None:
        source = patched_middleware_source()

        self.assertIn('NTC terminal tool-result handshake', source)
        self.assertIn('NTC nonterminal next-call handshake', source)


if __name__ == '__main__':
    unittest.main()
