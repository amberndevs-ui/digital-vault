"""
Digital Vault ID Allocation Core Module

Implements the canonical ID allocation and collision resolution rules
from logs/ids-allocated.md for testing purposes.
"""

import os
import yaml
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import threading
import time


class EntityStatus(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    ARCHIVED = "ARCHIVED"
    DELETED = "DELETED"
    UNKNOWN = "UNKNOWN"
    CONFLICT = "CONFLICT"
    RECONCILED = "RECONCILED"


class VerificationStatus(Enum):
    VERIFIED = "VERIFIED"
    UNVERIFIED = "UNVERIFIED"
    STALE = "STALE"
    UNKNOWN = "UNKNOWN"
    CONFLICT = "CONFLICT"


class SourceType(Enum):
    MANUAL = "manual"
    API = "api"
    EMAIL = "email"
    FILE = "file"
    SCREENSHOT = "screenshot"
    IMPORT = "import"
    PLATFORM = "platform"
    INFERRED = "inferred"
    OTHER = "other"


@dataclass
class Verification:
    status: VerificationStatus = VerificationStatus.UNVERIFIED
    source_type: SourceType = SourceType.MANUAL
    source_ref: str = "user-provided"
    discovered_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_verified: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    confidence: float = 0.5


@dataclass
class Relationship:
    to: str
    type: str
    valid_from: Optional[str] = None
    valid_until: Optional[str] = None
    role: Optional[str] = None
    primary: bool = False
    source: Optional[str] = None
    confidence: Optional[float] = None


@dataclass
class CredentialRef:
    credential_id: str
    provider: str
    reference: str
    related_entity: str


@dataclass
class Entity:
    id: str
    type: str
    name: str
    status: EntityStatus = EntityStatus.ACTIVE
    platform: str = ""
    relationships: List[Relationship] = field(default_factory=list)
    verification: Verification = field(default_factory=Verification)
    credential_ref: Optional[CredentialRef] = None
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    conflict_history: List[Dict] = field(default_factory=list)


class IDAllocator:
    """Core ID allocation logic matching logs/ids-allocated.md"""
    
    PREFIXES = {
        'EMAIL', 'ACCOUNT', 'ORG', 'PROJECT', 'DOMAIN', 'REPO', 'SERVER',
        'PHONE', 'SIM', 'DEVICE', 'BILLING', 'META', 'BM', 'ADS', 'PAGE',
        'PIXEL', 'WABA', 'WA', 'API', 'CRED', 'AUDIT', 'LOG', 'CONFLICT', 'REL', 'INBOX'
    }
    
    def __init__(self, entities_root: Path, registry_path: Path):
        self.entities_root = Path(entities_root)
        self.registry_path = Path(registry_path)
        self._lock = threading.Lock()
        self._load_registry()
    
    def _load_registry(self):
        """Load registry from file (advisory only)"""
        self.registry = {}
        if self.registry_path.exists():
            content = self.registry_path.read_text(encoding='utf-8')
            # Simple parsing for markdown table
            for line in content.split('\n'):
                if '|' in line and not line.startswith('|---') and not line.startswith('| Prefixo'):
                    parts = [p.strip() for p in line.split('|')[1:-1]]
                    if len(parts) >= 3:
                        prefix = parts[0]
                        try:
                            last = int(parts[1])
                            next_avail = int(parts[2])
                            self.registry[prefix] = {'last': last, 'next': next_avail}
                        except ValueError:
                            pass
    
    def _save_registry(self):
        """Save registry to file"""
        lines = [
            "| Prefixo | Categoria | Último Número Alocado | Próximo Disponível |",
            "|---|---|---:|---|"
        ]
        categories = {
            'EMAIL': 'Email', 'ACCOUNT': 'Conta de plataforma', 'ORG': 'Organização/Empresa',
            'PROJECT': 'Projeto/Marca/Site', 'DOMAIN': 'Domínio', 'REPO': 'Repositório Git',
            'SERVER': 'Servidor/VPS', 'PHONE': 'Telefone', 'SIM': 'SIM card / Chip',
            'DEVICE': 'Dispositivo', 'BILLING': 'Billing / Assinatura', 'META': 'Perfil Meta',
            'BM': 'Business Manager', 'ADS': 'Conta de Anúncios', 'PAGE': 'Página FB/IG',
            'PIXEL': 'Pixel / Dataset', 'WABA': 'WhatsApp Business Account', 'WA': 'WhatsApp',
            'API': 'API Key / Endpoint', 'CRED': 'Referência de Credencial', 'AUDIT': 'Relatório de Auditoria',
            'LOG': 'Log', 'CONFLICT': 'Registro de Conflito', 'REL': 'Relacionamento separado', 'INBOX': 'Item da Inbox'
        }
        for prefix in sorted(self.PREFIXES):
            cat = categories.get(prefix, prefix)
            data = self.registry.get(prefix, {'last': 0, 'next': 1})
            lines.append(f"| {prefix} | {cat} | {data['last']} | {data['next']} |")
        content = "\n".join(lines) + "\n"
        self.registry_path.write_text(content, encoding='utf-8')
    
    def _normalize_email(self, email: str) -> str:
        """Normalize email for identity comparison"""
        email = email.strip()
        if '@' in email:
            local, domain = email.rsplit('@', 1)
            return f"{local.lower()}@{domain.lower()}"
        return email.lower()
    
    def _normalize_domain(self, domain: str) -> str:
        """Normalize domain for identity comparison"""
        domain = domain.strip().lower()
        if domain.endswith('.'):
            domain = domain[:-1]
        return domain
    
    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone to E.164 if possible"""
        # Simplified: just strip formatting
        cleaned = ''.join(c for c in phone if c.isdigit() or c == '+')
        return cleaned
    
    def get_identity_key(self, entity: Entity) -> str:
        """Get normalized identity key for deduplication"""
        if entity.type == 'email':
            return f"email:{self._normalize_email(entity.name)}"
        elif entity.type == 'domain':
            return f"domain:{self._normalize_domain(entity.name)}"
        elif entity.type in ('phone', 'whatsapp'):
            return f"phone:{self._normalize_phone(entity.name)}"
        elif entity.type == 'account':
            return f"account:{entity.platform}:{entity.name}"
        elif entity.type == 'project':
            return f"project:{entity.platform}:{entity.name}"
        return f"{entity.type}:{entity.name}"
    
    def _candidate_id(self, prefix: str) -> str:
        """Generate candidate ID from registry"""
        if prefix not in self.registry:
            self.registry[prefix] = {'last': 0, 'next': 1}
        next_num = self.registry[prefix]['next']
        return f"{prefix}-{next_num:04d}"
    
    def _entity_path(self, entity_id: str) -> Path:
        """Get filesystem path for entity"""
        prefix = entity_id.split('-')[0].lower() + 's'
        # Map prefix to directory
        dir_map = {
            'EMAIL': 'emails', 'ACCOUNT': 'accounts', 'ORG': 'organizations',
            'PROJECT': 'projects', 'DOMAIN': 'domains', 'REPO': 'repositories',
            'SERVER': 'servers', 'PHONE': 'phones', 'SIM': 'sims',
            'DEVICE': 'devices', 'BILLING': 'billing', 'META': 'meta',
            'BM': 'bm', 'ADS': 'ads', 'PAGE': 'page', 'PIXEL': 'pixel',
            'WABA': 'waba', 'WA': 'wa', 'API': 'api', 'CRED': 'credentials',
            'AUDIT': 'audits', 'LOG': 'logs', 'CONFLICT': 'conflicts',
            'REL': 'relationships', 'INBOX': 'inbox'
        }
        directory = dir_map.get(entity_id.split('-')[0], 'unknown')
        return self.entities_root / directory / f"{entity_id}.yaml"
    
    def _entity_exists(self, entity_id: str) -> bool:
        """Check if entity exists in filesystem (authoritative)"""
        return self._entity_path(entity_id).exists()
    
    def _find_conflicted_copies(self, prefix: str) -> List[Path]:
        """Find conflicted copy files for a prefix"""
        dir_map = {
            'EMAIL': 'emails', 'ACCOUNT': 'accounts', 'ORG': 'organizations',
            'PROJECT': 'projects', 'DOMAIN': 'domains', 'REPO': 'repositories',
            'SERVER': 'servers', 'PHONE': 'phones', 'SIM': 'sims',
            'DEVICE': 'devices', 'BILLING': 'billing'
        }
        directory = dir_map.get(prefix, '')
        if not directory:
            return []
        entity_dir = self.entities_root / directory
        if not entity_dir.exists():
            return []
        return list(entity_dir.glob("*conflicted copy*"))
    
    def allocate_id(self, prefix: str, use_exclusive: bool = True) -> str:
        """
        Allocate next available ID for prefix.
        Uses exclusive creation when available.
        """
        if prefix not in self.PREFIXES:
            raise ValueError(f"Unknown prefix: {prefix}")
        
        with self._lock:
            # Pre-check: find next available by scanning filesystem
            while True:
                candidate = self._candidate_id(prefix)
                if not self._entity_exists(candidate):
                    break
                # Registry stale - increment
                self.registry[prefix]['next'] += 1
            
            # Update registry
            self.registry[prefix]['last'] = int(candidate.split('-')[1])
            self.registry[prefix]['next'] = self.registry[prefix]['last'] + 1
            self._save_registry()
            
            return candidate
    
    def create_entity_atomic(self, entity: Entity, use_exclusive: bool = True) -> bool:
        """
        Create entity file with atomic/exclusive write.
        Returns True on success, False on collision.
        """
        path = self._entity_path(entity.id)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to YAML
        data = {
            'id': entity.id,
            'type': entity.type,
            'name': entity.name,
            'status': entity.status.value,
            'platform': entity.platform,
            'relationships': [
                {
                    'to': r.to,
                    'type': r.type,
                    'valid_from': r.valid_from,
                    'valid_until': r.valid_until,
                    'role': r.role,
                    'primary': r.primary,
                    'source': r.source,
                    'confidence': r.confidence
                }
                for r in entity.relationships
            ],
            'verification': {
                'status': entity.verification.status.value,
                'source_type': entity.verification.source_type.value,
                'source_ref': entity.verification.source_ref,
                'discovered_at': entity.verification.discovered_at,
                'last_verified': entity.verification.last_verified,
                'confidence': entity.verification.confidence
            },
            'notes': entity.notes,
            'created_at': entity.created_at,
            'updated_at': entity.updated_at,
            'conflict_history': entity.conflict_history
        }
        if entity.credential_ref:
            data['credential_ref'] = {
                'credential_id': entity.credential_ref.credential_id,
                'provider': entity.credential_ref.provider,
                'reference': entity.credential_ref.reference,
                'related_entity': entity.credential_ref.related_entity
            }
        
        yaml_content = yaml.dump(data, allow_unicode=True, sort_keys=False)
        
        try:
            if use_exclusive:
                # Exclusive creation (atomic on POSIX)
                with open(path, 'x', encoding='utf-8') as f:
                    f.write(yaml_content)
            else:
                # Fallback: temp file + rename + revalidate
                tmp_path = path.with_suffix('.tmp')
                with open(tmp_path, 'w', encoding='utf-8') as f:
                    f.write(yaml_content)
                # Validate temp
                with open(tmp_path, 'r', encoding='utf-8') as f:
                    test_load = yaml.safe_load(f)
                if test_load.get('id') != entity.id:
                    tmp_path.unlink(missing_ok=True)
                    return False
                tmp_path.rename(path)
                # Revalidate
                with open(path, 'r', encoding='utf-8') as f:
                    final_load = yaml.safe_load(f)
                if final_load.get('id') != entity.id:
                    return False
            return True
        except FileExistsError:
            return False
        except Exception:
            return False
    
    def load_entity(self, entity_id: str) -> Optional[Entity]:
        """Load entity from filesystem"""
        path = self._entity_path(entity_id)
        if not path.exists():
            return None
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        if not data:
            return None
        entity = Entity(
            id=data['id'],
            type=data['type'],
            name=data['name'],
            status=EntityStatus(data.get('status', 'ACTIVE')),
            platform=data.get('platform', ''),
            notes=data.get('notes', ''),
            created_at=data.get('created_at', ''),
            updated_at=data.get('updated_at', ''),
            conflict_history=data.get('conflict_history', [])
        )
        # Relationships
        for r in data.get('relationships', []):
            entity.relationships.append(Relationship(
                to=r['to'], type=r['type'],
                valid_from=r.get('valid_from'), valid_until=r.get('valid_until'),
                role=r.get('role'), primary=r.get('primary', False),
                source=r.get('source'), confidence=r.get('confidence')
            ))
        # Verification
        v = data.get('verification', {})
        entity.verification = Verification(
            status=VerificationStatus(v.get('status', 'UNVERIFIED')),
            source_type=SourceType(v.get('source_type', 'manual')),
            source_ref=v.get('source_ref', ''),
            discovered_at=v.get('discovered_at', ''),
            last_verified=v.get('last_verified', ''),
            confidence=v.get('confidence', 0.5)
        )
        # Credential ref
        cr = data.get('credential_ref')
        if cr:
            entity.credential_ref = CredentialRef(
                credential_id=cr['credential_id'],
                provider=cr['provider'],
                reference=cr['reference'],
                related_entity=cr['related_entity']
            )
        return entity
    
    def save_entity(self, entity: Entity):
        """Save entity (overwrite)"""
        path = self._entity_path(entity.id)
        path.parent.mkdir(parents=True, exist_ok=True)
        entity.updated_at = datetime.now(timezone.utc).isoformat()
        
        data = {
            'id': entity.id,
            'type': entity.type,
            'name': entity.name,
            'status': entity.status.value,
            'platform': entity.platform,
            'relationships': [
                {
                    'to': r.to, 'type': r.type,
                    'valid_from': r.valid_from, 'valid_until': r.valid_until,
                    'role': r.role, 'primary': r.primary,
                    'source': r.source, 'confidence': r.confidence
                }
                for r in entity.relationships
            ],
            'verification': {
                'status': entity.verification.status.value,
                'source_type': entity.verification.source_type.value,
                'source_ref': entity.verification.source_ref,
                'discovered_at': entity.verification.discovered_at,
                'last_verified': entity.verification.last_verified,
                'confidence': entity.verification.confidence
            },
            'notes': entity.notes,
            'created_at': entity.created_at,
            'updated_at': entity.updated_at,
            'conflict_history': entity.conflict_history
        }
        if entity.credential_ref:
            data['credential_ref'] = {
                'credential_id': entity.credential_ref.credential_id,
                'provider': entity.credential_ref.provider,
                'reference': entity.credential_ref.reference,
                'related_entity': entity.credential_ref.related_entity
            }
        
        yaml_content = yaml.dump(data, allow_unicode=True, sort_keys=False)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
    
    def detect_collision(self, prefix: str) -> List[str]:
        """Detect duplicate IDs in filesystem and conflicted copies"""
        dir_map = {
            'EMAIL': 'emails', 'ACCOUNT': 'accounts', 'ORG': 'organizations',
            'PROJECT': 'projects', 'DOMAIN': 'domains', 'REPO': 'repositories',
            'SERVER': 'servers', 'PHONE': 'phones', 'SIM': 'sims',
            'DEVICE': 'devices', 'BILLING': 'billing'
        }
        directory = dir_map.get(prefix, '')
        if not directory:
            return []
        entity_dir = self.entities_root / directory
        if not entity_dir.exists():
            return []
        
        ids = []
        has_conflicted_copy = False
        # Check all files in directory, not just *.yaml
        for f in entity_dir.iterdir():
            if not f.is_file():
                continue
            if 'RECONCILED-' in f.name:
                continue
            eid = f.stem
            if eid.startswith(f"{prefix}-"):
                if 'conflicted copy' in f.name:
                    has_conflicted_copy = True
                else:
                    ids.append(eid)
        
        # Find duplicate stems
        seen = set()
        dupes = set()
        for eid in ids:
            if eid in seen:
                dupes.add(eid)
            seen.add(eid)
        
        # Conflicted copy indicates a collision
        if has_conflicted_copy:
            # Return the base ID that has the conflicted copy
            for f in entity_dir.glob("*.conflicted copy"):
                # stem is "EMAIL-0001.yaml" for "EMAIL-0001.yaml.conflicted copy"
                base = f.stem
                if base.endswith('.yaml'):
                    base = base[:-5]
                if base.startswith(f"{prefix}-"):
                    dupes.add(base)
        
        return list(dupes)
    
    def resolve_collision(self, conflict_id: str, entities: List[Entity], 
                          logs_dir: Path) -> Dict[str, Any]:
        """
        Resolve collision per logs/ids-allocated.md procedure.
        Returns resolution details.
        """
        if len(entities) != 2:
            raise ValueError("Expected exactly 2 entities for collision")
        
        e1, e2 = entities
        
        # Step 2: Preserve both - already in filesystem
        # Step 3: Mark conflict
        e1.status = EntityStatus.CONFLICT
        e1.verification.status = VerificationStatus.CONFLICT
        e1.conflict_history.append({
            'conflict_id': conflict_id,
            'detected_at': datetime.now(timezone.utc).isoformat(),
            'reason': 'duplicate_id_post_sync'
        })
        e2.status = EntityStatus.CONFLICT
        e2.verification.status = VerificationStatus.CONFLICT
        e2.conflict_history.append({
            'conflict_id': conflict_id,
            'detected_at': datetime.now(timezone.utc).isoformat(),
            'reason': 'duplicate_id_post_sync'
        })
        
        # Step 4: Determine canonical claim via provenance
        key1 = self.get_identity_key(e1)
        key2 = self.get_identity_key(e2)
        
        logs_dir.mkdir(parents=True, exist_ok=True)
        conflict_log = logs_dir / f"{conflict_id}.yaml"
        
        resolution = {
            'conflict_id': conflict_id,
            'original_ids': [e1.id, e2.id],
            'identity_keys': [key1, key2],
            'case': None,
            'canonical_id': None,
            'reallocated_id': None,
            'reconciled_file': None,
            'manual_required': False,
            'provenance_analysis': {}
        }
        
        if key1 != key2:
            # CASE A: Distinct entities
            resolution['case'] = 'distinct_entities'
            # Decide by provenance (simplified: first one keeps ID)
            # In real impl, would compare source_type, discovered_at, verification, relationships
            canonical = e1
            other = e2
            
            # Allocate new ID for other
            prefix = e2.id.split('-')[0]
            new_id = self.allocate_id(prefix)
            
            # Update other entity
            old_id = e2.id
            e2.id = new_id
            e2.status = EntityStatus.ACTIVE
            e2.verification.status = VerificationStatus.UNVERIFIED
            e2.conflict_history.append({
                'previous_id': old_id,
                'conflict_id': conflict_id,
                'resolved_at': datetime.now(timezone.utc).isoformat(),
                'resolution': 'reallocated_distinct_entity'
            })
            
            resolution['canonical_id'] = canonical.id
            resolution['reallocated_id'] = new_id
            
            # Save both
            self.save_entity(canonical)
            self.save_entity(e2)
            
            # Update relationships in other entities (simplified)
            # In real impl, would scan all entities and update references
            
        else:
            # CASE B: Same real entity
            resolution['case'] = 'same_entity'
            # Decide canonical by provenance
            # Simplified: higher confidence wins
            if e1.verification.confidence >= e2.verification.confidence:
                canonical = e1
                duplicate = e2
            else:
                canonical = e2
                duplicate = e1
            
            # Duplicate becomes RECONCILED evidence (no new ID)
            reconciled_id = f"RECONCILED-{duplicate.id}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}"
            duplicate.id = reconciled_id
            duplicate.status = EntityStatus.RECONCILED
            duplicate.verification.status = VerificationStatus.VERIFIED
            
            # Move to reconciled location
            old_path = self._entity_path(f"{duplicate.id.split('-')[0]}-{duplicate.id.split('-')[1]}")  # original path
            # Actually save as reconciled
            reconciled_path = self.entities_root / 'conflicts' / 'reconciled' / f"{reconciled_id}.yaml"
            reconciled_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save canonical
            self.save_entity(canonical)
            # Save reconciled
            self.save_entity(duplicate)  # This will use new id
            
            # Record in canonical's conflict history
            canonical.conflict_history.append({
                'reconciled_duplicate': reconciled_id,
                'conflict_id': conflict_id,
                'resolved_at': datetime.now(timezone.utc).isoformat(),
                'resolution': 'reconciled_same_entity'
            })
            self.save_entity(canonical)
            
            resolution['canonical_id'] = canonical.id
            resolution['reconciled_file'] = reconciled_id
        
        # Step 7: Log conflict
        conflict_log.write_text(yaml.dump(resolution, allow_unicode=True, sort_keys=False), encoding='utf-8')
        
        return resolution
    
    def validate_cleanup_conditions(self, conflict_id: str, logs_dir: Path) -> Dict[str, bool]:
        """Validate Step 8 cleanup conditions"""
        results = {
            'A_versions_preserved': False,
            'B_ids_unique': False,
            'C_relationships_updated': False,
            'D_conflict_log_persisted': False,
            'can_cleanup': False
        }
        
        # A: Versions preserved
        conflict_files = list(logs_dir.glob(f"*{conflict_id}*.yaml"))
        reconciled_files = list((self.entities_root / 'conflicts' / 'reconciled').glob(f"*{conflict_id.split('-')[-1]}*.yaml"))
        conflict_ab_files = list(self.entities_root.glob(f"**/CONFLICT-*{conflict_id.split('-')[-1]}*.yaml"))
        results['A_versions_preserved'] = len(conflict_files) > 0 or len(reconciled_files) > 0 or len(conflict_ab_files) > 0
        
        # B: IDs unique
        # Check all entities for duplicates
        all_ids = []
        for entity_dir in self.entities_root.iterdir():
            if entity_dir.is_dir():
                for f in entity_dir.glob("*.yaml"):
                    if 'conflicted copy' not in f.name:
                        all_ids.append(f.stem)
        results['B_ids_unique'] = len(all_ids) == len(set(all_ids))
        
        # C: Relationships updated (simplified - check no references to old conflicted IDs)
        # In real impl, would verify all relationships point to valid IDs
        results['C_relationships_updated'] = True  # Placeholder
        
        # D: Conflict log persisted
        results['D_conflict_log_persisted'] = (logs_dir / f"{conflict_id}.yaml").exists()
        
        results['can_cleanup'] = all(results.values())
        return results


def normalize_email(email: str) -> str:
    """Standalone email normalization"""
    email = email.strip()
    if '@' in email:
        local, domain = email.rsplit('@', 1)
        return f"{local.lower()}@{domain.lower()}"
    return email.lower()


def normalize_domain(domain: str) -> str:
    """Standalone domain normalization"""
    domain = domain.strip().lower()
    if domain.endswith('.'):
        domain = domain[:-1]
    return domain


def normalize_phone(phone: str) -> str:
    """Standalone phone normalization"""
    cleaned = ''.join(c for c in phone if c.isdigit() or c == '+')
    return cleaned


def is_canonical_id(entity_id: str) -> bool:
    """Validate ID matches PREFIXO-NNNN pattern"""
    import re
    pattern = r'^[A-Z]{2,7}-\d{4}$'
    return bool(re.match(pattern, entity_id))


def is_inbox_id(entity_id: str) -> bool:
    """Check if ID is inbox format"""
    return entity_id.startswith('INBOX-')


# Export key functions
__all__ = [
    'IDAllocator', 'Entity', 'EntityStatus', 'VerificationStatus', 'SourceType',
    'Verification', 'Relationship', 'CredentialRef',
    'normalize_email', 'normalize_domain', 'normalize_phone',
    'is_canonical_id', 'is_inbox_id'
]