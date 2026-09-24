"""Adversarial regression tests: failure paths must never reach experiment design."""
import copy
import hashlib
import io
import json
import os
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stderr
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from cohervia_scientist.cli import build_parser
from cohervia_scientist.context import RepositoryContext
from cohervia_scientist.json_utils import parse_json_object
from cohervia_scientist.memory import ScientificMemory
from cohervia_scientist.provider import OpenAIProvider, ScriptedProvider
from cohervia_scientist.reasoning import ScientificReasoner, write_packet
from cohervia_scientist.schemas import ExperimentPlan
from test_reasoning import QUESTION, HYPOTHESES, CRITIQUES, SELECTION, EXPERIMENT, REVIEW
import test_reasoning


class BoundaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo, self.root = test_reasoning.ReasonerTests()._repo(self.tmp.name)

    def reasoner(self, responses=None, **kwargs):
        if responses is None:
            responses = [QUESTION, HYPOTHESES, CRITIQUES, SELECTION, EXPERIMENT, REVIEW]
        self.provider = ScriptedProvider([json.dumps(x) for x in responses])
        return ScientificReasoner(provider=self.provider, repo_root=self.repo,
                                  scientist_root=self.root, **kwargs)

    def config(self, **changes):
        path = self.root / 'config/reasoning.json'
        value = json.loads(path.read_text())
        value.update(changes)
        path.write_text(json.dumps(value))

    def test_all_rejected_stops_after_critique_and_preserves_packet(self):
        critiques = copy.deepcopy(CRITIQUES)
        for item in critiques['critiques']:
            item['recommendation'] = 'reject'
        packet = self.reasoner([QUESTION, HYPOTHESES, critiques]).run()
        self.assertEqual(len(self.provider.calls), 3)
        self.assertEqual(packet.status, 'blocked_by_critic')
        self.assertIsNone(packet.selection.hypothesis_id)
        self.assertIsNone(packet.experiment)
        path = write_packet(packet, scientist_root=self.root)
        self.assertEqual(json.loads(path.read_text())['evidence_status'], 'not_evidence')

    def test_selection_cannot_override_rejection_or_revision(self):
        for recommendation in ('reject', 'revise'):
            with self.subTest(recommendation=recommendation):
                critiques = copy.deepcopy(CRITIQUES)
                critiques['critiques'][0]['recommendation'] = recommendation
                critiques['critiques'][1]['recommendation'] = 'advance_exploratory'
                reasoner = self.reasoner([QUESTION, HYPOTHESES, critiques, SELECTION])
                with self.assertRaisesRegex(ValueError, 'critic-approved'):
                    reasoner.run()
                self.assertEqual(len(self.provider.calls), 4)

    def test_contradictory_critic_approval_is_blocked(self):
        for field in ('fatal_flaws', 'required_revisions', 'leakage_risks'):
            with self.subTest(field=field):
                critiques = copy.deepcopy(CRITIQUES)
                critiques['critiques'][0][field] = ['unresolved problem']
                packet = self.reasoner([QUESTION, HYPOTHESES, critiques]).run()
                self.assertIsNone(packet.experiment)

    def test_principal_can_abstain(self):
        selection = dict(SELECTION, hypothesis_id=None)
        packet = self.reasoner([QUESTION, HYPOTHESES, CRITIQUES, selection]).run()
        self.assertIsNone(packet.experiment)
        self.assertEqual(len(self.provider.calls), 4)

    def test_integrity_rejection_revision_and_contradictions_are_binding(self):
        for review, expected in ((dict(REVIEW, disposition='reject'), 'rejected_by_integrity'),
                                 (dict(REVIEW, disposition='revise'), 'revision_required'),
                                 (dict(REVIEW, evidence_boundary_issues=['leak']), 'revision_required')):
            packet = self.reasoner([QUESTION, HYPOTHESES, CRITIQUES, SELECTION, EXPERIMENT, review]).run()
            self.assertEqual(packet.status, expected)
            self.assertFalse(packet.to_dict()['execution_authorized'])

    def test_policy_and_source_context_reach_every_role(self):
        packet = self.reasoner().run()
        for call in self.provider.calls:
            self.assertIn('constitution', call['instructions'])
            self.assertIn('evidence policy', call['instructions'])
            self.assertIn('Cohervia test context', call['prompt'])
        self.assertEqual(len(packet.provenance['calls']), 6)
        source = next(x for x in packet.provenance['context_sources'] if x['path'] == 'README.md')
        self.assertEqual(source['sha256'], hashlib.sha256((self.repo/'README.md').read_bytes()).hexdigest())

    def test_source_snapshot_is_stable_during_run(self):
        reasoner = self.reasoner()
        original = self.provider.complete
        def mutate(**kwargs):
            (self.repo/'README.md').write_text('changed during call')
            return original(**kwargs)
        self.provider.complete = mutate
        reasoner.run()
        self.assertTrue(all('Cohervia test context' in x['prompt'] for x in self.provider.calls))
        self.assertTrue(all('changed during call' not in x['prompt'] for x in self.provider.calls))

    def test_required_policies_cannot_be_omitted_missing_or_truncated(self):
        self.config(approved_context_paths=['README.md'])
        snapshot = RepositoryContext(self.repo, self.root).snapshot()
        self.assertIn('evidence policy', snapshot.policies)
        self.config(max_context_characters=1)
        with self.assertRaises(ValueError):
            RepositoryContext(self.repo, self.root).snapshot()
        self.config(max_context_characters=10000)
        (self.repo/'docs/research/EVIDENCE_POLICY.md').unlink()
        with self.assertRaises(FileNotFoundError):
            self.reasoner().run()
        self.assertEqual(len(self.provider.calls), 0)

    def test_unreviewed_context_paths_denied(self):
        for path in ('holdout/answers.json', '/etc/passwd', '../outside', 'scientist/state/failures.jsonl'):
            with self.subTest(path=path):
                self.config(approved_context_paths=[path])
                with self.assertRaises(ValueError):
                    RepositoryContext(self.repo, self.root)

    def test_context_symlink_and_hardlink_denied(self):
        path = self.repo/'README.md'
        target = self.repo/'sealed.txt'
        target.write_text('must not ingest')
        path.unlink()
        path.symlink_to(target)
        with self.assertRaises(ValueError):
            self.reasoner().run()
        path.unlink()
        os.link(target, path)
        with self.assertRaises(ValueError):
            self.reasoner().run()

    def test_memory_symlink_denied(self):
        path = self.root/'state/failures.jsonl'
        path.unlink()
        path.symlink_to(self.repo/'README.md')
        with self.assertRaises(ValueError):
            ScientificMemory(self.root).relevant('margin')

    def test_budgets_are_validated_before_provider_calls(self):
        for field, values in (('memory_limit', [-1, 0, 21, True]), ('hypothesis_count', [0, 1, 9, True])):
            for value in values:
                with self.subTest(field=field, value=value):
                    with self.assertRaises(ValueError):
                        self.reasoner(**{field: value})
        for value in (-1, 0, 21):
            with self.assertRaises(ValueError):
                ScientificMemory(self.root).relevant('margin', value)
        for flag, value in (('--memory-limit','-1'), ('--memory-limit','21'), ('--hypothesis-count','1')):
            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                build_parser().parse_args(['reason','--model','operator-model',flag,value])

    def test_memory_provenance_and_ledger_cap(self):
        rows = [{'id':str(i), 'lesson':'margin slope failed', 'memory_type':'spoofed', 'relevance':999}
                for i in range(10)]
        path = self.root/'state/failures.jsonl'
        path.write_text(''.join(json.dumps(x)+'\n' for x in rows))
        memory = ScientificMemory(self.root)
        found = memory.relevant('margin slope', 2)
        self.assertEqual(len(found), 2)
        self.assertEqual(found[0]['memory_type'], 'failure')
        self.assertEqual(found[0]['relevance'], 2)
        self.assertEqual(found[0]['source_line'], 1)
        self.assertEqual(len(found[0]['record_sha256']), 64)
        self.assertEqual(len(memory.sources), 2)
        path.write_text(json.dumps({'evidence_class':'confirmatory','lesson':'margin'}))
        with self.assertRaises(ValueError):
            memory.relevant('margin')
        path.write_text(json.dumps({'lesson':'margin' * 4000}))
        with self.assertRaises(ValueError):
            memory.relevant('margin')

    def test_prior_mistakes_are_supplied_to_generator_and_critic(self):
        path = self.root/'state/failures.jsonl'
        path.write_text(json.dumps({'id':'negative-1', 'lesson':'margin slope failed under noise',
                                    'unresolved':['measurement artifact'], 'cause':None})+'\n')
        packet = self.reasoner().run()
        self.assertEqual(packet.relevant_memory[0]['id'], 'negative-1')
        for call in self.provider.calls[1:3]:
            self.assertIn('negative-1', call['prompt'])
            self.assertIn('measurement artifact', call['prompt'])
            self.assertIn('null', call['prompt'])

    def test_model_text_has_no_execution_or_permission_channel(self):
        marker = self.repo/'should-not-exist'
        question = dict(QUESTION, question=f"__import__('pathlib').Path('{marker}').touch()")
        packet = self.reasoner([question,HYPOTHESES,CRITIQUES,SELECTION,EXPERIMENT,REVIEW]).run()
        self.assertFalse(marker.exists())
        self.assertEqual(packet.question.question, question['question'])
        self.assertFalse(packet.to_dict()['execution_authorized'])

    def test_directory_symlink_and_nonregular_input_denied(self):
        state = self.root/'state'
        other = self.root/'other-state'
        state.rename(other)
        state.symlink_to(other, target_is_directory=True)
        with self.assertRaises(ValueError):
            ScientificMemory(self.root).relevant('margin')
        state.unlink()
        other.rename(state)
        path = self.repo/'README.md'
        path.unlink()
        os.mkfifo(path)
        with self.assertRaises(ValueError):
            self.reasoner().run()

    def test_no_memory_match_is_explicit_and_does_not_write_ledgers(self):
        before = {p.name:p.read_bytes() for p in (self.root/'state').iterdir()}
        packet = self.reasoner().run()
        self.assertEqual(packet.relevant_memory, [])
        self.assertEqual(packet.provenance['retrieval']['no_matches_means'], 'unknown_not_no_prior_failures')
        self.assertEqual(before, {p.name:p.read_bytes() for p in (self.root/'state').iterdir()})

    def test_model_json_rejects_ambiguous_or_unbounded_output(self):
        for text in ('prose {"x":1}', '{"x":1} trailing', '{"x":1,"x":2}', '{"x":NaN}',
                     '[{}]', '```python\n{}\n```', '{}{}', 'x'*100001):
            with self.subTest(text=text[:30]), self.assertRaises(ValueError):
                parse_json_object(text)

    def test_hypotheses_and_critic_must_be_complete_and_distinct(self):
        bad_hypotheses = copy.deepcopy(HYPOTHESES)
        bad_hypotheses['hypotheses'][1]['statement'] = bad_hypotheses['hypotheses'][0]['statement']
        with self.assertRaises(ValueError):
            self.reasoner([QUESTION,bad_hypotheses]).run()
        bad_critiques = copy.deepcopy(CRITIQUES)
        bad_critiques['critiques'][1]['hypothesis_id'] = 'H1'
        with self.assertRaises(ValueError):
            self.reasoner([QUESTION,HYPOTHESES,bad_critiques]).run()
        bad_hypotheses = copy.deepcopy(HYPOTHESES)
        bad_hypotheses['hypotheses'].append('ignored garbage')
        with self.assertRaises(ValueError):
            self.reasoner([QUESTION,bad_hypotheses]).run()

    def test_experiment_schema_fails_closed(self):
        for key, value in (('requires_holdout', True), ('requires_holdout', 0), ('authority_effect','grant'),
                           ('procedure',[]), ('failure_criteria',[' ']), ('controls', None)):
            with self.subTest(key=key), self.assertRaises(ValueError):
                ExperimentPlan.from_dict(dict(EXPERIMENT, **{key:value}))
        bad = dict(EXPERIMENT)
        del bad['stopping_conditions']
        with self.assertRaises(ValueError):
            ExperimentPlan.from_dict(bad)
        with self.assertRaises(ValueError):
            ExperimentPlan.from_dict(dict(EXPERIMENT, tool_call='execute'))
        with self.assertRaisesRegex(ValueError, 'wrong hypothesis'):
            self.reasoner([QUESTION,HYPOTHESES,CRITIQUES,SELECTION,dict(EXPERIMENT,hypothesis_id='H2')]).run()

    def test_packet_creation_is_exclusive_and_protected_paths_denied(self):
        packet = self.reasoner().run()
        path = write_packet(packet, scientist_root=self.root)
        original = path.read_bytes()
        with self.assertRaises(FileExistsError):
            write_packet(packet, scientist_root=self.root)
        self.assertEqual(path.read_bytes(), original)
        for output in (self.root/'SCIENTIFIC_CONSTITUTION.md', self.root/'config/new.json',
                       self.repo/'external.json'):
            with self.subTest(output=output), self.assertRaises(ValueError):
                write_packet(packet, output, scientist_root=self.root)
        link = self.root/'runs/link.json'
        link.symlink_to(self.root/'SCIENTIFIC_CONSTITUTION.md')
        with self.assertRaises(ValueError):
            write_packet(packet, link, scientist_root=self.root)

    def test_concurrent_writers_cannot_overwrite(self):
        packet = self.reasoner().run()
        def attempt(_):
            try:
                write_packet(packet, scientist_root=self.root)
                return True
            except FileExistsError:
                return False
        with ThreadPoolExecutor(max_workers=2) as pool:
            self.assertEqual(sorted(pool.map(attempt, range(2))), [False,True])
        other = self.reasoner().run()
        self.assertNotEqual(other.run_id, packet.run_id)

    def test_provider_exception_stops_pipeline(self):
        reasoner = self.reasoner()
        self.provider.complete = MagicMock(side_effect=TimeoutError('timed out'))
        with self.assertRaises(TimeoutError):
            reasoner.run()
        self.assertFalse((self.root/'runs').exists())


class ProviderTests(unittest.TestCase):
    def test_openai_contract_without_network_or_secrets(self):
        client = MagicMock()
        client.responses.create.return_value = SimpleNamespace(status='completed', output_text='{}', output=[])
        factory = MagicMock(return_value=client)
        with patch.dict('sys.modules', {'openai':SimpleNamespace(OpenAI=factory)}):
            provider = OpenAIProvider(model='operator-model', api_key='test-placeholder')
            self.assertNotIn('test-placeholder', repr(provider))
            self.assertEqual(provider.complete(instructions='rules',prompt='data'), '{}')
            factory.assert_called_once_with(api_key='test-placeholder',base_url='https://api.openai.com/v1',timeout=60.0,max_retries=0)
            args = client.responses.create.call_args.kwargs
            self.assertEqual(args['tools'], [])
            self.assertFalse(args['store'])
            self.assertEqual(args['max_output_tokens'], 8000)
            for response in (SimpleNamespace(status='incomplete'), SimpleNamespace(status='completed',output_text='',output=[]),
                             SimpleNamespace(status='completed',output_text='{}',output=[SimpleNamespace(type='function_call')])):
                client.responses.create.return_value = response
                with self.assertRaises(RuntimeError):
                    provider.complete(instructions='rules', prompt='data')
