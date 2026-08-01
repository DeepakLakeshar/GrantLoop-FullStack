import { FileText, Download } from "lucide-react";
import { StatusBadge } from "@/components/shared/StatusBadge";
import type { GrantLoopDocument } from "@/types/entities";
import { formatDate } from "@/lib/format";

interface DocumentsProps {
  documents: GrantLoopDocument[];
}

/** "Gallery" section — photo-type Documents only. */
export function DocumentGallery({ documents }: DocumentsProps) {
  const photos = documents.filter((d) => d.document_type === "photo");
  if (photos.length === 0) return null;

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
      {photos.map((doc) => (
        <div key={doc.id} className="aspect-square rounded-lg overflow-hidden border border-outline-variant bg-surface-container-high">
          <img src={doc.file_url} alt="" className="w-full h-full object-cover" />
        </div>
      ))}
    </div>
  );
}

/** "Documents" section — everything that isn't a photo (invoices,
 * completion/inspection reports, certificates, etc). document_type is a
 * plain string per Architecture Freeze v1.0 — new types render fine
 * without a code change. */
export function DocumentList({ documents }: DocumentsProps) {
  const files = documents.filter((d) => d.document_type !== "photo");
  if (files.length === 0) return null;

  return (
    <div className="space-y-3">
      {files.map((doc) => (
        <div
          key={doc.id}
          className="flex items-center gap-4 p-4 border border-outline-variant rounded-lg hover:bg-surface-container-low transition-colors"
        >
          <FileText className="w-6 h-6 text-on-surface-variant shrink-0" />
          <div className="flex-1 min-w-0">
            <p className="font-body-md font-bold text-primary capitalize">{doc.document_type.replace(/_/g, " ")}</p>
            <p className="text-data-table text-on-surface-variant">Uploaded {formatDate(doc.uploaded_at)}</p>
          </div>
          <StatusBadge status={doc.status} />
          <a href={doc.file_url} target="_blank" rel="noreferrer" aria-label="Download document">
            <Download className="w-5 h-5 text-on-surface-variant hover:text-primary transition-colors" />
          </a>
        </div>
      ))}
    </div>
  );
}
