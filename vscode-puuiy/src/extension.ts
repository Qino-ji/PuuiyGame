import * as vscode from 'vscode';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const LANGUAGE_ID = 'piy';

const KEYWORDS = [
    'var', 'let', 'fn', 'func', 'class', 'extends',
    'if', 'elif', 'else', 'while', 'for', 'in',
    'return', 'pass', 'break', 'continue',
    'import', 'from', 'as', 'self', 'new',
    'true', 'false', 'null', 'none',
    'and', 'or', 'not', 'is'
];

const BUILTINS = [
    'print', 'range', 'len', 'typeof', 'str', 'int', 'float',
    'bool', 'array', 'dict', 'abs', 'min', 'max', 'random',
    'sin', 'cos', 'tan', 'sqrt', 'floor', 'ceil', 'clamp'
];

const TYPES = ['int', 'float', 'bool', 'string', 'array', 'dict', 'void', 'any'];

interface SnippetDef {
    label: string;
    snippet: string;
    detail: string;
}

const SNIPPETS: SnippetDef[] = [
    { label: 'fn',       snippet: 'fn ${1:name}(${2:args})\n\t${3:pass}',                                              detail: 'Function definition' },
    { label: 'class',    snippet: 'class ${1:Name}:\n\tvar ${2:name}: ${3:type} = ${4:value}\n\n\tfn init(${5:args})\n\t\t${6:pass}', detail: 'Class definition' },
    { label: 'if',       snippet: 'if ${1:condition}:\n\t${2:pass}',                                                  detail: 'If statement' },
    { label: 'elif',     snippet: 'elif ${1:condition}:\n\t${2:pass}',                                                detail: 'Elif statement' },
    { label: 'else',     snippet: 'else:\n\t${1:pass}',                                                               detail: 'Else statement' },
    { label: 'while',    snippet: 'while ${1:condition}:\n\t${2:pass}',                                               detail: 'While loop' },
    { label: 'for',      snippet: 'for ${1:item} in ${2:collection}:\n\t${3:pass}',                                   detail: 'For loop' },
    { label: 'extends',  snippet: 'class ${1:Name}:\n\textends ${2:Parent}\n\n\tfn init(${3:args})\n\t\t${4:pass}',   detail: 'Extended class' },
    { label: 'import',   snippet: 'import "${1:path}"',                                                               detail: 'Import module' },
];

const HOVER_DOCS: Record<string, string> = {
    'var':     'Variable declaration\n```piy\nvar x: int = 10\n```',
    'fn':      'Function declaration\n```piy\nfn add(a: int, b: int) -> int\n\treturn a + b\n```',
    'class':   'Class declaration\n```piy\nclass Player:\n\tvar health: int = 100\n```',
    'extends': 'Inheritance\n```piy\nclass Enemy:\n\textends Entity\n```',
    'if':      'Conditional statement\n```piy\nif x > 0:\n\tprint("positive")\n```',
    'while':   'While loop\n```piy\nwhile running:\n\tupdate()\n```',
    'for':     'For loop\n```piy\nfor i in range(10):\n\tprint(i)\n```',
    'self':    'Instance reference\n```piy\nfn init()\n\tself._x = 0\n```',
    'return':  'Return value\n```piy\nreturn result\n```',
    'pass':    'Empty block placeholder',
    'import':  'Import module\n```piy\nimport "engine/core/game.piy"\n```',
    'true':    'Boolean true',
    'false':   'Boolean false',
    'null':    'Null value',
    'print':   'Print to console\n```piy\nprint("hello")\n```',
    'range':   'Generate range\n```piy\nfor i in range(10):\n\t# 0..9\n```',
    'len':     'Get length\n```piy\nvar n = len(array)\n```',
    'typeof':  'Get type\n```piy\nvar t = typeof(x)\n```',
    'abs':     'Absolute value\n```piy\nvar v = abs(-5)\n```',
    'random':  'Random number\n```piy\nvar r = random()\n```',
};

const FOLDING_BLOCK_KEYWORDS = ['fn', 'func', 'if', 'elif', 'else', 'while', 'for', 'class'];

// Keywords that open a new block (indent after them when formatting).
// NOTE: "extends" is NOT a block opener — it is part of a class signature.
const FORMAT_BLOCK_KEYWORDS = ['fn', 'func', 'if', 'elif', 'else', 'while', 'for', 'class', 'case', 'default'];
const FORMAT_DEDENT_KEYWORDS = ['elif', 'else', 'case', 'default'];

const INDENT_STR = '    ';

// ---------------------------------------------------------------------------
// Utility helpers
// ---------------------------------------------------------------------------

function escapeRegex(str: string): string {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/** Count leading spaces on a line. */
function leadingSpaces(line: string): number {
    let n = 0;
    while (n < line.length && line[n] === ' ') {
        n++;
    }
    return n;
}

/** Check whether `str` starts with `prefix` followed by a word boundary. */
function startsWithWord(str: string, prefix: string): boolean {
    if (!str.startsWith(prefix)) return false;
    const nextChar = str[prefix.length];
    return nextChar === undefined || /[^\w]/.test(nextChar);
}

/** Return the first word (identifier) of a trimmed line, or empty string. */
function firstWordOf(line: string): string {
    return line.split(/[\s(]/)[0];
}

// ---------------------------------------------------------------------------
// Cached completion items (static — built once at activation time)
// ---------------------------------------------------------------------------

let cachedCompletions: vscode.CompletionItem[] | null = null;

function getCompletions(): vscode.CompletionItem[] {
    if (cachedCompletions) {
        return cachedCompletions;
    }

    const items: vscode.CompletionItem[] = [];

    for (const kw of KEYWORDS) {
        items.push(new vscode.CompletionItem(kw, vscode.CompletionItemKind.Keyword));
    }
    for (const bn of BUILTINS) {
        const item = new vscode.CompletionItem(bn, vscode.CompletionItemKind.Function);
        item.detail = 'Built-in function';
        items.push(item);
    }
    for (const tp of TYPES) {
        items.push(new vscode.CompletionItem(tp, vscode.CompletionItemKind.TypeParameter));
    }
    for (const s of SNIPPETS) {
        const item = new vscode.CompletionItem(s.label, vscode.CompletionItemKind.Snippet);
        item.insertText = new vscode.SnippetString(s.snippet);
        item.detail = s.detail;
        items.push(item);
    }

    cachedCompletions = items;
    return items;
}

// ---------------------------------------------------------------------------
// Extension lifecycle
// ---------------------------------------------------------------------------

/** Minimum interval (ms) between document validations to throttle CPU usage. */
const VALIDATION_DEBOUNCE_MS = 300;

export function activate(context: vscode.ExtensionContext): void {
    console.log('Puuiy Language Support is now active');

    const diagnosticCollection = vscode.languages.createDiagnosticCollection('piy');
    context.subscriptions.push(diagnosticCollection);

    // Document validation on open (immediate) and change (debounced)
    let validationTimer: ReturnType<typeof setTimeout> | undefined;

    context.subscriptions.push(
        vscode.workspace.onDidOpenTextDocument(doc => {
            if (doc.languageId === LANGUAGE_ID) {
                validatePiyDocument(doc, diagnosticCollection);
            }
        })
    );
    context.subscriptions.push(
        vscode.workspace.onDidChangeTextDocument(e => {
            if (e.document.languageId !== LANGUAGE_ID) return;
            if (validationTimer) {
                clearTimeout(validationTimer);
            }
            validationTimer = setTimeout(() => {
                validationTimer = undefined;
                validatePiyDocument(e.document, diagnosticCollection);
            }, VALIDATION_DEBOUNCE_MS);
        })
    );

    // Commands
    context.subscriptions.push(
        vscode.commands.registerCommand('piy.run', () => runPiyFile(false))
    );
    context.subscriptions.push(
        vscode.commands.registerCommand('piy.runCurrent', () => runPiyFile(true))
    );
    context.subscriptions.push(
        vscode.commands.registerCommand('piy.format', formatPiyDocument)
    );
    context.subscriptions.push(
        vscode.commands.registerCommand('piy.fixIndent', fixIndentCommand)
    );

    // Language features
    context.subscriptions.push(
        vscode.languages.registerCompletionItemProvider(LANGUAGE_ID, createCompletionProvider())
    );
    context.subscriptions.push(
        vscode.languages.registerHoverProvider(LANGUAGE_ID, createHoverProvider())
    );
    context.subscriptions.push(
        vscode.languages.registerDefinitionProvider(LANGUAGE_ID, createDefinitionProvider())
    );
    context.subscriptions.push(
        vscode.languages.registerReferenceProvider(LANGUAGE_ID, createReferenceProvider())
    );
    context.subscriptions.push(
        vscode.languages.registerDocumentSymbolProvider(LANGUAGE_ID, createDocumentSymbolProvider())
    );
    context.subscriptions.push(
        vscode.languages.registerCodeActionsProvider(LANGUAGE_ID, createCodeActionProvider())
    );
    context.subscriptions.push(
        vscode.languages.registerFoldingRangeProvider(LANGUAGE_ID, createFoldingRangeProvider())
    );
    context.subscriptions.push(
        vscode.languages.registerInlayHintsProvider(LANGUAGE_ID, createInlayHintsProvider())
    );

    // Formatting provider (enables built-in Format Document / Format on Save)
    context.subscriptions.push(
        vscode.languages.registerDocumentFormattingEditProvider(LANGUAGE_ID, {
            provideDocumentFormattingEdits(document: vscode.TextDocument): vscode.TextEdit[] {
                const fullText = document.getText();
                const formatted = formatPiyCode(fullText);
                const fullRange = new vscode.Range(
                    document.positionAt(0),
                    document.positionAt(fullText.length)
                );
                return [vscode.TextEdit.replace(fullRange, formatted)];
            }
        })
    );
}

export function deactivate() {
    // Release cached completions so they can be GC'd on extension deactivation
    cachedCompletions = null;
}

// ---------------------------------------------------------------------------
// Configuration helpers
// ---------------------------------------------------------------------------

function getPythonCommand(): string {
    return vscode.workspace.getConfiguration('puuiy').get<string>('pythonCommand', 'python');
}

function getRunnerScript(): string {
    return vscode.workspace.getConfiguration('puuiy').get<string>('runnerScript', 'puuiy.py');
}

// ---------------------------------------------------------------------------
// Command implementations
// ---------------------------------------------------------------------------

/**
 * Run a .piy file in a terminal.
 * @param requireExtension  If true, the active file MUST end with ".piy".
 */
function runPiyFile(requireExtension: boolean): void {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage('No active editor');
        return;
    }

    const filePath = editor.document.fileName;
    if (requireExtension && !filePath.endsWith('.piy')) {
        vscode.window.showErrorMessage('Current file is not a .piy file');
        return;
    }

    const terminal = vscode.window.createTerminal('Puuiy');
    const quote = filePath.includes('"') ? "'" : '"';
    terminal.sendText(`${getPythonCommand()} ${getRunnerScript()} ${quote}${filePath}${quote}`);
    terminal.show();
}

function formatPiyDocument(): void {
    const editor = vscode.window.activeTextEditor;
    if (!editor) return;

    const document = editor.document;
    const fullText = document.getText();
    const formatted = formatPiyCode(fullText);
    const fullRange = new vscode.Range(
        document.positionAt(0),
        document.positionAt(fullText.length)
    );

    void editor.edit(editBuilder => {
        editBuilder.replace(fullRange, formatted);
    });
}

/** Fix indentation without changing anything else (piy.fixIndent command). */
function fixIndentCommand(): void {
    formatPiyDocument();
}

// ---------------------------------------------------------------------------
// Provider factories
// ---------------------------------------------------------------------------

function createCompletionProvider(): vscode.CompletionItemProvider<vscode.CompletionItem> {
    return {
        provideCompletionItems(_document: vscode.TextDocument, _position: vscode.Position): vscode.CompletionItem[] {
            return getCompletions();
        }
    };
}

function createHoverProvider(): vscode.HoverProvider {
    return {
        provideHover(document: vscode.TextDocument, position: vscode.Position): vscode.Hover | undefined {
            const wordRange = document.getWordRangeAtPosition(position);
            if (!wordRange) return undefined;

            const word = document.getText(wordRange);
            if (word && HOVER_DOCS[word]) {
                return new vscode.Hover(new vscode.MarkdownString(HOVER_DOCS[word]));
            }
            return undefined;
        }
    };
}

function createDefinitionProvider(): vscode.DefinitionProvider {
    return {
        provideDefinition(document: vscode.TextDocument, position: vscode.Position): vscode.Location | undefined {
            const wordRange = document.getWordRangeAtPosition(position);
            if (!wordRange) return undefined;

            const word = document.getText(wordRange);
            if (!word) return undefined;

            const text = document.getText();
            const patterns = [
                new RegExp(`^(\\s*)(fn|func)\\s+${escapeRegex(word)}\\s*\\(`, 'm'),
                new RegExp(`^(\\s*)(var|let)\\s+${escapeRegex(word)}\\b`, 'm'),
                new RegExp(`^(\\s*)class\\s+${escapeRegex(word)}\\b`, 'm'),
            ];

            for (const pattern of patterns) {
                const match = pattern.exec(text);
                if (match) {
                    const line = text.substring(0, match.index).split('\n').length - 1;
                    return new vscode.Location(document.uri, new vscode.Position(line, 0));
                }
            }
            return undefined;
        }
    };
}

function createReferenceProvider(): vscode.ReferenceProvider {
    return {
        provideReferences(document: vscode.TextDocument, position: vscode.Position, _context: vscode.ReferenceContext): vscode.Location[] {
            const wordRange = document.getWordRangeAtPosition(position);
            if (!wordRange) return [];

            const word = document.getText(wordRange);
            if (!word) return [];

            const escaped = escapeRegex(word);
            const wordBoundaryRegex = new RegExp(`\\b${escaped}\\b`, 'g');

            const text = document.getText();
            const locations: vscode.Location[] = [];
            let match: RegExpExecArray | null;
            while ((match = wordBoundaryRegex.exec(text)) !== null) {
                const offset = match.index;
                const pos = document.positionAt(offset);
                locations.push(new vscode.Location(document.uri, pos));
            }
            return locations;
        }
    };
}

function createDocumentSymbolProvider(): vscode.DocumentSymbolProvider {
    return {
        provideDocumentSymbols(document: vscode.TextDocument): vscode.DocumentSymbol[] {
            const symbols: vscode.DocumentSymbol[] = [];
            const lines = document.getText().split('\n');
            let currentClass: vscode.DocumentSymbol | null = null;

            for (let i = 0; i < lines.length; i++) {
                const line = lines[i];
                const trimmed = line.trim();

                const classMatch = trimmed.match(/^class\s+(\w+)/);
                if (classMatch) {
                    const fullRange = new vscode.Range(i, 0, i, line.length);
                    const nameStart = line.indexOf(classMatch[1]);
                    const selRange = new vscode.Range(i, nameStart, i, nameStart + classMatch[1].length);
                    const symbol = new vscode.DocumentSymbol(
                        classMatch[1], '',
                        vscode.SymbolKind.Class,
                        fullRange, selRange
                    );
                    symbols.push(symbol);
                    currentClass = symbol;
                    continue;
                }

                const fnMatch = trimmed.match(/^\s*(?:fn|func)\s+(\w+)/);
                if (fnMatch) {
                    const fullRange = new vscode.Range(i, 0, i, line.length);
                    const nameStart = line.indexOf(fnMatch[1]);
                    const selRange = new vscode.Range(i, nameStart, i, nameStart + fnMatch[1].length);
                    const symbol = new vscode.DocumentSymbol(
                        fnMatch[1], '',
                        vscode.SymbolKind.Function,
                        fullRange, selRange
                    );
                    if (currentClass) {
                        currentClass.children.push(symbol);
                    } else {
                        symbols.push(symbol);
                    }
                    continue;
                }

                const varMatch = trimmed.match(/^\s*(?:var|let)\s+(\w+)/);
                if (varMatch) {
                    const fullRange = new vscode.Range(i, 0, i, line.length);
                    const nameStart = line.indexOf(varMatch[1]);
                    const selRange = new vscode.Range(i, nameStart, i, nameStart + varMatch[1].length);
                    const symbol = new vscode.DocumentSymbol(
                        varMatch[1], '',
                        vscode.SymbolKind.Variable,
                        fullRange, selRange
                    );
                    if (currentClass) {
                        currentClass.children.push(symbol);
                    }
                }
            }
            return symbols;
        }
    };
}

function createCodeActionProvider(): vscode.CodeActionProvider {
    return {
        provideCodeActions(document: vscode.TextDocument, range: vscode.Range, _context: vscode.CodeActionContext): vscode.CodeAction[] {
            const actions: vscode.CodeAction[] = [];
            const line = document.lineAt(range.start).text;
            const trimmed = line.trim();

            // Missing colon quick-fixes
            for (const { pattern, title } of MISSING_COLON_PATTERNS) {
                if (pattern.test(trimmed) && !trimmed.endsWith(':')) {
                    actions.push(makeAddColonFix(document, range, line, title));
                    break; // Only one colon fix per line
                }
            }

            // Add type hint for variable declarations without a type annotation
            const indentPrefix = line.substring(0, line.length - trimmed.length);
            const isIndented = indentPrefix.length > 0;
            if (isIndented && trimmed.match(/^(var|let)\s+\w+\s*=\s*.+$/)) {
                if (!trimmed.includes(':')) {
                    const match = trimmed.match(/^(var|let)\s+(\w+)\s*=\s*(.+)$/);
                    if (match) {
                        const fix = new vscode.CodeAction('Add type hint', vscode.CodeActionKind.QuickFix);
                        fix.edit = new vscode.WorkspaceEdit();
                        const newLine = `${indentPrefix}var ${match[2]}: any = ${match[3]}`;
                        fix.edit.replace(document.uri, range, newLine);
                        actions.push(fix);
                    }
                }
            }

            // Prefix unused variables (skip occurrences inside comments/strings)
            const unusedVarMatch = trimmed.match(/^(?:var|let)\s+(\w+).*=\s*.+$/);
            if (unusedVarMatch) {
                const wordRange = document.getWordRangeAtPosition(range.start);
                if (wordRange) {
                    const word = document.getText(wordRange);
                    const text = document.getText();
                    const wordBoundaryRegex = new RegExp(`\\b${escapeRegex(word)}\\b`, 'g');
                    let count = 0;
                    let m: RegExpExecArray | null;
                    while ((m = wordBoundaryRegex.exec(text)) !== null) {
                        const pos = document.positionAt(m.index);
                        const checkLine = document.lineAt(pos.line).text;
                        const col = pos.character;
                        if (
                            checkLine.trimStart().startsWith('#') ||
                            isInsideString(checkLine, col)
                        ) {
                            continue;
                        }
                        count++;
                    }
                    if (count === 1) {
                        const fix = new vscode.CodeAction(
                            `Prefix unused variable '${word}' with underscore`,
                            vscode.CodeActionKind.QuickFix
                        );
                        fix.edit = new vscode.WorkspaceEdit();
                        const kwdMatch = trimmed.match(/^(var|let)\s+(\w+)/);
                        if (kwdMatch) {
                            const newLine = line.replace(`${kwdMatch[1]} ${kwdMatch[2]}`, `${kwdMatch[1]} _${kwdMatch[2]}`);
                            fix.edit.replace(document.uri, range, newLine);
                        }
                        actions.push(fix);
                    }
                }
            }

            return actions;
        }
    };
}



/** Check whether a column position on a line is inside a string literal. */
function isInsideString(line: string, column: number): boolean {
    let inString = false;
    let stringChar = '';
    for (let i = 0; i < column; i++) {
        const ch = line[i];
        if (!ch) break;
        if (ch === '\\') { i++; continue; }
        if (inString) {
            if (ch === stringChar) { inString = false; }
        } else {
            if (ch === '"' || ch === "'") { inString = true; stringChar = ch; }
        }
    }
    return inString;
}

function makeAddColonFix(document: vscode.TextDocument, range: vscode.Range, line: string, title: string): vscode.CodeAction {
    const fix = new vscode.CodeAction(title, vscode.CodeActionKind.QuickFix);
    fix.edit = new vscode.WorkspaceEdit();
    fix.edit.replace(document.uri, range, line + ':');
    return fix;
}

function createFoldingRangeProvider(): vscode.FoldingRangeProvider {
    return {
        provideFoldingRanges(document: vscode.TextDocument): vscode.FoldingRange[] {
            const ranges: vscode.FoldingRange[] = [];
            const lines = document.getText().split('\n');
            const stack: number[] = [];

            for (let i = 0; i < lines.length; i++) {
                const trimmed = lines[i].trim();
                const firstWord = firstWordOf(trimmed);

                if (FOLDING_BLOCK_KEYWORDS.includes(firstWord) && trimmed.endsWith(':')) {
                    stack.push(i);
                } else if (stack.length > 0 && lines[i].length > 0 && leadingSpaces(lines[i]) === 0) {
                    // A non-indented line closes the current folding block
                    const start = stack.pop()!;
                    if (i - start > 1) {
                        ranges.push(new vscode.FoldingRange(start, i - 1));
                    }
                }
                // Empty lines and comments are intentionally ignored — they don't break folding
            }

            // Close any remaining blocks at end-of-file
            while (stack.length > 0) {
                const start = stack.pop()!;
                ranges.push(new vscode.FoldingRange(start, lines.length - 1));
            }
            return ranges;
        }
    };
}

function createInlayHintsProvider(): vscode.InlayHintsProvider {
    return {
        provideInlayHints(document: vscode.TextDocument, range: vscode.Range): vscode.InlayHint[] {
            const hints: vscode.InlayHint[] = [];
            const text = document.getText(range);
            const lines = text.split('\n');

            for (let i = 0; i < lines.length; i++) {
                const line = lines[i];
                const baseLine = range.start.line + i;

                // Inferred type for variable declarations
                const varMatch = line.match(/^\s*(?:var|let)\s+(\w+)\s*=\s*(.+)$/);
                if (varMatch && !line.includes(':')) {
                    const eqPos = line.indexOf('=');
                    if (eqPos !== -1) {
                        const val = varMatch[2].trim();
                        const inferredType = inferTypeFromValue(val);
                        hints.push(new vscode.InlayHint(
                            new vscode.Position(baseLine, eqPos),
                            `: ${inferredType}`,
                            vscode.InlayHintKind.Type
                        ));
                    }
                }

                // Return type annotation
                const fnMatch = line.match(/^\s*(?:fn|func)\s+\w+\(.*\)\s*->\s*(\w+)/);
                if (fnMatch) {
                    const arrowPos = line.indexOf('->');
                    if (arrowPos !== -1) {
                        hints.push(new vscode.InlayHint(
                            new vscode.Position(baseLine, arrowPos + 2),
                            ` ${fnMatch[1]}`,
                            vscode.InlayHintKind.Type
                        ));
                    }
                }
            }
            return hints;
        }
    };
}

function inferTypeFromValue(value: string): string {
    if (/^-?\d+\.\d+$/.test(value)) return 'float';
    if (/^-?\d+$/.test(value)) return 'int';
    if (value === 'true' || value === 'false') return 'bool';
    if (value.startsWith('"') || value.startsWith("'")) return 'string';
    if (value.startsWith('[')) return 'array';
    if (value.startsWith('{')) return 'dict';
    if (value.endsWith('.new()')) return value.replace('.new()', '');
    return 'any';
}

// Patterns for quick-fix colon detection
const MISSING_COLON_PATTERNS: Array<{ pattern: RegExp; title: string }> = [
    { pattern: /^fn\s+\w+\(.*\)\s*$/,           title: 'Add colon after function signature' },
    { pattern: /^(?:if|elif|while|for)\s+.+$/,  title: 'Add colon after condition' },
    { pattern: /^else$/,                         title: 'Add colon after else' },
    { pattern: /^class\s+\w+$/,                  title: 'Add colon after class declaration' },
];

// ---------------------------------------------------------------------------
// Document validation
// ---------------------------------------------------------------------------

function validatePiyDocument(document: vscode.TextDocument, diagnosticCollection: vscode.DiagnosticCollection): void {
    const diagnostics: vscode.Diagnostic[] = [];
    const lines = document.getText().split('\n');

    const indentStack: number[] = [0];
    let inString = false;
    let stringChar = '';

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        const trimmed = line.trim();

        if (trimmed === '' || trimmed.startsWith('#')) {
            continue;
        }

        const currentIndent = leadingSpaces(line);

        // Indentation consistency check (skip when inside a multi-line string)
        if (!inString) {
            if (currentIndent > indentStack[indentStack.length - 1]) {
                indentStack.push(currentIndent);
            } else if (currentIndent < indentStack[indentStack.length - 1]) {
                while (indentStack.length > 1 && indentStack[indentStack.length - 1] > currentIndent) {
                    indentStack.pop();
                }
                if (indentStack[indentStack.length - 1] !== currentIndent && currentIndent !== 0) {
                    diagnostics.push(new vscode.Diagnostic(
                        new vscode.Range(i, 0, i, line.length),
                        `Inconsistent indentation at line ${i + 1}`,
                        vscode.DiagnosticSeverity.Warning
                    ));
                }
            }
        }

        // Track multi-line strings (operate on trimmed to skip leading whitespace)
        for (let k = 0; k < trimmed.length; k++) {
            const ch = trimmed[k];
            if (ch === '#') break;
            if (inString) {
                if (ch === '\\') { k++; continue; }
                if (ch === stringChar) { inString = false; }
            } else {
                if (ch === '"' || ch === "'") {
                    // Triple-quoted string — skip the delimiter
                    if (k + 2 < trimmed.length && trimmed[k + 1] === ch && trimmed[k + 2] === ch) {
                        k += 2;
                        continue;
                    }
                    inString = true;
                    stringChar = ch;
                }
            }
        }
    }

    diagnosticCollection.set(document.uri, diagnostics);
}

// ---------------------------------------------------------------------------
// Code formatting
// ---------------------------------------------------------------------------

function formatPiyCode(code: string): string {
    const lines = code.split('\n');
    const formatted: string[] = [];
    let indentLevel = 0;

    for (const line of lines) {
        const trimmed = line.trim();

        if (trimmed === '' || trimmed.startsWith('#')) {
            formatted.push(trimmed);
            continue;
        }

        const firstWord = firstWordOf(trimmed);

        // Dedent before applying current indent for keywords like elif / else / case / default
        if (FORMAT_DEDENT_KEYWORDS.includes(firstWord) && indentLevel > 0) {
            indentLevel--;
        }

        formatted.push(INDENT_STR.repeat(indentLevel) + trimmed);

        // Check if this line opens a new block (ends with ":" and starts with a block keyword)
        const isBlockOpener = FORMAT_BLOCK_KEYWORDS.some(kw => {
            if (startsWithWord(trimmed, kw)) {
                return trimmed.endsWith(':');
            }
            return false;
        });

        if (isBlockOpener) {
            indentLevel++;
        }
    }

    return formatted.join('\n');
}