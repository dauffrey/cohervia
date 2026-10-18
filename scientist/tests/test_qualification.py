import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from cohervia_scientist.cli import build_parser, cmd_qualify
from cohervia_scientist.provider import ScriptedProvider
from cohervia_scientist.qualification import (
    Archive, CASE_IDS, DIMENSIONS, FixtureMemory, RecordingProvider, evaluate_packet,
    load_protocol, run_qualification, scripted_responses, verify_archive,
)
from cohervia_scientist.reasoning import ScientificReasoner
import test_reasoning


class QualificationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo, self.root = test_reasoning.ReasonerTests()._repo(self.tmp.name)
        (self.root/'qualification').mkdir()
        source = Path(__file__).resolve().parents[1]/'qualification'
        for name in ('suite.json','rubric.json'):
            (self.root/'qualification'/name).write_bytes((source/name).read_bytes())
        self.suite, self.rubric, _ = load_protocol(self.root)

    def packet(self, case=None):
        case = case or self.suite['cases'][0]
        engine = ScientificReasoner(provider=ScriptedProvider(scripted_responses(case)),
                                    repo_root=self.repo, scientist_root=self.root)
        engine.memory = FixtureMemory(self.root, case)
        return engine.run(question_override=case['question']).to_dict()

    def test_fixed_protocol_and_seven_human_dimensions(self):
        self.assertEqual([x['id'] for x in self.suite['cases']], list(CASE_IDS))
        self.assertEqual(set(self.rubric['dimensions']), set(DIMENSIONS))
        self.assertEqual(self.rubric['rating_authority'], 'human_only')
        path = self.root/'qualification/suite.json'
        altered = copy.deepcopy(self.suite)
        altered['cases'].pop()
        path.write_text(json.dumps(altered))
        with self.assertRaises(ValueError):
            load_protocol(self.root)

    def test_full_scripted_run_preserves_requests_outputs_and_unknown_scores(self):
        before = {p.name:p.read_bytes() for p in (self.root/'state').iterdir()}
        path, report = run_qualification(self.root)
        self.assertEqual(report['mode'], 'scripted_instrumentation')
        self.assertEqual(report['pipeline_error_count'], 0)
        self.assertEqual(report['structural_failure_count'], 0)
        self.assertEqual(report['qualification_decision'], 'pending_human_review')
        self.assertFalse(report['scientific_evidence'])
        self.assertFalse(report['execution_authorized'])
        self.assertEqual(len(report['results']), 7)
        verified = verify_archive(self.root, path.name)
        self.assertEqual(verified['verified_artifacts'], 92)  # start + 7 * (12 calls + result)
        for case, row in zip(self.suite['cases'],report['results']):
            result = json.loads((self.root/'runs'/row['artifact']['file']).read_text())
            for value in result['evaluation']['quality_ratings'].values():
                self.assertIsNone(value['rating'])
                self.assertEqual(value['state'], 'unknown')
            calls = result['calls']
            self.assertEqual(len(calls), 6)
            for expected, call in zip(scripted_responses(case),calls):
                response = json.loads((self.root/'runs'/call['response']['file']).read_text())
                self.assertEqual(response['raw_text'], expected)
                self.assertTrue(response['complete'])
        self.assertEqual(before, {p.name:p.read_bytes() for p in (self.root/'state').iterdir()})

    def test_memory_fixture_uses_actual_lexical_retrieval_without_ledger_pollution(self):
        memory = FixtureMemory(self.root, self.suite['cases'][0])
        self.assertEqual(memory.relevant('margin slope')[0]['id'], 'QUAL-Q01-M1')
        self.assertEqual(memory.relevant('completelyunrelatedtoken'), [])
        self.assertEqual((self.root/'state/failures.jsonl').read_bytes(), b'')

    def test_missing_memory_citation_is_flagged_but_not_called_quality_score(self):
        packet = self.packet()
        for h in packet['hypotheses']:
            h['prior_failures_considered'] = []
        result = evaluate_packet(self.suite['cases'][0], packet)
        check = next(c for c in result['checks'] if c['id']=='fixture_cited_by_id')
        self.assertEqual(check['result'], 'fail')
        self.assertIsNone(result['quality_ratings']['memory_use']['rating'])

    def test_structural_checks_detect_known_mutations(self):
        mutations = {
            'distinct_mechanism_prediction_text': lambda p: p['hypotheses'].__setitem__(1,dict(p['hypotheses'][0],id='H2')),
            'critic_coverage_and_gate': lambda p: p['critiques'][0].update(recommendation='reject'),
            'exploratory_no_authority': lambda p: p['experiment'].update(requires_holdout=True),
            'comparison_fields_present': lambda p: p['experiment'].update(baselines=[]),
            'conservative_envelope': lambda p: p.update(epistemic_state='observed'),
            'explicit_falsifiers': lambda p: p['hypotheses'][0].update(falsification_condition=''),
        }
        original = self.packet()
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                packet = copy.deepcopy(original)
                mutate(packet)
                checks = evaluate_packet(self.suite['cases'][0],packet)['checks']
                self.assertEqual(next(c for c in checks if c['id']==name)['result'],'fail')

    def test_citation_parroting_cannot_produce_a_scientific_quality_pass(self):
        packet = self.packet()
        for h in packet['hypotheses']:
            h['statement'] = 'This proves universal AI safety.'
        result = evaluate_packet(self.suite['cases'][0],packet)
        # Intentionally expose semantic blind spots rather than claiming a keyword detector is science.
        self.assertEqual(result['qualification_decision'], 'pending_human_review')
        self.assertEqual(result['quality_ratings']['claim_conservatism']['state'], 'unknown')

    def test_all_rejected_packets_do_not_penalize_missing_experiment_as_zero(self):
        def factory(case):
            responses = scripted_responses(case)
            critic = json.loads(responses[2])
            for c in critic['critiques']:
                c['recommendation']='reject'
            responses[2] = json.dumps(critic)
            return ScriptedProvider(responses[:3])
        path, report = run_qualification(self.root, provider_factory=factory)
        verify_archive(self.root,path.name)
        for row in report['results']:
            result=json.loads((self.root/'runs'/row['artifact']['file']).read_text())
            self.assertEqual(len(result['calls']),3)
            self.assertEqual(result['packet']['status'],'blocked_by_critic')
            check=next(c for c in row['checks'] if c['dimension']=='experimental_discriminability')
            self.assertEqual(check['result'],'not_assessed')

    def test_malformed_outputs_are_preserved_and_all_cases_remain_in_denominator(self):
        path, report = run_qualification(self.root,provider_factory=lambda case:ScriptedProvider(['not json']))
        self.assertEqual(report['pipeline_error_count'],7)
        self.assertEqual(len(report['results']),7)
        verify_archive(self.root,path.name)
        result=json.loads((self.root/'runs'/report['results'][0]['artifact']['file']).read_text())
        response=json.loads((self.root/'runs'/result['calls'][0]['response']['file']).read_text())
        self.assertEqual(response['raw_text'],'not json')
        self.assertTrue(all(c['result']=='not_assessed' for c in result['evaluation']['checks']))

    def test_provider_error_is_sanitized_and_archived(self):
        class FailureProvider:
            def complete(self,**kwargs):
                raise Exception('secret should never be copied')
        path, report = run_qualification(self.root,provider_factory=lambda case:FailureProvider())
        self.assertEqual(report['pipeline_error_count'],7)
        verify_archive(self.root,path.name)
        for artifact in report['artifacts']:
            self.assertNotIn('secret should never be copied',(self.root/'runs'/artifact['file']).read_text())

    def test_oversized_output_is_explicitly_incomplete_and_stops(self):
        recorder=RecordingProvider(ScriptedProvider(['x'*1_000_001]),Archive(self.root),'Q01')
        with self.assertRaises(ValueError):
            recorder.complete(instructions='rules',prompt='data')
        response=json.loads((self.root/'runs'/recorder.calls[0]['response']['file']).read_text())
        self.assertFalse(response['complete'])
        self.assertIsNone(response['raw_text'])
        self.assertEqual(response['byte_length'],1_000_001)

    def test_partial_provider_response_is_preserved_without_becoming_a_packet(self):
        from cohervia_scientist.provider import ProviderResponseError
        class PartialProvider:
            def complete(self, **kwargs):
                raise ProviderResponseError('incomplete', output_text='{"question":', response_status='incomplete')
        path, report = run_qualification(self.root, provider_factory=lambda case:PartialProvider())
        self.assertEqual(report['pipeline_error_count'], 7)
        verify_archive(self.root,path.name)
        result=json.loads((self.root/'runs'/report['results'][0]['artifact']['file']).read_text())
        response=json.loads((self.root/'runs'/result['calls'][0]['response']['file']).read_text())
        self.assertEqual(response['raw_text'], '{"question":')
        self.assertEqual(response['response_status'], 'incomplete')
        self.assertIsNone(result['packet'])

    def test_archive_recomputes_counts_instead_of_trusting_summary(self):
        path,_=run_qualification(self.root)
        report=json.loads(path.read_text())
        report['pipeline_error_count']=99
        path.write_text(json.dumps(report))
        with self.assertRaisesRegex(ValueError,'summary counts'):
            verify_archive(self.root,path.name)

    def test_archive_binds_summary_mode_and_protocol_identity(self):
        mutations = (
            ('mode', 'live_candidate_reasoning', 'summary mode'),
            ('suite_id', 'forged-suite', 'summary protocol identity'),
            ('rubric_id', 'forged-rubric', 'summary protocol identity'),
        )
        for field, value, message in mutations:
            with self.subTest(field=field):
                path, _ = run_qualification(self.root)
                report = json.loads(path.read_text())
                report[field] = value
                path.write_text(json.dumps(report))
                with self.assertRaisesRegex(ValueError, message):
                    verify_archive(self.root, path.name)

    def test_archive_detects_tampering_and_path_injection(self):
        path, report = run_qualification(self.root)
        first=self.root/'runs'/report['artifacts'][1]['file']
        first.write_text('{}')
        with self.assertRaisesRegex(ValueError,'hash mismatch'):
            verify_archive(self.root,path.name)
        for name in ('../SCIENTIFIC_CONSTITUTION.md','/tmp/a.json'):
            with self.assertRaises(ValueError):
                verify_archive(self.root,name)

    def test_rubric_and_review_focus_are_not_passed_to_live_role_prompts(self):
        class Capture(ScriptedProvider):
            def complete(inner, **kwargs):
                self.assertNotIn(self.suite['cases'][0]['review_focus'],kwargs['prompt'])
                self.assertNotIn('rating_authority',kwargs['prompt'])
                return super(Capture,inner).complete(**kwargs)
        run_qualification(self.root,provider_factory=lambda case:Capture(scripted_responses(case)))

    def test_repeated_runs_are_separate_and_do_not_overwrite(self):
        one,_=run_qualification(self.root)
        before=one.read_bytes()
        two,_=run_qualification(self.root)
        self.assertNotEqual(one,two)
        self.assertEqual(one.read_bytes(),before)

    def test_cli_live_calls_require_explicit_provider_and_model(self):
        parser=build_parser()
        args=parser.parse_args(['--root',str(self.root),'qualify','--provider','openai'])
        with self.assertRaises(ValueError),patch('cohervia_scientist.qualification.OpenAIProvider') as provider:
            cmd_qualify(args)
        provider.assert_not_called()
        args=parser.parse_args(['--root',str(self.root),'qualify','--model','accidental-model'])
        with self.assertRaises(ValueError):
            cmd_qualify(args)
        with self.assertRaises(ValueError):
            run_qualification(self.root,model='m',provider_factory=lambda case:None)

    def test_checked_in_archive_preserves_replayable_instrumentation(self):
        import lzma
        source=Path(__file__).resolve().parents[1]/'qualification/results/scripted-instrumentation.json.xz'
        bundle=json.loads(lzma.decompress(source.read_bytes()))
        self.assertEqual(bundle['format'],'cohervia-qualification-archive-v1')
        runs=self.root/'runs'
        runs.mkdir()
        for name,content in bundle['files'].items():
            self.assertEqual(Path(name).name,name)
            (runs/name).write_text(content)
        result=verify_archive(self.root,bundle['summary'])
        self.assertEqual(result['cases'],7)
        self.assertFalse(result['scientific_evidence'])

    def test_summary_cannot_discard_failed_cases(self):
        path,_=run_qualification(self.root)
        report=json.loads(path.read_text())
        report['results'].pop()
        path.write_text(json.dumps(report))
        with self.assertRaisesRegex(ValueError,'every case'):
            verify_archive(self.root,path.name)


if __name__=='__main__':
    unittest.main()
