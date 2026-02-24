import os

from tree_sitter import Language, Parser
# Import all grammars
import tree_sitter_c as ts_c
import tree_sitter_c_sharp as ts_c_sharp
import tree_sitter_cpp as ts_cpp
import tree_sitter_go as ts_go
import tree_sitter_java as ts_java
import tree_sitter_javascript as ts_javascript
import tree_sitter_php as ts_php
import tree_sitter_python as ts_python
import tree_sitter_ruby as ts_ruby
import tree_sitter_rust as ts_rust
import tree_sitter_typescript as ts_typescript

from .extractors import (
    BaseExtractor,
    CExtractor,
    CppExtractor,
    CSharpExtractor,
    GoExtractor,
    JavaExtractor,
    ParsedFile,
    PHPExtractor,
    PythonExtractor,
    RubyExtractor,
    RustExtractor,
    TypeScriptExtractor,
)

# ── 1. Language Detection & Parsing Setup ─────────────────────────────────────

LANGUAGE_EXTENSIONS = {
    "typescript": {".ts"},
    "tsx": {".tsx"},
    "javascript": {".js", ".jsx", ".mjs"},
    "python": {".py"},
    "go": {".go"},
    "rust": {".rs"},
    "java": {".java"},
    "c": {".c", ".h"},
    "cpp": {".cpp", ".cc", ".hpp", ".cxx"},
    "ruby": {".rb"},
    "c_sharp": {".cs"},
    "php": {".php"},
}

_parser_cache: dict[str, Parser] = {}

def get_language_from_path(file_path: str) -> str | None:
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    for lang, exts in LANGUAGE_EXTENSIONS.items():
        if ext in exts:
            return "typescript" if lang == "tsx" else lang
    return None

def _load_grammar(language: str) -> Language:
    lang_map = {
        "typescript": ts_typescript.language_typescript(),
        "tsx": ts_typescript.language_tsx(),
        "javascript": ts_javascript.language(),
        "python": ts_python.language(),
        "go": ts_go.language(),
        "rust": ts_rust.language(),
        "java": ts_java.language(),
        "c": ts_c.language(),
        "cpp": ts_cpp.language(),
        "ruby": ts_ruby.language(),
        "c_sharp": ts_c_sharp.language(),
        "php": ts_php.language_php(),
    }
    return Language(lang_map[language], language)

def _get_parser(language: str) -> Parser:
    if language not in _parser_cache:
        parser = Parser()
        parser.set_language(_load_grammar(language))
        _parser_cache[language] = parser
    return _parser_cache[language]

def _get_extractor(language: str) -> BaseExtractor:
    extractors: dict[str, type[BaseExtractor]] = {
        "typescript": TypeScriptExtractor,
        "javascript": TypeScriptExtractor,
        "python": PythonExtractor,
        "go": GoExtractor,
        "rust": RustExtractor,
        "java": JavaExtractor,
        "c": CExtractor,
        "cpp": CppExtractor,
        "ruby": RubyExtractor,
        "c_sharp": CSharpExtractor,
        "php": PHPExtractor,
    }
    return extractors[language]()


# ── 2. Core Parsing Engine ────────────────────────────────────────────────────

def parse_file(file_path: str, file_content: bytes) -> ParsedFile | None:
    """Parses a file and extracts its AST metadata into the unified structure."""
    language = get_language_from_path(file_path)
    if not language:
        return None

    # Handle TSX vs TS dynamically based on actual file path
    if file_path.endswith(".tsx"):
        parser = _get_parser("tsx")
    else:
        parser = _get_parser(language)

    tree = parser.parse(file_content)
    extractor = _get_extractor(language)
    
    return extractor.extract(tree.root_node, file_content, file_path)
