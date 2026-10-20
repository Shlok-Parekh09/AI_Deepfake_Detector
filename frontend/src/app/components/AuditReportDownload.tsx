import { useState } from 'react';
import { Download, FileText } from 'lucide-react';
import type { AuditEvidence } from './AudioReview';

export function AuditReportDownload({ pdf, filename, evidence, error }: {
  pdf?: string; filename?: string; evidence: AuditEvidence | null; error?: string;
}) {
  const [downloadError, setDownloadError] = useState('');
  function download() {
    try {
      if (!pdf) return;
      const data = Uint8Array.from(atob(pdf), char => char.charCodeAt(0));
      const url = URL.createObjectURL(new Blob([data], { type: 'application/pdf' }));
      const link = document.createElement('a'); link.href = url; link.download = filename || 'media-assessment.pdf';
      document.body.appendChild(link); link.click(); link.remove();
      window.setTimeout(() => URL.revokeObjectURL(url), 1000);
      setDownloadError('');
    } catch { setDownloadError('The report could not be downloaded. Please retry the scan.'); }
  }
  return <section className="mt-6 rounded-xl border border-gray-800 bg-[#12121f] p-4 sm:p-5">
    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div className="flex items-start gap-3 min-w-0"><FileText size={20} className="mt-0.5 text-gray-400 shrink-0" />
        <div><h3 className="text-sm font-semibold text-white">Technical audit report</h3>
          <p className="text-xs text-gray-400 leading-5 mt-1">Two pages · English · Times New Roman. Includes evidence, model identity, method, coverage, limitations, and reviewer sign-off.</p>
        </div>
      </div>
      <button type="button" onClick={download} disabled={!pdf} className="inline-flex min-h-11 shrink-0 items-center justify-center gap-2 rounded-lg border border-gray-600 px-4 py-2 text-sm text-white hover:bg-gray-800 disabled:opacity-40 disabled:cursor-not-allowed focus-visible:outline focus-visible:outline-2 focus-visible:outline-cyan-400"><Download size={16} />Download PDF</button>
    </div>
    {evidence?.report_id && <p className="mt-3 text-[10px] text-gray-500 font-mono break-all">Report {evidence.report_id} · Automated assessment; unsigned</p>}
    {(error || downloadError || !pdf) && <p role="status" className="text-xs text-orange-300 mt-3">{downloadError || error || 'No PDF is attached to this older scan. Run a new scan to generate its report.'}</p>}
  </section>;
}
