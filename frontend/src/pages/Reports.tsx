import { useState } from 'react';
import { FileText, Download, Loader2, BarChart3, ShieldCheck, Building2, AlertTriangle } from 'lucide-react';
import { motion } from 'framer-motion';
import apiClient from '../api/client';

interface ReportConfig {
  id: string;
  title: string;
  description: string;
  endpoint: string;
  method: 'GET' | 'POST';
  icon: React.ElementType;
  color: string;
  bgColor: string;
}

const REPORT_TYPES: ReportConfig[] = [
  {
    id: 'executive',
    title: 'Executive Report',
    description: 'Full org-level performance, risk narrative, and compliance health overview.',
    endpoint: '/reports/executive',
    method: 'GET',
    icon: BarChart3,
    color: 'text-cyan-500',
    bgColor: 'bg-cyan-500/10',
  },
  {
    id: 'compliance',
    title: 'Compliance Report',
    description: 'System-wide policy violations and anomaly narrative powered by Gemma.',
    endpoint: '/reports/compliance',
    method: 'POST',
    icon: ShieldCheck,
    color: 'text-emerald-500',
    bgColor: 'bg-emerald-500/10',
  },
  {
    id: 'risk',
    title: 'Risk Summary',
    description: 'Top-risk entities with propagated scores and mitigation priorities.',
    endpoint: '/reports/risk',
    method: 'GET',
    icon: AlertTriangle,
    color: 'text-amber-500',
    bgColor: 'bg-amber-500/10',
  },
];

function generatePDF(title: string, content: string, metrics: any) {
  // Build a styled HTML document for PDF printing
  const htmlContent = `
<!DOCTYPE html>
<html>
<head>
  <title>${title} - VeriGem</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Outfit:wght@700&display=swap');
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Inter', system-ui, sans-serif; color: #0F172A; padding: 48px; line-height: 1.7; }
    .header { border-bottom: 3px solid #3B82F6; padding-bottom: 20px; margin-bottom: 32px; }
    .header h1 { font-family: 'Outfit', sans-serif; font-size: 28px; color: #0F172A; }
    .header p { color: #64748B; margin-top: 4px; font-size: 14px; }
    .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin-bottom: 32px; }
    .metric { background: #F1F5F9; border: 1px solid #CBD5E1; border-radius: 8px; padding: 16px; }
    .metric .label { font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #64748B; font-weight: 600; }
    .metric .value { font-size: 22px; font-weight: 700; color: #0F172A; margin-top: 4px; }
    .report-content { white-space: pre-wrap; font-size: 14px; line-height: 1.8; color: #1E293B; }
    .report-content h1, .report-content h2, .report-content h3 { margin-top: 20px; margin-bottom: 8px; color: #0F172A; }
    .report-content strong { font-weight: 700; }
    .report-content ul, .report-content ol { padding-left: 24px; margin: 8px 0; }
    .footer { margin-top: 48px; padding-top: 16px; border-top: 1px solid #E2E8F0; color: #94A3B8; font-size: 11px; text-align: center; }
    @media print { body { padding: 24px; } }
  </style>
</head>
<body>
  <div class="header">
    <h1>VeriGem — ${title}</h1>
    <p>Generated: ${new Date().toLocaleString()}</p>
  </div>
  ${metrics ? `<div class="metrics">${Object.entries(metrics).filter(([k, v]) => typeof v === 'number' || typeof v === 'string').map(([k, v]) => `<div class="metric"><div class="label">${k.replace(/_/g, ' ')}</div><div class="value">${v}</div></div>`).join('')}</div>` : ''}
  <div class="report-content">${content.replace(/\n/g, '<br/>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/^## (.*?)$/gm, '<h2>$1</h2>').replace(/^### (.*?)$/gm, '<h3>$1</h3>').replace(/^# (.*?)$/gm, '<h1>$1</h1>')}</div>
  <div class="footer">VeriGem Financial Digital Twin — Powered by Google Gemma (gemma-3-27b-it)</div>
</body>
</html>`;

  const blob = new Blob([htmlContent], { type: 'text/html' });
  const url = URL.createObjectURL(blob);
  const printWindow = window.open(url, '_blank');
  if (printWindow) {
    printWindow.addEventListener('load', () => {
      printWindow.print();
    });
  }
}

export function Reports() {
  const [reports, setReports] = useState<Record<string, { loading: boolean; data: any; error: string }>>({});

  const generateReport = async (config: ReportConfig) => {
    setReports(prev => ({
      ...prev,
      [config.id]: { loading: true, data: null, error: '' },
    }));

    try {
      const res = config.method === 'GET'
        ? await apiClient.get(config.endpoint)
        : await apiClient.post(config.endpoint);

      setReports(prev => ({
        ...prev,
        [config.id]: { loading: false, data: res.data, error: '' },
      }));
    } catch (err: any) {
      setReports(prev => ({
        ...prev,
        [config.id]: { loading: false, data: null, error: err.response?.data?.detail || 'Report generation failed.' },
      }));
    }
  };

  const handleDownloadPDF = (config: ReportConfig) => {
    const report = reports[config.id];
    if (!report?.data) return;
    generatePDF(config.title, report.data.report || 'No narrative generated.', report.data.metrics);
  };

  return (
    <div className="space-y-6">
      <header className="mb-8">
        <motion.h1
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-4xl font-bold text-text font-display tracking-tight"
        >
          Generated Reports
        </motion.h1>
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="text-textMuted text-lg mt-2"
        >
          Executive summaries authored by Gemma — click Generate, then download as PDF
        </motion.p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {REPORT_TYPES.map((config, i) => {
          const report = reports[config.id];
          return (
            <motion.div
              key={config.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className="glass-card p-6 flex flex-col justify-between"
            >
              <div>
                <div className="flex justify-between items-start mb-4">
                  <div className={`p-3 rounded-lg ${config.bgColor}`}>
                    <config.icon className={`w-6 h-6 ${config.color}`} />
                  </div>
                  {report?.data && (
                    <span className="text-xs font-medium px-2 py-1 bg-emerald-500/10 text-emerald-500 rounded-full border border-emerald-500/20">
                      ✓ Ready
                    </span>
                  )}
                </div>
                <h3 className="font-bold text-lg text-text">{config.title}</h3>
                <p className="text-sm text-textMuted mt-1 leading-relaxed">{config.description}</p>
              </div>

              {report?.error && (
                <div className="mt-4 p-3 bg-rose-500/10 text-rose-500 text-sm rounded-lg border border-rose-500/20">
                  {report.error}
                </div>
              )}

              <div className="mt-6 flex gap-2">
                <button
                  onClick={() => generateReport(config)}
                  disabled={report?.loading}
                  className="btn-primary flex-1 flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {report?.loading ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <FileText className="w-4 h-4" />
                      Generate
                    </>
                  )}
                </button>
                {report?.data && (
                  <button
                    onClick={() => handleDownloadPDF(config)}
                    className="btn-secondary flex items-center gap-2"
                  >
                    <Download className="w-4 h-4" />
                    PDF
                  </button>
                )}
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Render generated report content */}
      {REPORT_TYPES.map(config => {
        const report = reports[config.id];
        if (!report?.data) return null;
        return (
          <motion.div
            key={`content-${config.id}`}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-panel p-8"
          >
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-lg ${config.bgColor}`}>
                  <config.icon className={`w-5 h-5 ${config.color}`} />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-text font-display">{config.title}</h3>
                  <p className="text-xs text-textMuted">Generated at {new Date(report.data.generated_at).toLocaleString()}</p>
                </div>
              </div>
              <button
                onClick={() => handleDownloadPDF(config)}
                className="btn-secondary flex items-center gap-2 text-sm"
              >
                <Download className="w-4 h-4" />
                Download PDF
              </button>
            </div>

            {/* Metrics summary */}
            {report.data.metrics && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
                {Object.entries(report.data.metrics)
                  .filter(([_, v]) => typeof v === 'number' || typeof v === 'string')
                  .slice(0, 8)
                  .map(([key, value]) => (
                    <div key={key} className="p-3 bg-surfaceHover rounded-lg border border-surfaceBorder">
                      <p className="text-xs text-textMuted uppercase tracking-wider font-semibold">{key.replace(/_/g, ' ')}</p>
                      <p className="text-lg font-bold text-text mt-1">{String(value)}</p>
                    </div>
                  ))}
              </div>
            )}

            {/* Report narrative */}
            <div className="prose prose-sm max-w-none text-text">
              <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed text-text bg-transparent p-0 border-none">
                {report.data.report}
              </pre>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}
