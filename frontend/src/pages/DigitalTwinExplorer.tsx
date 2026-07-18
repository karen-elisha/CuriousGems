import React, { useCallback } from 'react';
import { ReactFlow, MiniMap, Controls, Background, useNodesState, useEdgesState } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { motion } from 'framer-motion';
import { Search } from 'lucide-react';

const initialNodes = [
  { id: '1', position: { x: 250, y: 5 }, data: { label: 'Department: Engineering' }, className: 'glass-card' },
  { id: '2', position: { x: 100, y: 100 }, data: { label: 'Employee: Alice' }, className: 'glass-card' },
  { id: '3', position: { x: 400, y: 100 }, data: { label: 'Employee: Bob' }, className: 'glass-card' },
  { id: '4', position: { x: 400, y: 200 }, data: { label: 'PO-10023' }, className: 'glass-card border-amber-500/50' },
  { id: '5', position: { x: 400, y: 300 }, data: { label: 'Vendor: CloudCo' }, className: 'glass-card border-emerald-500/50' },
];

const initialEdges = [
  { id: 'e1-2', source: '2', target: '1', animated: true },
  { id: 'e1-3', source: '3', target: '1', animated: true },
  { id: 'e3-4', source: '3', target: '4', label: 'RAISED' },
  { id: 'e4-5', source: '4', target: '5', label: 'ISSUED_TO' },
];

export function DigitalTwinExplorer() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col space-y-4">
      <header className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-text">Digital Twin Explorer</h1>
          <p className="text-textMuted">Interactive topology of your entire ecosystem</p>
        </div>
        <div className="relative w-72">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-textMuted" />
          <input 
            type="text" 
            placeholder="Search entities (e.g. V-1002)..." 
            className="input-field pl-10"
          />
        </div>
      </header>

      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="flex-1 glass-panel overflow-hidden relative"
      >
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          fitView
          className="bg-slate-900/50"
        >
          <Controls className="bg-surface border-surfaceBorder fill-text" />
          <MiniMap className="bg-surface border-surfaceBorder mask-image-rounded" maskColor="rgba(15, 23, 42, 0.8)" />
          <Background color="#334155" gap={16} size={1} />
        </ReactFlow>
      </motion.div>
    </div>
  );
}
