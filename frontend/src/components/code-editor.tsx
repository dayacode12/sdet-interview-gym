"use client";

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

export function CodeEditor({
  value,
  onChange,
  language = "java",
  height = 380,
  template,
}: {
  value: string;
  onChange: (v: string) => void;
  language?: "java" | "sql" | "typescript";
  height?: number;
  template?: string;
}) {
  return (
    <div className="overflow-hidden rounded-lg border border-slate-300 bg-slate-900">
      <Editor
        height={height}
        language={language}
        value={value}
        onChange={(v) => onChange(v ?? "")}
        theme="vs-dark"
        options={{
          minimap: { enabled: false },
          fontSize: 13,
          lineNumbers: "on",
          scrollBeyondLastLine: false,
          tabSize: 4,
          wordWrap: "on",
          automaticLayout: true,
        }}
        loading={
          <div className="flex h-full items-center justify-center text-sm text-slate-400">
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
