import copy
import unittest
from dataclasses import asdict, replace
from unittest.mock import patch
import test_orchestrator
import test_partitions
from cohervia_harness.archive import verify_trial_archive
from cohervia_harness.audit import AppendOnlyAuditLog
from cohervia_harness.memory import GovernedMemory
from cohervia_harness.models import Partition
from cohervia_harness.tasks import development_tasks
from cohervia_harness.selectors import validate_estimate_statistics
from test_selectors import emergence_record,transfer_record


class ReviewFixTests(unittest.TestCase):
    def archive(self):
        f=test_orchestrator.OrchestratorTests();f.setUp()
        config=replace(test_partitions.PartitionTests()._config(Partition.INSTRUMENTATION),model_identity=f.agent.identity)
        return asdict(f.runner.run(config=config,task=development_tasks()[0],agent=f.agent))

    def test_archive_round_trip_and_saved_io_bindings(self):
        original=self.archive()
        self.assertEqual(verify_trial_archive(original)['verified_events'],4)
        for key,value in (('actual_answer',[999]),('task',{'task_id':'rewritten'}),
                          ('trial_config',{**original['metadata']['trial_config'],'system_configuration_hash':'rewritten'})):
            r=copy.deepcopy(original);r['metadata'][key]=value
            with self.subTest(key=key),self.assertRaisesRegex(ValueError,'binding mismatch'):
                verify_trial_archive(r)

    def test_archive_rejects_missing_corrupt_and_relabelled_artifacts(self):
        for mutate in (
            lambda r:r['metadata']['audit_records'].pop(),
            lambda r:r['metadata']['audit_records'][2]['event']['payload'].update(answer_sha256='fake'),
            lambda r:r.update(audit_root_hash='fake'),
            lambda r:r.update(score=0),
            lambda r:r['metadata'].update(scientific_evidence=True),
            lambda r:r['metadata'].update(execution_authorized=True),
            lambda r:r.update(partition='capability_holdout_a'),
        ):
            r=self.archive();mutate(r)
            with self.assertRaises(ValueError):verify_trial_archive(r)

    def test_memory_reuse_denied_and_new_trial_reset_audited(self):
        log=AppendOnlyAuditLog();m=GovernedMemory(audit=log);m.begin_trial('T1')
        m.write(actor='fixture',trial_id='T1',key='plan',value=42)
        state,root=m.state_hash,log.root_hash
        with self.assertRaises(PermissionError):m.begin_trial('T1')
        self.assertEqual((m.state_hash,log.root_hash),(state,root))
        m.begin_trial('T2')
        event=log.records[-1].event
        self.assertEqual(event.kind,'memory_trial_started')
        self.assertEqual(event.payload['previous_trial_id'],'T1')
        self.assertEqual(event.payload['previous_state_hash'],state)
        self.assertEqual(event.payload['resulting_state_hash'],m.state_hash)
        self.assertEqual(event.payload['persistence_scope'],'trial')
        self.assertTrue(log.verify())
        with self.assertRaises(PermissionError):m.begin_trial('T1')

    def test_failed_reset_preserves_state_and_trial_id_and_can_be_retried(self):
        log=AppendOnlyAuditLog();m=GovernedMemory(audit=log);m.begin_trial('T1')
        m.write(actor='fixture',trial_id='T1',key='plan',value=42)
        state,root=m.state_hash,log.root_hash
        with patch.object(log,'append',side_effect=OSError('sink failed')):
            with self.assertRaises(OSError):m.begin_trial('T2')
        self.assertEqual((m.trial_id,m.state_hash,log.root_hash),('T1',state,root))
        m.begin_trial('T2')
        self.assertIsNone(m.read(trial_id='T2',key='plan'))

    def test_unavailable_statistics_preserved_but_available_values_checked_for_all_labels(self):
        for factory,transfer,delta in ((emergence_record,False,'delta_emergent'),(transfer_record,True,'delta_transfer')):
            r=factory();r[delta]=None;r['lower_confidence_bound']=None
            self.assertTrue(validate_estimate_statistics(r,transfer=transfer,allow_missing=True).passed)
            r[delta]=-0.6
            self.assertFalse(validate_estimate_statistics(r,transfer=transfer,allow_missing=True).passed)
            for bad in (float('nan'),float('inf'),True):
                r[delta]=bad
                self.assertFalse(validate_estimate_statistics(r,transfer=transfer,allow_missing=True).passed)
