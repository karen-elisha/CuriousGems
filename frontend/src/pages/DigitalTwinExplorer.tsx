import React from 'react';
import { ReactFlow, MiniMap, Controls, Background, useNodesState, useEdgesState } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { motion } from 'framer-motion';
import { Search, SlidersHorizontal } from 'lucide-react';

const initialNodes = [
<<<<<<< HEAD
  { id: '1', position: { x: 250, y: 5 }, data: { label: 'Department: Engineering' }, className: 'glass-card border-cyan-500/30 bg-cyan-500/10 shadow-[0_0_15px_rgba(6,182,212,0.15)] font-medium' },
  { id: '2', position: { x: 100, y: 100 }, data: { label: 'Employee: Alice' }, className: 'glass-card border-violet-500/30 bg-violet-500/10 shadow-[0_0_15px_rgba(139,92,246,0.15)] font-medium' },
  { id: '3', position: { x: 400, y: 100 }, data: { label: 'Employee: Bob' }, className: 'glass-card border-violet-500/30 bg-violet-500/10 shadow-[0_0_15px_rgba(139,92,246,0.15)] font-medium' },
  { id: '4', position: { x: 400, y: 200 }, data: { label: 'PO-10023' }, className: 'glass-card border-amber-500/50 bg-amber-500/10 shadow-[0_0_15px_rgba(245,158,11,0.2)] font-medium' },
  { id: '5', position: { x: 400, y: 300 }, data: { label: 'Vendor: CloudCo' }, className: 'glass-card border-emerald-500/50 bg-emerald-500/10 shadow-[0_0_15px_rgba(16,185,129,0.2)] font-medium' },
];

const initialEdges = [
  { id: 'e1-2', source: '2', target: '1', animated: true, style: { stroke: '#06B6D4', strokeWidth: 2 } },
  { id: 'e1-3', source: '3', target: '1', animated: true, style: { stroke: '#06B6D4', strokeWidth: 2 } },
  { id: 'e3-4', source: '3', target: '4', label: 'RAISED', style: { stroke: '#8B5CF6', strokeWidth: 2 }, labelStyle: { fill: '#F8FAFC', fontWeight: 600, fontSize: 12 }, labelBgStyle: { fill: 'rgba(15, 23, 42, 0.8)' } },
  { id: 'e4-5', source: '4', target: '5', label: 'ISSUED_TO', style: { stroke: '#8B5CF6', strokeWidth: 2 }, labelStyle: { fill: '#F8FAFC', fontWeight: 600, fontSize: 12 }, labelBgStyle: { fill: 'rgba(15, 23, 42, 0.8)' } },
=======
  { id: 'dept-1', position: { x: 300, y: 0 }, data: { label: '🏢 Engineering Dept' }, className: 'node-department' },
  { id: 'emp-1', position: { x: 100, y: 120 }, data: { label: '👤 Alice Chen' }, className: 'node-employee' },
  { id: 'emp-2', position: { x: 500, y: 120 }, data: { label: '👤 Bob Kumar' }, className: 'node-employee' },
  { id: 'ven-1', position: { x: 50, y: 300 }, data: { label: '🏭 CloudCo Ltd' }, className: 'node-vendor' },
  { id: 'ven-2', position: { x: 550, y: 300 }, data: { label: '🏭 DataServe Inc' }, className: 'node-vendor' },
  { id: 'po-1', position: { x: 100, y: 240 }, data: { label: '📋 PO-10023' }, className: 'node-po' },
  { id: 'po-2', position: { x: 500, y: 240 }, data: { label: '📋 PO-10045' }, className: 'node-po' },
  { id: 'inv-1', position: { x: 300, y: 360 }, data: { label: '🧾 INV-5501' }, className: 'node-invoice' },
  { id: 'txn-1', position: { x: 300, y: 460 }, data: { label: '💳 TXN-9901' }, className: 'node-transaction' },
];

const initialEdges = [
  { id: 'e-emp1-dept', source: 'emp-1', target: 'dept-1', label: 'BELONGS_TO', animated: true },
  { id: 'e-emp2-dept', source: 'emp-2', target: 'dept-1', label: 'BELONGS_TO', animated: true },
  { id: 'e-emp1-po1', source: 'emp-1', target: 'po-1', label: 'RAISED' },
  { id: 'e-emp2-po2', source: 'emp-2', target: 'po-2', label: 'RAISED' },
  { id: 'e-po1-ven1', source: 'po-1', target: 'ven-1', label: 'ISSUED_TO' },
  { id: 'e-po2-ven2', source: 'po-2', target: 'ven-2', label: 'ISSUED_TO' },
  { id: 'e-inv1-po1', source: 'inv-1', target: 'po-1', label: 'BILLED_AGAINST' },
  { id: 'e-txn1-inv1', source: 'txn-1', target: 'inv-1', label: 'PAYS' },
  { id: 'e-emp2-txn1', source: 'emp-2', target: 'txn-1', label: 'APPROVED', style: { stroke: '#ef4444', strokeWidth: 2 } },
>>>>>>> 632c496 (Update frontend)
];

export function DigitalTwinExplorer() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col space-y-6">
      <header className="flex justify-between items-end">
        <div>
<<<<<<< HEAD
          <motion.h1 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-4xl font-bold text-text font-display tracking-tight"
          >
            Digital Twin Explorer
          </motion.h1>
          <motion.p 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.1 }}
            className="text-textMuted text-lg mt-2"
          >
            Interactive topology of your entire ecosystem
          </motion.p>
=======
          <h1 className="text-3xl font-bold text-text">Digital Twin Explorer</h1>
          <p className="text-textMuted">Interactive topology of your entire ecosystem</p>
        </div>
        <div className="relative w-72">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-textMuted" />
          <input 
            type="text" 
            placeholder="Search entities (e.g. VEN-1002)..." 
            className="input-field pl-10"
          />
>>>>>>> 632c496 (Update frontend)
        </div>
        <motion.div 
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="flex items-center gap-3"
        >
          <div className="relative w-80 group">
            <div className="absolute -inset-0.5 bg-gradient-to-r from-cyan-400 to-violet-500 rounded-lg blur opacity-0 group-hover:opacity-30 transition duration-500"></div>
            <div className="relative flex items-center">
              <Search className="absolute left-3 w-5 h-5 text-cyan-400" />
              <input 
                type="text" 
                placeholder="Search entities (e.g. V-1002)..." 
                className="input-field pl-10 bg-surface/80 backdrop-blur-sm border-surfaceBorder focus:border-cyan-500/50"
              />
            </div>
          </div>
          <button className="p-2 rounded-lg bg-surfaceHover border border-surfaceBorder hover:bg-surface text-cyan-400 transition-colors shadow-sm hover:shadow-glow-primary">
            <SlidersHorizontal className="w-5 h-5" />
          </button>
        </motion.div>
      </header>

      <motion.div 
        initial={{ opacity: 0, scale: 0.98 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.3 }}
        className="flex-1 glass-panel overflow-hidden relative shadow-2xl"
      >
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          fitView
          className="bg-transparent"
        >
<<<<<<< HEAD
          <Controls className="bg-surface/80 backdrop-blur-md border border-surfaceBorder rounded-xl overflow-hidden shadow-lg [&>button]:border-b-surfaceBorder [&>button]:text-text hover:[&>button]:bg-surfaceHover fill-text" />
          <MiniMap 
            className="bg-surface/80 backdrop-blur-md border border-surfaceBorder rounded-xl shadow-lg" 
            maskColor="rgba(15, 23, 42, 0.7)" 
            nodeColor={(n) => {
              if (n.className?.includes('amber')) return '#F59E0B';
              if (n.className?.includes('emerald')) return '#10B981';
              if (n.className?.includes('violet')) return '#8B5CF6';
              return '#06B6D4';
            }} 
          />
          <Background color="rgba(148, 163, 184, 0.15)" gap={20} size={1.5} />
=======
          <Controls />
          <MiniMap maskColor="rgba(15, 23, 42, 0.8)" />
          <Background color="#334155" gap={16} size={1} />
>>>>>>> 632c496 (Update frontend)
        </ReactFlow>
      </motion.div>
    </div>
  );
}
