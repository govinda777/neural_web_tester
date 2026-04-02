import React, { useEffect, useState, useMemo } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MarkerType,
  applyEdgeChanges,
  applyNodeChanges
} from 'reactflow';
import 'reactflow/dist/style.css';

const StateGraph = ({ steps }) => {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);

  useEffect(() => {
    const newNodes = [];
    const newEdges = [];
    const stateMap = new Map();

    steps.forEach((step, index) => {
      const hash = step.state_hash || 'init';

      if (!stateMap.has(hash)) {
        stateMap.set(hash, {
          id: hash,
          label: hash.substring(0, 6),
          step: step.step_number
        });

        newNodes.push({
          id: hash,
          data: { label: `Estado: ${hash.substring(0, 6)}` },
          position: { x: newNodes.length * 200, y: 100 },
          style: {
            background: hash === 'init' ? '#3b82f6' : '#fff',
            color: hash === 'init' ? '#fff' : '#000',
            border: '2px solid #3b82f6',
            borderRadius: '8px',
            fontSize: '10px',
            fontWeight: 'bold',
            width: 120
          }
        });
      }

      // Conecta o estado anterior ao atual se houver uma ação
      if (index > 0 && step.action) {
        const prevHash = steps[index - 1].state_hash || 'init';
        const edgeId = `e-${prevHash}-${hash}`;

        if (!newEdges.find(e => e.id === edgeId)) {
          newEdges.push({
            id: edgeId,
            source: prevHash,
            target: hash,
            label: step.action.type,
            animated: true,
            labelStyle: { fontSize: '8px', fill: '#6366f1', fontWeight: 'bold' },
            markerEnd: {
              type: MarkerType.ArrowClosed,
              color: '#6366f1',
            },
            style: { stroke: '#6366f1', strokeWidth: 2 }
          });
        }
      }
    });

    setNodes(newNodes);
    setEdges(newEdges);
  }, [steps]);

  const onNodesChange = (changes) => setNodes((nds) => applyNodeChanges(changes, nds));
  const onEdgesChange = (changes) => setEdges((eds) => applyEdgeChanges(changes, eds));

  return (
    <div className="h-64 w-full bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
      >
        <Background color="#cbd5e1" gap={16} />
        <Controls />
      </ReactFlow>
    </div>
  );
};

export default StateGraph;
