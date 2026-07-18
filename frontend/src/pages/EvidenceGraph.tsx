import React from 'react';
import { ReactFlow, MiniMap, Controls, Background } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

const initialNodes = [
  { id: '1', position: { x: 250, y: 50 }, data: { label: 'EMP-12 (Focal)' }, className: 'glass-card border-red-500 border-2' },
  { id: '2', position: { x: 100, y: 200 }, data: { label: 'PO-44' }, className: 'glass-card' },
  { id: '3', position: { x: 400, y: 200 }, data: { label: 'TXN-99' }, className: 'glass-card' },
];

const initialEdges = [
  { id: 'e1-2', source: '1', target: '2', label: 'RAISED', animated: true, style: { stroke: '#ef4444' } },
  { id: 'e1-3', source: '1', target: '3', label: 'APPROVED', animated: true, style: { stroke: '#ef4444' } },
];

export function EvidenceGraph() {
  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col space-y-4">
      <header>
        <h1 className="text-3xl font-bold text-text">Evidence Graph</h1>
        <p className="text-textMuted">Isolated subgraph showing compliance violation pathways</p>
      </header>

      <div className="flex-1 glass-panel overflow-hidden">
        <ReactFlow
          nodes={initialNodes}
          edges={initialEdges}
          fitView
          className="bg-slate-900/50"
        >
          <Controls className="bg-surface border-surfaceBorder fill-text" />
          <Background color="#334155" gap={16} />
        </ReactFlow>
      </div>
    </div>
  );
}
