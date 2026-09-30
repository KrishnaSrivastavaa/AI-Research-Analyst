import type { Citation as CitationType } from "../types";

interface CitationProps {
  citation: CitationType;
}

export default function Citation({ citation }: CitationProps) {
  const pageLabel =
    citation.page_start === citation.page_end
      ? `p. ${citation.page_start}`
      : `pp. ${citation.page_start}-${citation.page_end}`;

  return (
    <div className="flex items-center gap-2 rounded-lg border border-white/[0.06] bg-white/[0.02] px-3 py-2">
      <span className="shrink-0 text-xs font-medium text-violet-400">
        [{citation.id}]
      </span>

      <span className="truncate text-xs text-slate-400">
        {citation.document_name}
      </span>

      <span className="shrink-0 text-xs text-slate-600">{pageLabel}</span>
    </div>
  );
}
