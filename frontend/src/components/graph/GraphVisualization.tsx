import React, { useRef, useLayoutEffect, useState } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { GraphData, GraphNode, GraphEdge } from '../../types/api';

interface GraphVisualizationProps {
  data: GraphData;
  onNodeClick?: (node: GraphNode) => void;
  onEdgeClick?: (edge: GraphEdge) => void;
  selectedNode?: string | null;
  selectedEdge?: string | null;
  layout?: 'force' | 'circular' | 'hierarchical';
  showLabels?: boolean;
  nodeSize?: number;
  linkDistance?: number;
}

const NODE_TYPE_COLORS: Record<string, string> = {
  'PERSON': '#3B82F6',
  'ORGANIZATION': '#8B5CF6',
  'LOCATION': '#10B981',
  'TECHNOLOGY': '#F59E0B',
  'CONCEPT': '#EF4444',
  'DATE': '#6B7280',
  'EVENT': '#EC4899',
  'default': '#6B7280'
};

const GraphVisualization: React.FC<GraphVisualizationProps> = ({
  data,
  onNodeClick,
  onEdgeClick,
  selectedNode,
  selectedEdge,
  showLabels = true,
  nodeSize = 8,
  linkDistance = 100
}) => {
  const fgRef = useRef<any>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [size, setSize] = useState({ width: 0, height: 0 });

  useLayoutEffect(() => {
    const updateSize = () => {
      if (containerRef.current) {
        setSize({
          width: containerRef.current.offsetWidth,
          height: containerRef.current.offsetHeight,
        });
      }
    };

    window.addEventListener('resize', updateSize);
    updateSize(); // Initial size

    return () => window.removeEventListener('resize', updateSize);
  }, []);

  // Map data to react-force-graph format
  const graphData = {
    nodes: data.nodes.map(n => ({
      ...n,
      id: n.id,
      name: n.label || n.id,
      occurrence: n.occurrence || 1,
      color: NODE_TYPE_COLORS[n.type] || NODE_TYPE_COLORS.default
    })),
    links: data.edges.map(e => ({
      ...e,
      source: e.source,
      target: e.target,
      label: e.type || e.label || `${e.source}→${e.target}`,
      weight: e.weight || 1
    }))
  };

  return (
    <div ref={containerRef} className="w-full h-full" style={{ minHeight: 400, background: '#18181b' }}>
      <ForceGraph2D
        ref={fgRef}
        width={size.width}
        height={size.height}
        graphData={graphData}
        backgroundColor="#18181b"
        nodeLabel={(node: any) => `${node.name} (${node.type})`}
        linkLabel={(link: any) => link.label}
        nodeAutoColorBy="type"
        nodeCanvasObject={(node: any, ctx: any, globalScale: any) => {
          // Size node based on occurrence count
          const nodeRadius = Math.max(4, Math.min(20, (node.occurrence || 1) * 3));
          
          // Draw node as a colored circle
          ctx.beginPath();
          ctx.arc(node.x, node.y, nodeRadius, 0, 2 * Math.PI, false);
          ctx.fillStyle = node.color;
          ctx.shadowColor = '#000';
          ctx.shadowBlur = 6;
          ctx.fill();
          if (selectedNode && node.id === selectedNode) {
            ctx.lineWidth = 3;
            ctx.strokeStyle = '#fbbf24'; // gold highlight for dark mode
            ctx.stroke();
          }
          // Draw label
          if (showLabels) {
            ctx.font = `${12 / globalScale}px Sans-Serif`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'top';
            ctx.fillStyle = '#f3f4f6'; // light label for dark
            ctx.fillText(node.name, node.x, node.y + nodeRadius + 2);
          }
        }}
        linkDirectionalArrowLength={6}
        linkDirectionalArrowRelPos={1}
        linkWidth={(link: any) => (selectedEdge && link.id === selectedEdge ? 3 : Math.max(1, (link.weight || 1) * 2))}
        linkColor={(link: any) => (selectedEdge && link.id === selectedEdge ? '#fbbf24' : '#94a3b8')}
        linkCanvasObjectMode={() => showLabels ? 'after' : undefined}
        linkCanvasObject={(link: any, ctx: any, globalScale: any) => {
          if (showLabels && link.label) {
            const start = link.source;
            const end = link.target;
            if (typeof start === 'object' && typeof end === 'object') {
              const x = (start.x + end.x) / 2;
              const y = (start.y + end.y) / 2;
              ctx.save();
              ctx.font = `${10 / globalScale}px Sans-Serif`;
              ctx.fillStyle = '#a1a1aa'; // muted label for dark
              ctx.textAlign = 'center';
              ctx.textBaseline = 'middle';
              ctx.fillText(link.label, x, y);
              ctx.restore();
            }
          }
        }}
        onNodeClick={(node: any) => onNodeClick && onNodeClick(node as GraphNode)}
        onLinkClick={(link: any) => onEdgeClick && onEdgeClick(link as GraphEdge)}
        cooldownTicks={100}
        onEngineStop={() => fgRef.current && fgRef.current.zoomToFit(400, 50)}
        linkDistance={linkDistance}
        nodeRelSize={nodeSize}
        enableNodeDrag={true}
      />
    </div>
  );
};

export default GraphVisualization; 