import { useEffect, useState } from 'react';
import ReactFlow, { Background, Controls, Node, Edge } from 'reactflow';
import 'reactflow/dist/style.css';
import axios from 'axios';

function App() {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);

  useEffect(() => {
    axios.get('http://localhost:5001/api/commits')
      .then(res => {
        setNodes(res.data.nodes);
        setEdges(res.data.edges);
      })
      .catch(err => console.error("Error fetching commits:", err));
  }, []);

  return (
    <div style={{ height: '100vh', width: '100vw', backgroundColor: '#f8fafc' }}>
      <div style={{ position: 'absolute', zIndex: 10, padding: '20px', fontFamily: 'sans-serif' }}>
        <h1 style={{ margin: 0, color: '#1e293b' }}>PyGit Visualizer</h1>
        <p style={{ color: '#64748b', margin: '5px 0' }}>Live interactive view of your .pygit object DAG</p>
      </div>
      <ReactFlow nodes={nodes} edges={edges} fitView>
        <Background gap={20} color="#cbd5e1" />
        <Controls />
      </ReactFlow>
    </div>
  );
}

export default App;