"""In-memory verification of complete scripted apparatus archives.

Hashes detect inconsistency relative to the retained archive, not coordinated
rewriting, authenticity, historical custody, or scientific validity. No file or
holdout reader is exposed here. Partial/paused archives are not verified as complete.
"""
from __future__ import annotations
from typing import Any, Mapping
from .audit import AppendOnlyAuditLog
from .canonical import hash_object
from .models import Partition, TrialConfig


def verify_trial_archive(archive: Mapping[str, Any]) -> dict[str, object]:
    try:
        return _verify(archive)
    except (KeyError, TypeError, AttributeError) as error:
        raise ValueError("malformed apparatus archive") from error


def _verify(archive: Mapping[str, Any]) -> dict[str, object]:
    metadata = archive['metadata']
    records = metadata['audit_records']
    if not isinstance(records, list) or len(records) != 4:
        raise ValueError('complete apparatus archive requires four events')
    if type(archive['event_count']) is not int or archive['event_count'] != len(records):
        raise ValueError('archive event count mismatch')
    previous = AppendOnlyAuditLog.GENESIS
    events = []
    for index, record in enumerate(records):
        if type(record['sequence']) is not int or record['sequence'] != index or record['previous_hash'] != previous:
            raise ValueError('archive audit sequence/link mismatch')
        body = {key: record[key] for key in ('sequence', 'event', 'previous_hash')}
        if hash_object(body) != record['record_hash']:
            raise ValueError('archive audit hash mismatch')
        event = record['event']
        identity = {key: event[key] for key in ('trial_id', 'actor', 'kind', 'payload')}
        identity['sequence'] = index
        if event['event_id'] != hash_object(identity):
            raise ValueError('archive event identity mismatch')
        events.append(event)
        previous = record['record_hash']
    if previous != archive['audit_root_hash']:
        raise ValueError('archive audit root mismatch')
    if [e['kind'] for e in events] != ['memory_trial_started', 'trial_started', 'agent_answer', 'verifier_result']:
        raise ValueError('archive event coverage/order mismatch')
    config, task = metadata['trial_config'], metadata['task']
    parsed = dict(config)
    parsed['partition'] = Partition(parsed['partition'])
    TrialConfig(**parsed).validate_for_harness()
    if (archive['trial_id'] != config['trial_id'] or archive['partition'] != config['partition']
            or any(e['trial_id'] != config['trial_id'] for e in events)):
        raise ValueError('archive trial identity mismatch')
    start, answer, verification = (e['payload'] for e in events[1:])
    if start['trial_config_sha256'] != hash_object(config):
        raise ValueError('archive configuration binding mismatch')
    if start['task_sha256'] != hash_object(task):
        raise ValueError('archive task binding mismatch')
    if answer['answer_sha256'] != hash_object(metadata['actual_answer']):
        raise ValueError('archive answer binding mismatch')
    if (start['task_id'] != task['task_id'] or answer['task_id'] != task['task_id']
            or metadata['task_id'] != task['task_id'] or metadata['task_family_id'] != task['task_family_id']
            or config['task_family_id'] != task['task_family_id']):
        raise ValueError('archive task identity mismatch')
    if (archive['score'] != verification['score'] or archive['verifier_result'] != verification['status']):
        raise ValueError('archive verifier result mismatch')
    if (archive['completed'] is not True or archive['paused'] is not False
            or metadata['scientific_evidence'] is not False or metadata['execution_authorized'] is not False
            or metadata['evidence_quality'] != 'instrumentation'
            or metadata['apparatus_mode'] != 'scripted_fixture_instrumentation'):
        raise ValueError('archive instrumentation boundary mismatch')
    return {'verified_events': len(events), 'scientific_evidence': False, 'execution_authorized': False}
