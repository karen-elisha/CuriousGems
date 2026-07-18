import React, { useState } from 'react';
import { UploadCloud, CheckCircle2, Loader2, Database } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../api/client';

const REQUIRED_FILES = [
  'employees.csv',
  'vendors.csv',
  'purchase_orders.csv',
  'invoices.csv',
  'transactions.csv',
  'audit_logs.csv'
];

export function Setup() {
  const navigate = useNavigate();
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
    <div className="min-h-screen bg-[var(--bg-background)] flex flex-col items-center justify-center p-6 relative overflow-hidden">
      
      <div className="w-full max-w-2xl bg-[var(--bg-surface)] border border-[var(--border-surface)] rounded-xl shadow-lg p-10 z-10">
        <div className="flex flex-col items-center text-center mb-8">
          <div className="w-16 h-16 bg-gray-50 rounded-2xl flex items-center justify-center mb-6 border border-[var(--border-surface)] shadow-sm">
            <Database className="w-8 h-8 text-[var(--color-primary)]" />
          </div>
          <h1 className="text-3xl font-bold text-[var(--text-main)] mb-2 tracking-tight">Test Case Ingestion</h1>
          <p className="text-[var(--text-muted)]">
            Upload your structured datasets to initialize the validation engine.
          </p>
        </div>

        <div className="bg-gray-50 border-2 border-dashed border-[var(--border-surface)] rounded-xl p-8 mb-8 text-center relative hover:bg-gray-100 transition-colors">
          <input 
            type="file" 
            multiple 
            accept=".csv"
            onChange={handleFileChange}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          />
          <UploadCloud className="w-10 h-10 text-[var(--text-muted)] mx-auto mb-4" />
          <p className="font-medium text-[var(--text-main)] mb-1">Drag & Drop CSV files here</p>
          <p className="text-sm text-[var(--text-muted)]">or click to browse</p>
        </div>

        <div className="grid grid-cols-2 gap-3 mb-8">
          {REQUIRED_FILES.map(name => (
            <div key={name} className="flex items-center gap-3 p-3 bg-white border border-[var(--border-surface)] rounded-lg shadow-sm">
              {files[name] ? (
                <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
              ) : (
                <div className="w-5 h-5 rounded-full border-2 border-[var(--border-surface)] shrink-0 bg-gray-50" />
              )}
              <span className={`text-sm font-mono truncate ${files[name] ? 'text-[var(--text-main)] font-medium' : 'text-[var(--text-muted)]'}`}>
                {name}
              </span>
            </div>
          ))}
        </div>

        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm mb-6 text-center font-medium">
            {error}
          </div>
        )}

        <button 
          onClick={handleInitialize}
          disabled={loading || Object.keys(files).length !== REQUIRED_FILES.length}
          className="w-full py-4 text-lg bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] text-white font-medium rounded-xl transition-colors shadow-sm flex items-center justify-center gap-3 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : null}
          {loading ? 'Booting Validation Engine...' : 'Execute Test Cases'}
        </button>
      </div>
    </div>
  );
}
