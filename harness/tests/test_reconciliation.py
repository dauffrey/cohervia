import copy
import unittest
from dataclasses import replace
from unittest.mock import patch

from cohervia_harness.audit import AppendOnlyAuditLog
from cohervia_harness.events import Event
from cohervia_harness.memory import GovernedMemory
from cohervia_harness.models import Partition
from cohervia_harness.selectors import (
    recompute_emergence_gate, recompute_transfer_gate,
    cross_family_eligible_configurations,
)
from test_selectors import emergence_record, transfer_record
import test_orchestrator
import test_partitions
from cohervia_harness.tasks import development_tasks


class ReconciliationTests(unittest.TestCase):
    def test_gate_rejects_nonfinite_boolean_missing_and_inconsistent_statistics(self):
        for factory, gate, delta in ((emergence_record, recompute_emergence_gate, 'delta_emergent'),
                                     (transfer_record, recompute_transfer_gate, 'delta_transfer')):
            for key in (delta, 'lower_confidence_bound', 'mean_observed_value', 'baseline_prediction'):
                for bad in (float('nan'), float('inf'), float('-inf'), True, None, '0.3'):
                    with self.subTest(key=key, bad=bad):
                        r=factory(); r[key]=bad
                        self.assertFalse(gate(r).passed)
            r=factory(); r['mean_observed_value']=0.2; r['baseline_prediction']=0.8
            self.assertIn('residual_component_mismatch', gate(r).reasons)

    def test_cross_family_rejects_mixed_hashes_stages_experiments_and_comparators(self):
        for key, value in (('system_configuration_hash','other'),('experiment_id','COH-EXP-0002'),
                           ('comparator_definition_hash','other'),('capability_endpoint_id','other')):
            a=[emergence_record('f1'),emergence_record('f2')]
            b=[transfer_record('f1'),transfer_record('f2')]
            b[1][key]=value
            self.assertEqual(cross_family_eligible_configurations(a,b),frozenset())
        a=[emergence_record('f1'),emergence_record('f2')]
        b=[transfer_record('f1'),transfer_record('f2')]
        conflict=copy.deepcopy(b[1]); conflict['protocol_valid']=False
        self.assertEqual(cross_family_eligible_configurations(a,b+[conflict]),frozenset())

    def test_audit_input_append_result_and_exposed_records_cannot_rewrite_history(self):
        audit=AppendOnlyAuditLog(); payload={'nested':{'values':[1]}}
        event=Event.create(trial_id='T',actor='fixture',kind='fixture',payload=payload,sequence=0)
        payload['nested']['values'].append(2)
        returned=audit.append(event); root=audit.root_hash
        event.payload['nested']['values'].append(3)
        returned.event.payload['nested']['values'].append(4)
        audit.records[0].event.payload['nested']['values'].append(5)
        self.assertEqual(audit.records[0].event.payload['nested']['values'],[1])
        self.assertEqual(audit.root_hash,root); self.assertTrue(audit.verify())

    def test_memory_copy_scope_and_atomic_failure(self):
        audit=AppendOnlyAuditLog(); memory=GovernedMemory(audit=audit); memory.begin_trial('T')
        value={'items':[1]}
        w=memory.write(actor='fixture',trial_id='T',key='k',value=value)
        value['items'].append(2); memory.read(trial_id='T',key='k')['items'].append(3)
        self.assertEqual(memory.state_hash,w.resulting_state_hash)
        self.assertEqual(w.persistence_scope,'trial')
        self.assertEqual(audit.records[-1].event.payload['persistence_scope'],'trial')
        before=memory.state_hash
        with patch.object(audit,'append',side_effect=OSError('sink failed')):
            with self.assertRaises(OSError):
                memory.write(actor='fixture',trial_id='T',key='k',value=42)
        self.assertEqual(memory.state_hash,before)
        with self.assertRaises(ValueError):
            memory.write(actor='fixture',trial_id='T',key='k',value=float('nan'))
        self.assertEqual(memory.state_hash,before)

    def test_holdouts_rejected_before_any_agent_or_task_execution(self):
        fixture=test_orchestrator.OrchestratorTests(); fixture.setUp()
        for partition in (Partition.CAPABILITY_HOLDOUT_A,Partition.TRANSFER_HOLDOUT_B,Partition.GOVERNANCE_HOLDOUT_C):
            config=test_partitions.PartitionTests()._config(partition)
            with patch.object(fixture.agent,'solve') as solve:
                with self.assertRaises(PermissionError):
                    fixture.runner.run(config=config,task=development_tasks()[0],agent=fixture.agent)
                solve.assert_not_called()
        for malformed in ('capability_holdout_a','development',None):
            with self.assertRaises(ValueError):
                test_partitions.PartitionTests()._config(malformed).validate_for_harness()

    def test_arbitrary_agents_and_tasks_rejected_and_fixture_remains_instrumentation(self):
        fixture=test_orchestrator.OrchestratorTests(); fixture.setUp()
        task=development_tasks()[0]
        config=replace(test_partitions.PartitionTests()._config(Partition.DEVELOPMENT),model_identity=fixture.agent.identity)
        class Unreviewed:
            def solve(self, task):
                raise AssertionError('must not execute')
        with self.assertRaises(PermissionError):
            fixture.runner.run(config=config,task=task,agent=Unreviewed())
        with self.assertRaises(PermissionError):
            fixture.runner.run(config=config,task=replace(task,prompt='unreviewed'),agent=fixture.agent)
        result=fixture.runner.run(config=config,task=task,agent=fixture.agent)
        self.assertFalse(result.metadata['scientific_evidence'])
        self.assertFalse(result.metadata['execution_authorized'])
        self.assertEqual(result.metadata['evidence_quality'],'instrumentation')
        self.assertEqual(result.metadata['actual_answer'],[1,2,3])
        self.assertEqual(len(result.metadata['audit_records']),result.event_count)
