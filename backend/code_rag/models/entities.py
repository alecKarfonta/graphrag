"""
Core entity models for Code RAG system.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union
from enum import Enum
import hashlib
import json


class EntityType(Enum):
    FUNCTION = "function"
    CLASS = "class"
    VARIABLE = "variable"
    MODULE = "module"
    INTERFACE = "interface"
    ENUM = "enum"
    STRUCT = "struct"
    IMPORT = "import"


class Visibility(Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    PROTECTED = "protected"
    INTERNAL = "internal"
    SPECIAL = "special"


class RelationshipType(Enum):
    CALLS = "calls"
    INHERITS = "inherits"
    IMPLEMENTS = "implements"
    IMPORTS = "imports"
    USES = "uses"
    CONTAINS = "contains"
    FOLLOWS_PATTERN = "follows_pattern"
    DEPENDS_ON = "depends_on"


@dataclass
class CodeEntity:
    """Base class for all code entities."""
    name: str
    entity_type: EntityType
    file_path: str
    line_start: int
    line_end: int
    language: str
    visibility: Visibility = Visibility.PUBLIC
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Generate unique ID after initialization."""
        self.id = self.generate_id()
    
    def generate_id(self) -> str:
        """Generate unique identifier for this entity."""
        content = f"{self.file_path}:{self.name}:{self.entity_type.value}:{self.line_start}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "entity_type": self.entity_type.value,
            "file_path": self.file_path,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "language": self.language,
            "visibility": self.visibility.value,
            "metadata": self.metadata
        }
    
    def to_search_text(self) -> str:
        """Generate searchable text representation."""
        return f"{self.entity_type.value} {self.name}"


@dataclass
class FunctionEntity(CodeEntity):
    """Represents a function or method in code."""
    parameters: List[Dict[str, str]] = field(default_factory=list)
    return_type: Optional[str] = None
    docstring: Optional[str] = None
    decorators: List[str] = field(default_factory=list)
    complexity: int = 1
    is_async: bool = False
    is_method: bool = False
    class_name: Optional[str] = None
    calls: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        super().__post_init__()
        self.entity_type = EntityType.FUNCTION
    
    def to_search_text(self) -> str:
        """Generate searchable text representation for functions."""
        parts = [
            f"function {self.name}",
            f"parameters: {', '.join([p.get('name', '') for p in self.parameters])}",
            f"returns: {self.return_type or 'None'}",
            self.docstring or "",
            f"decorators: {', '.join(self.decorators)}" if self.decorators else "",
            f"async function" if self.is_async else "",
            f"method of {self.class_name}" if self.is_method and self.class_name else "",
            f"calls: {', '.join(self.calls)}" if self.calls else ""
        ]
        return " ".join(filter(None, parts))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert function entity to dictionary."""
        base_dict = super().to_dict()
        base_dict.update({
            "parameters": self.parameters,
            "return_type": self.return_type,
            "docstring": self.docstring,
            "decorators": self.decorators,
            "complexity": self.complexity,
            "is_async": self.is_async,
            "is_method": self.is_method,
            "class_name": self.class_name,
            "calls": self.calls
        })
        return base_dict


@dataclass
class ClassEntity(CodeEntity):
    """Represents a class in code."""
    base_classes: List[str] = field(default_factory=list)
    methods: List[str] = field(default_factory=list)
    properties: List[str] = field(default_factory=list)
    interfaces: List[str] = field(default_factory=list)
    design_patterns: List[str] = field(default_factory=list)
    is_abstract: bool = False
    is_interface: bool = False
    docstring: Optional[str] = None
    
    def __post_init__(self):
        super().__post_init__()
        self.entity_type = EntityType.CLASS
    
    def to_search_text(self) -> str:
        """Generate searchable text representation for classes."""
        parts = [
            f"class {self.name}",
            f"inherits: {', '.join(self.base_classes)}" if self.base_classes else "",
            f"implements: {', '.join(self.interfaces)}" if self.interfaces else "",
            f"methods: {', '.join(self.methods)}",
            f"properties: {', '.join(self.properties)}" if self.properties else "",
            f"patterns: {', '.join(self.design_patterns)}" if self.design_patterns else "",
            "abstract class" if self.is_abstract else "",
            "interface" if self.is_interface else "",
            self.docstring or ""
        ]
        return " ".join(filter(None, parts))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert class entity to dictionary."""
        base_dict = super().to_dict()
        base_dict.update({
            "base_classes": self.base_classes,
            "methods": self.methods,
            "properties": self.properties,
            "interfaces": self.interfaces,
            "design_patterns": self.design_patterns,
            "is_abstract": self.is_abstract,
            "is_interface": self.is_interface,
            "docstring": self.docstring
        })
        return base_dict


@dataclass
class VariableEntity(CodeEntity):
    """Represents a variable or constant in code."""
    variable_type: Optional[str] = None
    scope: str = "local"  # local, global, class, instance
    is_constant: bool = False
    initial_value: Optional[str] = None
    
    def __post_init__(self):
        super().__post_init__()
        self.entity_type = EntityType.VARIABLE
    
    def to_search_text(self) -> str:
        """Generate searchable text representation for variables."""
        parts = [
            f"variable {self.name}",
            f"type: {self.variable_type}" if self.variable_type else "",
            f"scope: {self.scope}",
            "constant" if self.is_constant else "",
            f"value: {self.initial_value}" if self.initial_value else ""
        ]
        return " ".join(filter(None, parts))


@dataclass
class ModuleEntity(CodeEntity):
    """Represents a module or file in code."""
    imports: List[str] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    docstring: Optional[str] = None
    
    def __post_init__(self):
        super().__post_init__()
        self.entity_type = EntityType.MODULE
    
    def to_search_text(self) -> str:
        """Generate searchable text representation for modules."""
        parts = [
            f"module {self.name}",
            f"imports: {', '.join(self.imports)}" if self.imports else "",
            f"exports: {', '.join(self.exports)}" if self.exports else "",
            f"functions: {', '.join(self.functions)}" if self.functions else "",
            f"classes: {', '.join(self.classes)}" if self.classes else "",
            self.docstring or ""
        ]
        return " ".join(filter(None, parts))


@dataclass
class RelationshipEntity:
    """Represents a relationship between code entities."""
    source_entity_id: str
    target_entity_id: str
    relationship_type: RelationshipType
    context: str = ""
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Generate unique ID after initialization."""
        self.id = self.generate_id()
    
    def generate_id(self) -> str:
        """Generate unique identifier for this relationship."""
        content = f"{self.source_entity_id}:{self.target_entity_id}:{self.relationship_type.value}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert relationship to dictionary for serialization."""
        return {
            "id": self.id,
            "source_entity_id": self.source_entity_id,
            "target_entity_id": self.target_entity_id,
            "relationship_type": self.relationship_type.value,
            "context": self.context,
            "confidence": self.confidence,
            "metadata": self.metadata
        }


@dataclass
class ParseResult:
    """Result of parsing a code file."""
    file_path: str
    language: str
    success: bool
    entities: List[CodeEntity] = field(default_factory=list)
    relationships: List[RelationshipEntity] = field(default_factory=list)
    ast_tree: Optional[Any] = None
    source_code: Optional[str] = None
    error: Optional[str] = None
    parse_time_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert parse result to dictionary."""
        return {
            "file_path": self.file_path,
            "language": self.language,
            "success": self.success,
            "entities": [entity.to_dict() for entity in self.entities],
            "relationships": [rel.to_dict() for rel in self.relationships],
            "error": self.error,
            "parse_time_ms": self.parse_time_ms,
            "entity_count": len(self.entities),
            "relationship_count": len(self.relationships)
        }


# Type aliases for convenience
AnyEntity = Union[FunctionEntity, ClassEntity, VariableEntity, ModuleEntity] 