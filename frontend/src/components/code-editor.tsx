"use client";

import { useEffect } from "react";
import Editor from "@monaco-editor/react";

const JAVA_TEMPLATE = `// Your code must define: public class Main
// Read input from stdin (BufferedReader / Scanner), print output to stdout.
public class Main {
    public static void main(String[] args) throws Exception {
        java.io.BufferedReader br = new java.io.BufferedReader(new java.io.InputStreamReader(System.in));
        String line = br.readLine();
        System.out.println(line);
    }
}
`;

export interface CompletionSpec {
  label: string;
  kind: "Keyword" | "Class" | "Method" | "Snippet" | "Value" | "Struct" | "Field";
  detail?: string;
  /** Defaults to the label. Snippets use ${n:placeholder} syntax. */
  insertText?: string;
  documentation?: string;
}

const JAVA_KEYWORDS =
  "abstract boolean break byte case catch char class continue default do double else enum extends final finally float for if implements import instanceof int interface long new package private protected public return short static super switch synchronized this throw throws transient try void volatile while".split(
    " "
  );

const JAVA_CLASSES =
  "String StringBuilder List ArrayList LinkedList Map HashMap LinkedHashMap Set HashSet TreeSet Queue Deque ArrayDeque Arrays Collections Math Integer Long Double Boolean Character Object Exception RuntimeException IOException Scanner BufferedReader InputStreamReader Pattern Matcher Optional Stream Collectors Comparator System Thread Runnable".split(
    " "
  );

export const JAVA_COMPLETIONS: CompletionSpec[] = [
  ...JAVA_KEYWORDS.map((k) => ({ label: k, kind: "Keyword" as const, detail: "Java keyword" })),
  ...JAVA_CLASSES.map((c) => ({ label: c, kind: "Class" as const, detail: "Java class" })),
  {
    label: "sout",
    kind: "Snippet",
    detail: "System.out.println(… )",
    insertText: "System.out.println(${1});",
    documentation: "Print a line to stdout.",
  },
  {
    label: "main",
    kind: "Snippet",
    detail: "public static void main(String[] args)",
    insertText: "public static void main(String[] args) {\n\t${1}\n}",
  },
  {
    label: "fori",
    kind: "Snippet",
    detail: "for loop with an index",
    insertText: "for (int i = 0; i < ${1:n}; i++) {\n\t${2}\n}",
  },
  {
    label: "foreach",
    kind: "Snippet",
    detail: "for-each loop",
    insertText: "for (${1:String} ${2:item} : ${3:items}) {\n\t${4}\n}",
  },
  {
    label: "trycatch",
    kind: "Snippet",
    detail: "try / catch block",
    insertText: "try {\n\t${1}\n} catch (Exception e) {\n\t${2:e.printStackTrace();}\n}",
  },
  {
    label: "scanner",
    kind: "Snippet",
    detail: "Scanner reading stdin",
    insertText: "Scanner sc = new Scanner(System.in);",
  },
  {
    label: "buffered",
    kind: "Snippet",
    detail: "BufferedReader reading stdin",
    insertText: "BufferedReader br = new BufferedReader(new InputStreamReader(System.in));",
  },
  {
    label: "classMain",
    kind: "Snippet",
    detail: "runnable Main class skeleton",
    insertText:
      "public class Main {\n\tpublic static void main(String[] args) throws Exception {\n\t\t${1}\n\t}\n}",
  },
  {
    label: "arraylist",
    kind: "Snippet",
    detail: "List backed by ArrayList",
    insertText: "List<${1:String}> ${2:list} = new ArrayList<>();",
  },
  {
    label: "hashmap",
    kind: "Snippet",
    detail: "Map backed by HashMap",
    insertText: "Map<${1:String}, ${2:Integer}> ${3:map} = new HashMap<>();",
  },
];

const SQL_KEYWORDS = [
  "SELECT",
  "FROM",
  "WHERE",
  "GROUP BY",
  "HAVING",
  "ORDER BY",
  "LIMIT",
  "OFFSET",
  "JOIN",
  "INNER JOIN",
  "LEFT JOIN",
  "RIGHT JOIN",
  "FULL JOIN",
  "ON",
  "AS",
  "DISTINCT",
  "UNION",
  "UNION ALL",
  "INTERSECT",
  "EXCEPT",
  "WITH",
  "CASE",
  "WHEN",
  "THEN",
  "ELSE",
  "END",
  "AND",
  "OR",
  "NOT",
  "IS NULL",
  "LIKE",
  "IN",
  "BETWEEN",
  "EXISTS",
  "ASC",
  "DESC",
];

const SQL_FUNCTIONS = [
  "COUNT",
  "SUM",
  "AVG",
  "MIN",
  "MAX",
  "ROUND",
  "COALESCE",
  "LOWER",
  "UPPER",
  "LENGTH",
  "SUBSTR",
  "CAST",
  "GROUP_CONCAT",
  "STRFTIME",
];

export const SQL_COMPLETIONS: CompletionSpec[] = [
  ...SQL_KEYWORDS.map((k) => ({
    label: k,
    kind: "Keyword" as const,
    detail: "SQL keyword",
    insertText: `${k} `,
  })),
  ...SQL_FUNCTIONS.map((f) => ({ label: f, kind: "Method" as const, detail: "SQL function" })),
];

interface MonacoLike {
  languages: {
    registerCompletionItemProvider: (language: string, provider: unknown) => void;
    CompletionItemKind: Record<string, number>;
    CompletionItemInsertTextRule: { InsertAsSnippet: number };
  };
}

// The SQL editor learns the sandbox schema at runtime; the completion
// provider reads this module-level list so it always serves the latest one.
let sqlSchemaCompletions: CompletionSpec[] = [];
const registeredLanguages = new Set<string>();

function registerCompletions(monaco: MonacoLike, language: string): void {
  if (registeredLanguages.has(language)) return;
  registeredLanguages.add(language);
  const builtins = language === "java" ? JAVA_COMPLETIONS : SQL_COMPLETIONS;

  monaco.languages.registerCompletionItemProvider(language, {
    triggerCharacters: ["."],
    provideCompletionItems(
      model: { getWordUntilPosition: (p: unknown) => { startColumn: number; endColumn: number } },
      position: { lineNumber: number }
    ) {
      const word = model.getWordUntilPosition(position);
      const range = {
        startLineNumber: position.lineNumber,
        endLineNumber: position.lineNumber,
        startColumn: word.startColumn,
        endColumn: word.endColumn,
      };
      const items = language === "sql" ? builtins.concat(sqlSchemaCompletions) : builtins;
      return {
        suggestions: items.map((item) => ({
          label: item.label,
          kind:
            monaco.languages.CompletionItemKind[item.kind] ??
            monaco.languages.CompletionItemKind.Text,
          detail: item.detail,
          documentation: item.documentation,
          insertText: item.insertText ?? item.label,
          insertTextRules:
            item.kind === "Snippet"
              ? monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet
              : undefined,
          range,
        })),
      };
    },
  });
}

export function CodeEditor({
  value,
  onChange,
  language = "java",
  height = 380,
  template,
  extraCompletions,
}: {
  value: string;
  onChange: (v: string) => void;
  language?: "java" | "sql" | "typescript";
  height?: number;
  template?: string;
  /** Extra suggestions (e.g. SQL tables/columns from the live schema). */
  extraCompletions?: CompletionSpec[];
}) {
  useEffect(() => {
    if (language === "sql") sqlSchemaCompletions = extraCompletions ?? [];
  }, [language, extraCompletions]);

  return (
    <div className="overflow-hidden rounded-lg border border-slate-300 dark:border-slate-600 bg-slate-900">
      <Editor
        height={height}
        language={language}
        value={value}
        onChange={(v) => onChange(v ?? "")}
        onMount={(_editor, monaco) =>
          registerCompletions(monaco as unknown as MonacoLike, language)
        }
        theme="vs-dark"
        options={{
          minimap: { enabled: false },
          fontSize: 13,
          lineNumbers: "on",
          scrollBeyondLastLine: false,
          tabSize: 4,
          wordWrap: "on",
          automaticLayout: true,
          quickSuggestions: { other: true, comments: false, strings: false },
          suggestOnTriggerCharacters: true,
          wordBasedSuggestions: "currentDocument",
          acceptSuggestionOnEnter: "on",
          snippetSuggestions: "inline",
          fixedOverflowWidgets: true,
        }}
        loading={
          <div className="flex h-full items-center justify-center text-sm text-slate-400 dark:text-slate-500">
            Loading editor…
          </div>
        }
      />
      {template && value === "" ? (
        <button
          type="button"
          onClick={() => onChange(template)}
          className="w-full border-t border-slate-700 bg-slate-800 px-3 py-1.5 text-left text-xs text-slate-300 hover:bg-slate-700"
        >
          Insert starter template
        </button>
      ) : null}
    </div>
  );
}

export { JAVA_TEMPLATE };
