"""
Test fixtures for Digital Vault ID allocation tests.
Synthetic data only - no real vault data.
"""

import tempfile
import shutil
from pathlib import Path
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from unit.id_allocator import IDAllocator, Entity, EntityStatus, VerificationStatus, SourceType, Verification, Relationship, CredentialRef
from datetime import datetime, timezone


def create_test_sandbox() -> Path:
    """Create isolated test sandbox directory"""
    sandbox = Path(tempfile.mkdtemp(prefix='dv_test_'))
    # Create directory structure
    dirs = [
        'emails', 'accounts', 'organizations', 'projects', 'domains',
        'repositories', 'servers', 'phones', 'sims', 'devices', 'billing',
        'meta', 'bm', 'ads', 'page', 'pixel', 'waba', 'wa', 'api',
        'credentials', 'audits', 'logs', 'conflicts', 'relationships', 'inbox'
    ]
    for d in dirs:
        (sandbox / d).mkdir(parents=True, exist_ok=True)
    return sandbox


def cleanup_sandbox(sandbox: Path):
    """Remove test sandbox"""
    shutil.rmtree(sandbox, ignore_errors=True)


def create_registry_file(sandbox: Path) -> Path:
    """Create initial registry file"""
    registry = sandbox / 'logs' / 'ids-allocated.md'
    registry.parent.mkdir(parents=True, exist_ok=True)
    content = """| Prefixo | Categoria | Último Número Alocado | Próximo Disponível |
|---|---|---:|---|
| EMAIL | Email | 0 | 1 |
| ACCOUNT | Conta de plataforma | 0 | 1 |
| ORG | Organização/Empresa | 0 | 1 |
| PROJECT | Projeto/Marca/Site | 0 | 1 |
| DOMAIN | Domínio | 0 | 1 |
| REPO | Repositório Git | 0 | 1 |
| SERVER | Servidor/VPS | 0 | 1 |
| PHONE | Telefone | 0 | 1 |
| SIM | SIM card / Chip | 0 | 1 |
| DEVICE | Dispositivo | 0 | 1 |
| BILLING | Billing / Assinatura | 0 | 1 |
| META | Perfil Meta | 0 | 1 |
| BM | Business Manager | 0 | 1 |
| ADS | Conta de Anúncios | 0 | 1 |
| PAGE | Página FB/IG | 0 | 1 |
| PIXEL | Pixel / Dataset | 0 | 1 |
| WABA | WhatsApp Business Account | 0 | 1 |
| WA | WhatsApp | 0 | 1 |
| API | API Key / Endpoint | 0 | 1 |
| CRED | Referência de Credencial | 0 | 1 |
| AUDIT | Relatório de Auditoria | 0 | 1 |
| LOG | Log | 0 | 1 |
| CONFLICT | Registro de Conflito | 0 | 1 |
| REL | Relacionamento separado | 0 | 1 |
| INBOX | Item da Inbox | 0 | 1 |"""
    registry.write_text(content, encoding='utf-8')
    return registry


def create_test_entity(entity_id: str, entity_type: str, name: str, 
                       platform: str = "", status: EntityStatus = EntityStatus.ACTIVE,
                       verification_status: VerificationStatus = VerificationStatus.UNVERIFIED,
                       source_type: SourceType = SourceType.MANUAL,
                       source_ref: str = None,
                       confidence: float = 0.5) -> Entity:
    """Create a test entity"""
    if source_ref is None:
        source_ref = f"test-{source_type.value}"
    return Entity(
        id=entity_id,
        type=entity_type,
        name=name,
        status=status,
        platform=platform,
        verification=Verification(
            status=verification_status,
            source_type=source_type,
            source_ref=source_ref,
            confidence=confidence
        )
    )


def create_email_entity(entity_id: str, email: str, **kwargs) -> Entity:
    """Create email entity with normalized identity"""
    defaults = {'entity_type': 'email', 'platform': 'gmail'}
    defaults.update(kwargs)
    return create_test_entity(entity_id, defaults['entity_type'], email, platform=defaults['platform'], **{k:v for k,v in kwargs.items() if k not in ['entity_type', 'platform']})


def create_account_entity(entity_id: str, platform: str, name: str, **kwargs) -> Entity:
    """Create account entity"""
    defaults = {'entity_type': 'account'}
    defaults.update(kwargs)
    return create_test_entity(entity_id, defaults['entity_type'], name, platform=platform, **{k:v for k,v in kwargs.items() if k not in ['entity_type']})


# Synthetic test data
TEST_EMAILS = {
    'user_a': 'user-a@example.test',
    'user_b': 'user-b@example.test',
    'same_user': 'same-user@example.test',
    'user_c': 'User.C@Gmail.COM',  # Test normalization
}

TEST_ACCOUNTS = {
    'vercel_a': {'platform': 'vercel', 'name': 'user-a@example.test'},
    'vercel_b': {'platform': 'vercel', 'name': 'user-b@example.test'},
    'github_same': {'platform': 'github', 'name': 'same-user@example.test'},
}

TEST_PROJECTS = {
    'proj_a': {'platform': 'vercel', 'name': 'project-a'},
    'proj_b': {'platform': 'vercel', 'name': 'project-b'},
}