"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { AlertTriangle, ExternalLink, GitBranch, Minus, Network, Plus } from "lucide-react";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";

interface TreeNode {
  id: string;
  label: string;
  count?: number;
  unit?: string;
  note?: string;
  href?: string;
  children?: TreeNode[];
}

function countLeaves(node: TreeNode): number {
  if (!node.children?.length) return 1;
  return node.children.reduce((sum, child) => sum + countLeaves(child), 0);
}

function NodeCard({
  node,
  depth,
  openIds,
  toggle,
}: {
  node: TreeNode;
  depth: number;
  openIds: Set<string>;
  toggle: (id: string) => void;
}) {
  const hasChildren = !!node.children?.length;
  const open = openIds.has(node.id);

  const style =
    depth === 1
      ? "border-indigo-300 dark:border-indigo-800 bg-indigo-50 dark:bg-indigo-950 hover:border-indigo-400 dark:hover:border-indigo-500"
      : depth === 2
        ? "border-violet-200 dark:border-violet-800 bg-white dark:bg-slate-900 hover:border-violet-400"
        : "border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 hover:border-indigo-400 dark:hover:border-indigo-500";

  return (
    <div
      onClick={() => hasChildren && toggle(node.id)}
      className={cn("cursor-pointer rounded-lg border p-2.5 transition", style)}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex min-w-0 items-start gap-2">
          {hasChildren ? (
            open ? (
              <Minus className="mt-0.5 h-3.5 w-3.5 shrink-0 text-indigo-600 dark:text-indigo-400" />
            ) : (
              <Plus className="mt-0.5 h-3.5 w-3.5 shrink-0 text-indigo-600 dark:text-indigo-400" />
            )
          ) : (
            <GitBranch className="mt-0.5 h-3.5 w-3.5 shrink-0 text-slate-400 dark:text-slate-500" />
          )}
          <div className="min-w-0">
            <div className="flex flex-wrap items-baseline gap-x-2 gap-y-0.5">
              <span className="text-[13px] font-semibold leading-snug text-slate-900 dark:text-slate-100">{node.label}</span>
              {node.count !== undefined ? (
                <span className="shrink-0 rounded-full bg-indigo-100 dark:bg-indigo-900 px-1.5 py-0.5 text-[10px] font-bold text-indigo-800 dark:text-indigo-300">
                  {node.count} {node.unit ?? ""}
                </span>
              ) : null}
            </div>
            {node.note ? (
              <p className="mt-0.5 text-[11px] leading-snug text-slate-500 dark:text-slate-400">{node.note}</p>
            ) : null}
          </div>
        </div>

        {/* Leaf nodes navigate with the whole card; branch nodes get an inner link so
            clicking the card only expands, and the arrow opens the topic page. */}
        {node.href ? (
          hasChildren ? (
            <Link
              href={node.href}
              onClick={(e) => e.stopPropagation()}
              className="mt-0.5 flex shrink-0 items-center gap-0.5 rounded px-1.5 py-0.5 text-[11px] font-medium text-indigo-600 dark:text-indigo-400 hover:bg-indigo-100 dark:hover:bg-indigo-900"
            >
              topic <ExternalLink className="h-3 w-3" />
            </Link>
          ) : (
            <ExternalLink className="mt-0.5 h-3.5 w-3.5 shrink-0 text-indigo-500 dark:text-indigo-400" />
          )
        ) : null}
      </div>
    </div>
  );
}

function TreeBranch({
  node,
  depth,
  openIds,
  toggle,
}: {
  node: TreeNode;
  depth: number;
  openIds: Set<string>;
  toggle: (id: string) => void;
}) {
  const hasChildren = !!node.children?.length;
  const open = openIds.has(node.id);

  const card =
    depth === 0 ? (
      <NodeCard node={node} depth={depth} openIds={openIds} toggle={toggle} />
    ) : node.href && !hasChildren ? (
      <Link href={node.href}>
        <NodeCard node={node} depth={depth} openIds={openIds} toggle={toggle} />
      </Link>
    ) : (
      <NodeCard node={node} depth={depth} openIds={openIds} toggle={toggle} />
    );

  return (
    <div className={cn(depth > 0 && "ml-3 border-l-2 border-slate-200 dark:border-slate-700 pl-3")}>
      {card}
      {hasChildren && open ? (
        <div className="mt-1.5 space-y-1.5">
          {node.children!.map((child) => (
            <TreeBranch key={child.id} node={child} depth={depth + 1} openIds={openIds} toggle={toggle} />
          ))}
        </div>
      ) : null}
    </div>
  );
}

export default function MindMapPage() {
  const [root, setRoot] = useState<TreeNode | null>(null);
  const [openIds, setOpenIds] = useState<Set<string>>(new Set());
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .get<{ root: TreeNode }>("/api/mindmap")
      .then((r) => {
        setRoot(r.root);
        // Expand the root and its six branches by default.
        setOpenIds(new Set([r.root.id, ...(r.root.children ?? []).map((c) => c.id)]));
      })
      .catch((e) => setError(e.message));
  }, []);

  const toggle = (id: string) =>
    setOpenIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });

  const expandAll = () => {
    if (!root) return;
    const ids = new Set<string>();
    const collect = (n: TreeNode) => {
      if (n.children?.length) {
        ids.add(n.id);
        n.children.forEach(collect);
      }
    };
    collect(root);
    setOpenIds(ids);
  };

  const leafCount = useMemo(() => (root ? countLeaves(root) : 0), [root]);

  return (
    <div className="space-y-6">
      <header>
        <div className="flex items-center gap-2">
          <Network className="h-6 w-6 text-indigo-600 dark:text-indigo-400" />
          <h1 className="text-2xl font-bold">Mind Map</h1>
        </div>
        <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">
          The whole gym in one tree — {leafCount} study areas. Click a node to expand it; the{" "}
          <span className="font-medium text-indigo-700 dark:text-indigo-400">topic ↗</span> link (or any leaf) opens that
          exact topic. Counts come live from the content banks, so they are always truthful.
        </p>
      </header>

      {error ? (
        <div className="flex items-center gap-2 rounded-lg border border-rose-200 dark:border-rose-800 bg-rose-50 dark:bg-rose-950 p-3 text-sm text-rose-800 dark:text-rose-400">
          <AlertTriangle className="h-4 w-4" /> {error}
        </div>
      ) : null}

      {root ? (
        <>
          <div className="flex flex-wrap gap-1.5">
            <button
              onClick={expandAll}
              className="flex items-center gap-1.5 rounded-full bg-indigo-600 px-3 py-1 text-xs font-medium text-white hover:bg-indigo-700"
            >
              <Plus className="h-3 w-3" /> Expand everything
            </button>
            <button
              onClick={() => setOpenIds(new Set([root.id, ...(root.children ?? []).map((c) => c.id)]))}
              className="flex items-center gap-1.5 rounded-full border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-1 text-xs font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
            >
              <Minus className="h-3 w-3" /> Collapse to branches
            </button>
          </div>

          <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-4">
            <div className="rounded-xl bg-gradient-to-br from-indigo-600 to-violet-600 p-3 text-center text-white">
              <p className="text-sm font-bold">{root.label}</p>
              {root.note ? (
                <p className="mt-0.5 text-[11px] text-indigo-100">{root.note}</p>
              ) : null}
            </div>
            <div className="mt-3 space-y-1.5">
              {(root.children ?? []).map((branch) => (
                <TreeBranch key={branch.id} node={branch} depth={1} openIds={openIds} toggle={toggle} />
              ))}
            </div>
          </div>

          <p className="text-xs text-slate-500 dark:text-slate-400">
            Tip: nodes with <strong>+</strong> / <strong>−</strong> expand in place; everything else
            jumps straight to its page. The tree mirrors the sidebar labs one-to-one.
          </p>
        </>
      ) : !error ? (
        <div className="flex h-64 items-center justify-center rounded-xl border-2 border-dashed border-slate-300 dark:border-slate-600 text-sm text-slate-500 dark:text-slate-400">
          Loading the mind map…
        </div>
      ) : null}
    </div>
  );
}
