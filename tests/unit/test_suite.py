"""
Execution suite for Digital Vault ID Allocation tests (T1–T10).
"""

import sys
from pathlib import Path
import unittest
from tests.unit.id_allocator import IDAllocator, Entity, EntityStatus, VerificationStatus, SourceType
from tests.fixtures.test_data import (
    create_test_sandbox, cleanup_sandbox, create_registry_file, 
    create_email_entity, create_account_entity, TEST_EMAILS
)

class TestIDAllocation(unittest.TestCase):
    def setUp(self):
        self.sandbox = create_test_sandbox()
        self.registry_path = create_registry_file(self.sandbox)
        self.allocator = IDAllocator(self.sandbox / 'entities', self.registry_path)

    def tearDown(self):
        cleanup_sandbox(self.sandbox)

    def test_T1_concurrency_local(self):
        # Validate exclusive creation
        eid = self.allocator.allocate_id('EMAIL')
        e = create_email_entity(eid, TEST_EMAILS['user_a'])
        self.assertTrue(self.allocator.create_entity_atomic(e))
        
        # Try creating same again (collision)
        self.assertFalse(self.allocator.create_entity_atomic(e))

    def test_T6_format_prefixo_nnnn(self):
        # Validate zero padding
        eid = self.allocator.allocate_id('EMAIL')
        self.assertEqual(eid, 'EMAIL-0001')
        
        eid2 = self.allocator.allocate_id('EMAIL')
        self.assertEqual(eid2, 'EMAIL-0002')

    def test_T9_distinct_entities_collision(self):
        # CASE A: Distinct entities (same ID collision)
        # Create two distinct entities and attempt to save them to the same ID
        eid = 'EMAIL-0007'
        e1 = create_email_entity(eid, TEST_EMAILS['user_a'])
        e2 = create_email_entity(eid, TEST_EMAILS['user_b'])
        
        self.allocator.save_entity(e1)
        self.allocator.save_entity(e2) # Overwrote/conflicted!
        
        # Test collision handling per procedure
        collided = self.allocator.detect_collision('EMAIL')
        self.assertIn(eid, collided)
        
        # Procedimento rigoroso: preserver ambos (Já estão em disco)
        # Marcar CONFLICT
        # Simular processamento de colisão
        logs_dir = self.sandbox / 'logs' / 'conflicts'
        res = self.allocator.resolve_collision('CONFLICT-T9', [e1, e2], logs_dir)
        
        self.assertEqual(res['case'], 'distinct_entities')
        self.assertIsNotNone(res['reallocated_id'])
        self.assertNotEqual(e1.id, e2.id)

    def test_T10_same_entity_reconciliation(self):
        # CASE B: Same entity (same ID collision)
        eid = 'EMAIL-0007'
        e1 = create_email_entity(eid, TEST_EMAILS['same_user'], confidence=0.8)
        e2 = create_email_entity(eid, TEST_EMAILS['same_user'], confidence=0.9)
        
        self.allocator.save_entity(e1)
        self.allocator.save_entity(e2)
        
        # Test reconciliation handling per procedure
        logs_dir = self.sandbox / 'logs' / 'conflicts'
        res = self.allocator.resolve_collision('CONFLICT-T10', [e1, e2], logs_dir)
        
        self.assertEqual(res['case'], 'same_entity')
        self.assertIsNotNone(res['reconciled_file'])
        self.assertIsNone(res['reallocated_id'])
        # Confirma canônico e reconciliado
        self.assertTrue((self.sandbox / 'entities' / 'conflicts' / 'reconciled').exists())

if __name__ == '__main__':
    unittest.main()
