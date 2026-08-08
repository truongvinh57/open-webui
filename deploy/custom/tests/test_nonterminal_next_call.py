from pathlib import Path
import unittest


PATCH = Path(__file__).parent.parent / 'patches/open_webui/utils/middleware-nonterminal-next-call.patch'
TERMINAL_PATCH = Path(__file__).parent.parent / 'patches/open_webui/utils/middleware-terminal-result.patch'


class NonterminalNextCallPatchTest(unittest.TestCase):
    def test_patch_preserves_model_tool_loop_and_signed_arguments(self) -> None:
        source = PATCH.read_text(encoding='utf-8')

        self.assertIn('NTC nonterminal next-call handshake', source)
        self.assertIn("terminal_payload.get('terminal') is False", source)
        self.assertIn("isinstance(terminal_payload.get('next_call'), dict)", source)
        self.assertIn('Trusted server-side tool results require continuation', source)
        self.assertIn('Complete every independent continuation contract', source)
        self.assertIn("new_form_data['messages'] = add_or_update_system_message(", source)
        self.assertIn('append=True', source)
        self.assertIn('json.dumps(continuation_contracts', source)
        self.assertNotIn("'role': 'user'", source)
        self.assertNotIn('await tool_function(**next_arguments)', source)

    def test_mixed_parallel_results_preserve_every_open_branch(self) -> None:
        terminal_source = TERMINAL_PATCH.read_text(encoding='utf-8')
        continuation_source = PATCH.read_text(encoding='utf-8')

        self.assertIn('all_tool_results_terminal = bool(response_tool_calls)', terminal_source)
        self.assertIn(
            'all_tool_results_terminal = all_tool_results_terminal and is_terminal_answer',
            terminal_source,
        )
        self.assertIn('nonterminal_next_calls = []', continuation_source)
        self.assertIn('nonterminal_next_calls.append(next_call)', continuation_source)
        self.assertIn('for next_call in nonterminal_next_calls', continuation_source)
        self.assertNotIn("nonterminal_next_call = terminal_payload['next_call']", continuation_source)
        self.assertNotIn('terminal_tool_result', continuation_source)


if __name__ == '__main__':
    unittest.main()
