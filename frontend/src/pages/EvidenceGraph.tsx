import React from 'react';
import { ReactFlow, Controls, Background, useNodesState, useEdgesState } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { motion } from 'framer-motion';
import { AlertTriangle } from 'lucide-react';

const initialNodes = [
  { id: 'emp-12', position: { x: 300, y: 30 }, data: { label: '⚠️ EMP-12 (Focal)' }, className: 'node-focal' },
  { id: 'po-44', position: { x: 100, y: 180 }, data: { label: '📋 PO-44' }, className: 'node-po' },
  { id: 'inv-88', position: { x: 300, y: 300 }, data: { label: '🧾 INV-88' }, className: 'node-invoice' },
  { id: 'txn-99', position: { x: 500, y: 180 }, data: { label: '💳 TXN-99' }, className: 'node-transaction' },
  { id: 'ven-07', position: { x: 100, y: 330 }, data: { label: '🏭 VEN-07 (New)' }, className: 'node-vendor' },
];

const initialEdges = [
  { id: 'e1', source: 'emp-12', target: 'po-44', label: 'RAISED', animated: true, style: { stroke: '#ef4444', strokeWidth: 2 } },
  { id: 'e2', source: 'emp-12', target: 'txn-99', label: 'APPROVED', animated: true, style: { stroke: '#ef4444', strokeWidth: 2 } },
  { id: 'e3', source: 'txn-99', target: 'inv-88', label: 'PAYS' },
  { id: 'e4', source: 'inv-88', target: 'po-44', label: 'BILLED_AGAINST' },
  { id: 'e5', source: 'po-44', target: 'ven-07', label: 'ISSUED_TO' },
];

export function EvidenceGraph() {
  const [nodes, , onNodesChange] = useNodesState(initialNodes);
  const [edges, , onEdgesChange] = useEdgesState(initialEdges);

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col space-y-4">
      <header className="flex items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-text">Evidence Graph</h1>
          <p className="text-textMuted">Isolated subgraph showing compliance violation pathways</p>
        </div>
        <div className="ml-auto flex items-center gap-2 px-4 py-2 bg-red-500/10 border border-red-500/20 rounded-xl">
          <AlertTriangle className="w-4 h-4 text-red-400" />
          <span className="text-sm font-medium text-red-400">Segregation of Duties Violation Detected</span>
        </div>
      </header>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="flex-1 glass-panel overflow-hidden"
      >
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          fitView
          className="bg-slate-900/50"
        >
          <Controls />
          <Background color="#334155" gap={16} />
        </ReactFlow>
      </motion.div>
    </div>
  );
}
