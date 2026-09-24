"""Fixed development qualification probes, never experiments or scientific evidence."""
from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from .json_utils import parse_json_object
from .memory import ScientificMemory
from .provider import OpenAIProvider, ScriptedProvider, ProviderResponseError
from .reasoning import ScientificReasoner, write_artifact
from .safe_io import read_local

DIMENSIONS = (
    'falsifiability', 'memory_use', 'hypothesis_diversity', 'critic_effectiveness',
    'evidence_boundary_compliance', 'experimental_discriminability', 'claim_conservatism',
)
CASE_IDS = tuple(f'Q{i:02}' for i in range(1, 8))
BASELINE = 'b62a9d4d93d98f39be938970d2ed1493d5043253'
SUITE_SHA256 = 'c1be656cd4b46c5d15489b70589cf9bf1b3ee30b9ca14aca75f3d4dc1871e8f5'
RUBRIC_SHA256 = '004050cfd3db1ad5e447beeb2b8a7cff9b1330872cd442ab223d8f306f71f943'


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encode(value) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False).encode()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_protocol(root: Path):
    suite_bytes = read_local(root, 'qualification/suite.json', max_bytes=64000)
    rubric_bytes = read_local(root, 'qualification/rubric.json', max_bytes=32000)
    if digest(suite_bytes) != SUITE_SHA256 or digest(rubric_bytes) != RUBRIC_SHA256:
        raise ValueError('qualification protocol differs from the reviewed fixed snapshot')
    suite = parse_json_object(suite_bytes.decode())
    rubric = parse_json_object(rubric_bytes.decode())
    if (suite.get('schema_version') != 1 or suite.get('evidence_status') != 'instrumentation_only'
            or suite.get('suite_id') != 'cohervia-reasoning-qualification-v0.2.1'
            or not isinstance(suite.get('cases'), list)
            or not all(isinstance(c, dict) for c in suite['cases'])
            or [c.get('id') for c in suite['cases']] != list(CASE_IDS)):
        raise ValueError('qualification requires the fixed ordered seven-case suite')
    for case in suite['cases']:
        if set(case) != {'id', 'target', 'question', 'review_focus', 'memory_kind', 'memory'}:
            raise ValueError('unexpected case fields')
        for field in ('target', 'question', 'review_focus'):
            if not isinstance(case[field], str) or not 1 <= len(case[field].strip()) <= 4000:
                raise ValueError('invalid case text')
        if (case['memory_kind'] not in {'failure', 'anomaly'}
                or not isinstance(case['memory'], list) or len(case['memory']) != 1
                or not isinstance(case['memory'][0], dict)):
            raise ValueError('each case requires one controlled memory fixture')
        record = case['memory'][0]
        if (record.get('id') != f"QUAL-{case['id']}-M1"
                or record.get('evidence_class') != 'instrumentation'
                or record.get('origin') != 'synthetic_qualification_fixture_not_research_evidence'):
            raise ValueError('qualification memory must remain synthetic instrumentation')
    if (rubric.get('rating_authority') != 'human_only'
            or rubric.get('aggregation') != 'no_scalar_score_no_automatic_qualification'
            or set(rubric.get('dimensions', {})) != set(DIMENSIONS)):
        raise ValueError('qualification requires all seven human-reviewed dimensions')
    for dimension in rubric['dimensions'].values():
        if set(dimension.get('anchors', {})) != {'0', '1', '2', '3'}:
            raise ValueError('rubric must preserve four anchored ratings')
    return suite, rubric, {'suite_sha256': digest(suite_bytes), 'rubric_sha256': digest(rubric_bytes),
                           'suite_text': suite_bytes.decode(), 'rubric_text': rubric_bytes.decode()}


class FixtureMemory(ScientificMemory):
    """Use the engine's actual lexical retrieval with isolated, labeled fixture bytes."""
    def __init__(self, root: Path, case: dict):
        super().__init__(root)
        self.case = copy.deepcopy(case)

    def _read_sources(self):
        data = b'\n'.join(encode(r) for r in self.case['memory']) + b'\n'
        yield self.case['memory_kind'], f"qualification/suite.json#{self.case['id']}/memory", data


class Archive:
    def __init__(self, root: Path):
        self.root = Path(root).absolute()
        self.run_id = 'qualification-' + uuid4().hex
        self.artifacts = []

    def write(self, suffix: str, payload: dict):
        path = self.root / 'runs' / f'{self.run_id}-{suffix}.json'
        write_artifact(payload, path, scientist_root=self.root)
        content = read_local(self.root, 'runs/' + path.name, max_bytes=8_000_000)
        entry = {'file': path.name, 'sha256': digest(content)}
        self.artifacts.append(entry)
        return entry


def output_record(text: str) -> dict:
    raw = text.encode('utf-8')
    return {'sha256': digest(raw), 'byte_length': len(raw),
            'raw_text': text if len(raw) <= 1_000_000 else None,
            'complete': len(raw) <= 1_000_000}


class RecordingProvider:
    """Archive each request before calling; archive returned text before parsing."""
    def __init__(self, provider, archive: Archive, case_id: str):
        self.provider = provider
        self.archive = archive
        self.case_id = case_id
        self.calls = []
        self.model = getattr(provider, 'model', 'scripted-fixture')
        self.reasoning_effort = getattr(provider, 'reasoning_effort', None)

    def complete(self, *, instructions: str, prompt: str) -> str:
        if len(self.calls) >= 6:
            raise ValueError('qualification call budget exhausted')
        index = len(self.calls) + 1
        request = {'instructions': instructions, 'prompt': prompt, 'created_at': now(),
                   'case_id': self.case_id, 'call_index': index,
                   'provider_type': type(self.provider).__name__, 'model': self.model,
                   'reasoning_effort': self.reasoning_effort}
        saved_request = self.archive.write(f'{self.case_id}-call-{index}-request', request)
        call = {'request': saved_request, 'response': None}
        self.calls.append(call)
        try:
            text = self.provider.complete(instructions=instructions, prompt=prompt)
        except Exception as exc:
            # Exception messages can contain credentials or transport details.
            error = {'status': 'provider_error', 'error_type': type(exc).__name__, 'created_at': now()}
            if isinstance(exc, ProviderResponseError):
                error['response_status'] = exc.response_status
                if exc.output_text is not None:
                    error.update(output_record(exc.output_text))
            call['response'] = self.archive.write(f'{self.case_id}-call-{index}-response', error)
            raise RuntimeError("provider call failed; see archived error type") from None
        if not isinstance(text, str):
            call['response'] = self.archive.write(f'{self.case_id}-call-{index}-response',
                {'status': 'invalid_output_type', 'created_at': now()})
            raise ValueError('provider output must be text')
        response = {'status': 'returned', 'created_at': now(), **output_record(text)}
        if not response['complete']:
            response['status'] = 'oversized_output_not_preserved'
        call['response'] = self.archive.write(f'{self.case_id}-call-{index}-response', response)
        if not response['complete']:
            raise ValueError('provider output exceeded archive budget')
        return text


def evaluate_packet(case: dict, packet: dict | None):
    """Observable contract checks are deliberately not semantic quality scores."""
    checks = []

    def check(name, dimension, condition, refs):
        checks.append({'id': name, 'dimension': dimension,
                       'result': 'not_assessed' if condition is None else ('pass' if condition else 'fail'),
                       'basis': 'deterministic_structural_check_not_scientific_quality', 'references': refs})

    if packet is None:
        for dimension in DIMENSIONS:
            check('packet_unavailable', dimension, None, [])
    else:
        hs = packet['hypotheses']
        memory_id = case['memory'][0]['id']
        retrieved = any(x.get('id') == memory_id for x in packet['relevant_memory'])
        cited = any(memory_id in x['prior_failures_considered'] for x in hs)
        check('explicit_falsifiers', 'falsifiability',
              bool(hs) and all(x['prediction'].strip() and x['falsification_condition'].strip() for x in hs),
              ['hypotheses[].prediction', 'hypotheses[].falsification_condition'])
        check('fixture_retrieved', 'memory_use', retrieved, ['relevant_memory', 'provenance.retrieval'])
        check('fixture_cited_by_id', 'memory_use', cited, ['hypotheses[].prior_failures_considered'])
        signatures = {tuple(' '.join(h[k].casefold().split()) for k in ('mechanism', 'prediction')) for h in hs}
        check('distinct_mechanism_prediction_text', 'hypothesis_diversity', len(signatures) == len(hs) and len(hs) >= 2,
              ['hypotheses[].mechanism', 'hypotheses[].prediction'])
        critiques = packet['critiques']
        eligible = {c['hypothesis_id'] for c in critiques if c['recommendation'] == 'advance_exploratory'
                    and not c['fatal_flaws'] and not c['required_revisions'] and not c['leakage_risks']}
        chosen = packet['selection']['hypothesis_id']
        check('critic_coverage_and_gate', 'critic_effectiveness',
              sorted(c['hypothesis_id'] for c in critiques) == sorted(h['id'] for h in hs)
              and (chosen is None or chosen in eligible)
              and (chosen is not None or packet['experiment'] is None), ['critiques', 'selection', 'experiment'])
        plan = packet['experiment']
        check('exploratory_no_authority', 'evidence_boundary_compliance',
              packet.get('execution_authorized') is False and packet.get('evidence_status') == 'not_evidence'
              and (plan is None or (plan['requires_holdout'] is False and plan['authority_effect'] == 'none'
                                    and plan['evidence_class'] == 'exploratory')),
              ['evidence_status', 'execution_authorized', 'experiment'])
        check('comparison_fields_present', 'experimental_discriminability',
              None if plan is None else all(plan[k] for k in ('controls', 'baselines', 'independent_variables',
                    'dependent_variables', 'analysis_plan', 'failure_criteria', 'stopping_conditions')),
              ['experiment'])
        check('conservative_envelope', 'claim_conservatism',
              packet.get('epistemic_state') == 'inferred' and packet.get('evidence_status') == 'not_evidence',
              ['epistemic_state', 'evidence_status'])
    return {'evaluator_id': 'deterministic-structural-v1', 'checks': checks, 'quality_ratings': {d: {'rating': None, 'state': 'unknown',
            'reviewer': None, 'reviewed_at': None, 'rationale': None, 'artifact_references': []} for d in DIMENSIONS},
            'qualification_decision': 'pending_human_review', 'scientific_evidence': False}


def scripted_responses(case: dict):
    """Canned plumbing fixture, intentionally not a model-quality benchmark result."""
    question = {'question': case['question'], 'importance': 'Compare competing explanations.',
                'why_now': 'Fixed qualification probe, not new evidence.', 'theory_targets': [case['target']],
                'prior_evidence': ['Synthetic qualification memory only; not an empirical finding.'],
                'unknowns': ['Incremental information and generalization remain unknown.']}
    hypotheses = []
    for index, mechanism in enumerate(('incremental signal', 'no incremental effect', 'measurement noise', 'confounding'), 1):
        hypotheses.append({'id': f'H{index}', 'statement': f"{case['target']}: {mechanism} explains the observation.",
            'mechanism': mechanism, 'prediction': f'Controlled comparisons distinguish {mechanism} from alternatives.',
            'falsification_condition': f'Reject {mechanism} if its predicted contrast is absent in the defined regime.',
            'novelty_rationale': 'No novelty claim; scripted test fixture.', 'theory_targets': [case['target']],
            'prior_failures_considered': [case['memory'][0]['id']]})
    critiques = [{'hypothesis_id': f'H{i}', 'recommendation': 'advance_exploratory' if i == 1 else 'reject',
        'fatal_flaws': [] if i == 1 else ['Scripted rejection probe; not a real scientific judgment.'],
        'confounds': ['Review the case-specific fixture lesson.'], 'leakage_risks': [],
        'alternative_explanations': ['Null effect and measurement artifacts.'], 'required_revisions': []}
        for i in range(1, 5)]
    selection = {'hypothesis_id': 'H1', 'rationale': 'Scripted selection for plumbing validation only.',
                 'revisions_applied': [], 'residual_uncertainties': ['All scientific quality is unassessed.']}
    plan = {'title': 'Scripted exploratory design fixture', 'hypothesis_id': 'H1',
        'purpose': case['question'], 'environment': 'bounded synthetic analytical setting',
        'independent_variables': [case['target']], 'dependent_variables': ['independently specified task outcome'],
        'controls': [case['memory'][0]['lesson']], 'baselines': ['null effect', 'simpler baseline'],
        'procedure': ['Specify independent outcomes before comparing controlled synthetic conditions.'],
        'analysis_plan': ['Compare rival predictions under equal budgets.'],
        'failure_criteria': ['No distinguishable improvement over the simpler baseline.'],
        'stopping_conditions': ['Stop at the predeclared development budget.'],
        'provenance_requirements': ['Retain source, configuration, and output hashes.'],
        'evidence_class': 'exploratory', 'requires_holdout': False, 'authority_effect': 'none'}
    review = {'disposition': 'acceptable_exploratory', 'unsupported_claims': [], 'evidence_boundary_issues': [],
              'unresolved_concerns': ['Scripted fixture; semantic quality is not assessed.'], 'required_changes': []}
    return [json.dumps(x) for x in (question, {'hypotheses': hypotheses}, {'critiques': critiques}, selection, plan, review)]


def run_qualification(scientist_root: Path, *, model: str | None = None, provider_factory=None):
    """One fixed pass; no retries, experiment execution, ranking, or promotion."""
    root = Path(scientist_root).absolute()
    suite, rubric, protocol = load_protocol(root)
    mode = 'injected_test' if provider_factory is not None else ('live_candidate_reasoning' if model else 'scripted_instrumentation')
    if provider_factory is not None and model is not None:
        raise ValueError('injected test provider cannot masquerade as live model evaluation')
    archive = Archive(root)
    implementation = []
    for name in ('qualification.py', 'reasoning.py', 'memory.py', 'context.py', 'schemas.py',
                 'provider.py', 'prompts.py', 'safe_io.py', 'json_utils.py', '__init__.py'):
        data = read_local(Path(__file__).parent, name, max_bytes=256000)
        implementation.append({'module': name, 'sha256': digest(data)})
    start = archive.write('start', {'run_id': archive.run_id, 'created_at': now(), 'mode': mode,
        'protocol': protocol, 'implementation': implementation, 'case_order': list(CASE_IDS),
        'declared_development_baseline': BASELINE, 'actual_source_commit': {'state': 'unknown', 'value': None},
        'model': model, 'scientific_evidence': False, 'execution_authorized': False,
        'budget': {'cases': 7, 'calls_per_case': 6, 'automatic_retries': 0}})
    results = []
    for case in suite['cases']:
        recorder = None
        packet = None
        error_type = None
        try:
            underlying = (provider_factory(copy.deepcopy(case)) if provider_factory is not None
                          else OpenAIProvider(model=model) if model else ScriptedProvider(scripted_responses(case)))
            recorder = RecordingProvider(underlying, archive, case['id'])
            reasoner = ScientificReasoner(provider=recorder, repo_root=root.parent, scientist_root=root)
            reasoner.memory = FixtureMemory(root, case)
            packet = reasoner.run(question_override=case['question']).to_dict()
        except Exception as exc:
            error_type = type(exc).__name__
        result = {'case_id': case['id'], 'case': case, 'packet': packet, 'error_type': error_type,
                  'pipeline_status': 'complete' if packet is not None else 'error',
                  'calls': recorder.calls if recorder else [], 'evaluation': evaluate_packet(case, packet)}
        saved = archive.write(f"{case['id']}-result", result)
        results.append({'case_id': case['id'], 'pipeline_status': result['pipeline_status'], 'artifact': saved,
                        'checks': result['evaluation']['checks']})
    report = {'run_id': archive.run_id, 'completed_at': now(), 'mode': mode, 'start': start,
              'suite_id': suite['suite_id'], 'rubric_id': rubric['rubric_id'],
              'results': results, 'artifacts': list(archive.artifacts),
              'qualification_decision': 'pending_human_review', 'scientific_evidence': False,
              'quality_ratings': 'unassessed', 'execution_authorized': False,
              'pipeline_error_count': sum(x['pipeline_status'] == 'error' for x in results),
              'structural_failure_count': sum(c['result'] == 'fail' for x in results for c in x['checks'])}
    summary = archive.write('summary', report)
    return root / 'runs' / summary['file'], report


def verify_archive(scientist_root: Path, summary_name: str):
    """Check saved byte integrity and recompute structural checks; never promote ratings."""
    import re
    root = Path(scientist_root).absolute()
    if not re.fullmatch(r'qualification-[0-9a-f]{32}-summary\.json', summary_name):
        raise ValueError('expected a qualification summary filename, not an arbitrary path')
    report = parse_json_object(read_local(root, 'runs/' + summary_name, max_bytes=1_000_000).decode())
    run_id = summary_name.removesuffix('-summary.json')
    if report.get('run_id') != run_id or report.get('scientific_evidence') is not False:
        raise ValueError('invalid qualification identity or evidence boundary')
    entries = report['artifacts']
    if len(entries) > 100 or len({e['file'] for e in entries}) != len(entries):
        raise ValueError('invalid artifact manifest')
    loaded = {}
    for entry in entries:
        name = entry['file']
        if not re.fullmatch(re.escape(run_id) + r'-[A-Za-z0-9-]+\.json', name):
            raise ValueError('artifact reference escapes its qualification run')
        data = read_local(root, 'runs/' + name, max_bytes=8_000_000)
        if digest(data) != entry['sha256']:
            raise ValueError('artifact hash mismatch')
        # Raw-output archives can be larger than normal model JSON messages.
        loaded[name] = json.loads(data)
    by_name = {entry['file']: entry for entry in entries}

    def artifact(ref):
        if by_name.get(ref['file']) != ref:
            raise ValueError('artifact reference does not match the manifest')
        return loaded[ref['file']]

    start = artifact(report['start'])
    if (start.get('run_id') != run_id
            or start.get('scientific_evidence') is not False
            or start.get('execution_authorized') is not False):
        raise ValueError('archived start record violates qualification boundaries')
    if report.get('mode') != start.get('mode'):
        raise ValueError('summary mode does not match archived start record')

    protocol = start['protocol']
    for key, expected_hash in (('suite', SUITE_SHA256), ('rubric', RUBRIC_SHA256)):
        if digest(protocol[key + '_text'].encode()) != protocol[key + '_sha256']:
            raise ValueError('protocol snapshot hash mismatch')
        if protocol[key + '_sha256'] != expected_hash:
            raise ValueError('archived protocol is not the fixed reviewed snapshot')

    suite_snapshot = json.loads(protocol['suite_text'])
    rubric_snapshot = json.loads(protocol['rubric_text'])
    if (report.get('suite_id') != suite_snapshot.get('suite_id')
            or report.get('rubric_id') != rubric_snapshot.get('rubric_id')):
        raise ValueError('summary protocol identity does not match archived protocol')
    if (start.get('case_order') != list(CASE_IDS)
            or start.get('budget') != {'cases': 7, 'calls_per_case': 6, 'automatic_retries': 0}):
        raise ValueError('archived start record has unexpected case order or budget')
    if (start.get('mode') == 'live_candidate_reasoning' and not start.get('model')):
        raise ValueError('live qualification start record requires an explicit model')
    if (start.get('mode') == 'scripted_instrumentation' and start.get('model') is not None):
        raise ValueError('scripted qualification start record must not declare a live model')

    cases = suite_snapshot['cases']
    if [r['case_id'] for r in report['results']] != list(CASE_IDS):
        raise ValueError('qualification report must retain every case, including failures')
    if [case['id'] for case in cases] != list(CASE_IDS):
        raise ValueError('protocol snapshot must retain the ordered cases')
    error_count = 0
    fail_count = 0
    for case, row in zip(cases, report['results'], strict=True):
        result = artifact(row['artifact'])
        if result['case'] != case or result['evaluation'] != evaluate_packet(case, result['packet']):
            raise ValueError('saved case or structural evaluation mismatch')
        if result['evaluation']['checks'] != row['checks']:
            raise ValueError('summary check mismatch')
        status = 'complete' if result['packet'] is not None else 'error'
        if result['pipeline_status'] != status or row['pipeline_status'] != status:
            raise ValueError('pipeline status mismatch')
        error_count += status == 'error'
        fail_count += sum(c['result'] == 'fail' for c in result['evaluation']['checks'])
        if result['packet'] is not None:
            traces = result['packet']['provenance']['calls']
            if len(traces) != len(result['calls']):
                raise ValueError('packet call trace is incomplete')
            for trace, call in zip(traces, result['calls'], strict=True):
                request = artifact(call['request'])
                response = artifact(call['response'])
                if (trace['instructions_sha256'] != digest(request['instructions'].encode())
                        or trace['prompt_sha256'] != digest(request['prompt'].encode())
                        or trace['response_sha256'] != response['sha256']):
                    raise ValueError('packet provenance does not match archived calls')
        for call in result['calls']:
            request = artifact(call['request'])
            response = artifact(call['response'])
            if request['case_id'] != case['id']:
                raise ValueError('call belongs to a different case')
            if response.get('complete') and digest(response['raw_text'].encode()) != response['sha256']:
                raise ValueError('raw response hash mismatch')
    if (report['pipeline_error_count'] != error_count or report['structural_failure_count'] != fail_count
            or report['qualification_decision'] != 'pending_human_review'
            or report['quality_ratings'] != 'unassessed' or report['execution_authorized'] is not False):
        raise ValueError('summary counts or qualification boundaries mismatch')
    return {'verified_artifacts': len(entries), 'cases': len(cases),
            'scientific_evidence': False, 'qualification_decision': 'pending_human_review'}
