import React, { useState } from 'react';
import { UploadCloud, CheckCircle2, Loader2, Database } from 'lucide-react';
import apiClient from '../api/client';
import { motion } from 'framer-motion';

const REQUIRED_FILES = [
  'employees.csv',
  'vendors.csv',
  'purchase_orders.csv',
  'invoices.csv',
  'transactions.csv',
  'audit_logs.csv'
];

export function Setup() {
  const [files, setFiles] = useState<Record<string, File>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;
    const newFiles = { ...files };
    Array.from(e.target.files).forEach(file => {
      if (REQUIRED_FILES.includes(file.name)) {
        newFiles[file.name] = file;
      }
    });
    setFiles(newFiles);
  };

  const handleInitialize = async () => {
    if (Object.keys(files).length !== REQUIRED_FILES.length) {
      setError('Please upload all 6 required CSV files.');
      return;
    }
    
    setLoading(true);
    setError('');
    
    const formData = new FormData();
    REQUIRED_FILES.forEach(name => {
      formData.append(name.split('.')[0], files[name]);
    });

    try {
      await apiClient.post('/system/upload-datasets', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      // System booted successfully, navigate to dashboard
      window.location.href = '/'; 
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to initialize Digital Twin.');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center p-6 relative overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(6,182,212,0.15),transparent_50%)] pointer-events-none"></div>
      
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-2xl glass-panel p-10 z-10 relative overflow-hidden"
      >
        <div className="absolute top-0 right-0 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl -mr-32 -mt-32 pointer-events-none"></div>
        <div className="absolute bottom-0 left-0 w-64 h-64 bg-violet-500/10 rounded-full blur-3xl -ml-32 -mb-32 pointer-events-none"></div>

        <div className="flex flex-col items-center text-center mb-8 relative z-10">
          <motion.div 
            initial={{ scale: 0.9 }}
            animate={{ scale: 1 }}
            className="w-16 h-16 bg-cyan-500/10 rounded-2xl flex items-center justify-center mb-6 border border-cyan-500/20 shadow-glow-primary"
          >
            <Database className="w-8 h-8 text-cyan-400 drop-shadow-[0_0_8px_rgba(6,182,212,0.8)]" />
          </motion.div>
          <h1 className="text-3xl font-bold text-text mb-2 font-display tracking-tight">Test Case Ingestion</h1>
          <p className="text-textMuted text-lg">
            Upload your structured datasets to initialize the validation engine.
          </p>
        </div>

        <div className="bg-surface/30 border-2 border-dashed border-surfaceBorder rounded-xl p-8 mb-8 text-center relative hover:bg-surfaceHover/50 transition-colors group cursor-pointer">
          <input 
            type="file" 
            multiple 
            accept=".csv"
            onChange={handleFileChange}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-20"
          />
          <UploadCloud className="w-12 h-12 text-cyan-400 mx-auto mb-4 group-hover:scale-110 transition-transform duration-300 drop-shadow-[0_0_8px_rgba(6,182,212,0.5)]" />
          <p className="font-bold text-text mb-1 text-lg">Drag & Drop CSV files here</p>
          <p className="text-sm text-textMuted">or click to browse</p>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-8">
          {REQUIRED_FILES.map(name => (
            <div key={name} className="flex items-center gap-3 p-4 glass-card group">
              {files[name] ? (
                <div className="relative">
                  <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 drop-shadow-[0_0_8px_rgba(52,211,153,0.8)]" />
                  <div className="absolute inset-0 bg-emerald-400/20 rounded-full animate-ping opacity-50"></div>
                </div>
              ) : (
                <div className="w-5 h-5 rounded-full border-2 border-surfaceBorder shrink-0 bg-surface/50" />
              )}
              <span className={`text-sm font-mono truncate transition-colors ${files[name] ? 'text-cyan-300 font-bold' : 'text-textMuted'}`}>
                {name}
              </span>
            </div>
          ))}
        </div>

        {error && (
          <motion.div 
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl text-rose-400 text-sm mb-6 text-center font-bold tracking-wide"
          >
            {error}
          </motion.div>
        )}

        <button 
          onClick={handleInitialize}
          disabled={loading || Object.keys(files).length !== REQUIRED_FILES.length}
          className="btn-primary w-full py-4 text-lg font-bold flex justify-center items-center gap-3 relative overflow-hidden group disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading && <div className="absolute inset-0 bg-cyan-400/20 animate-pulse"></div>}
          <div className="relative z-10 flex items-center gap-2">
            {loading ? <Loader2 className="w-6 h-6 animate-spin drop-shadow-[0_0_8px_rgba(6,182,212,0.8)]" /> : null}
            {loading ? 'Booting Validation Engine...' : 'Execute Test Cases'}
          </div>
        </button>
      </motion.div>
    </div>
  );
}
