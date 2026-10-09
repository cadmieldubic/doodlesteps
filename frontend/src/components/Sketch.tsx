import { useId } from 'react';
import type { Lesson, Stroke } from '../schema';

const palette = { graphite: '#514752', lavender: '#9e7cc0', peach: '#d99473', mint: '#75a592' } as const;

/** Geometry comes only from the validated blueprint. No markup or model paths enter the DOM. */
function Primitive({ stroke, muted, highlighted, printable }: { stroke: Stroke; muted: boolean; highlighted: boolean; printable: boolean }) {
  const color = printable ? '#39323d' : muted ? '#c9c4d1' : highlighted ? '#9270b7' : palette[stroke.color];
  const fill = 'fill' in stroke && stroke.fill !== 'none' ? printable ? '#efedf0' : muted ? '#efedf2' : palette[stroke.fill] : 'none';
  const common = {
    'data-stroke-id': stroke.id,
    'data-stroke-state': muted ? 'previous' : highlighted ? 'current' : 'final',
    stroke: color, strokeWidth: stroke.width, opacity: muted ? stroke.opacity * 0.62 : stroke.opacity,
    strokeLinecap: 'round' as const, strokeLinejoin: 'round' as const, fill,
  };
  switch (stroke.kind) {
    case 'line': return <line {...common} x1={stroke.start.x} y1={stroke.start.y} x2={stroke.end.x} y2={stroke.end.y} />;
    case 'polyline': return <polyline {...common} points={stroke.points.map((point) => `${point.x},${point.y}`).join(' ')} />;
    case 'ellipse': return <ellipse {...common} cx={stroke.center.x} cy={stroke.center.y} rx={stroke.rx} ry={stroke.ry} />;
    case 'polygon': return <polygon {...common} points={stroke.points.map((point) => `${point.x},${point.y}`).join(' ')} />;
    case 'bezier': {
      const d = `M ${stroke.start.x} ${stroke.start.y} ${stroke.segments.map((segment) => `C ${segment.control1.x} ${segment.control1.y} ${segment.control2.x} ${segment.control2.y} ${segment.end.x} ${segment.end.y}`).join(' ')}${stroke.closed ? ' Z' : ''}`;
      return <path {...common} d={d} />;
    }
  }
}

export function Sketch({ lesson, step, revealed, highlight = true, printable = false, label, className = '' }: {
  lesson: Lesson; step?: number; revealed?: number; highlight?: boolean; printable?: boolean; label?: string; className?: string;
}) {
  const titleId = useId();
  const visibleStep = step ?? lesson.groups.length - 1;
  return <svg className={`sketch ${className}`} viewBox="0 0 1000 1000" role="img" aria-labelledby={titleId} xmlns="http://www.w3.org/2000/svg">
    <title id={titleId}>{label ?? `${lesson.title}${step === undefined ? ', finished drawing' : `, step ${step + 1}`}`}</title>
    {lesson.groups.slice(0, visibleStep + 1).map((group, groupIndex) => <g key={group.id} data-group-id={group.id}>
      {group.strokes.slice(0, groupIndex === visibleStep && revealed !== undefined ? revealed : undefined).map((stroke, strokeIndex) => <Primitive
        key={stroke.id} stroke={stroke}
        muted={step !== undefined && highlight && groupIndex < visibleStep}
        highlighted={step !== undefined && highlight && groupIndex === visibleStep && (revealed === undefined || strokeIndex === revealed - 1)}
        printable={printable}
      />)}
    </g>)}
  </svg>;
}
