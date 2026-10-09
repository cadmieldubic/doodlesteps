import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { Sketch } from './Sketch';
import { fixtureLesson } from '../test/fixtures';
import type { Lesson } from '../schema';

describe('immutable cumulative renderer', () => {
  it('retains exactly the same geometry while adding and muting strokes', () => {
    const original = structuredClone(fixtureLesson);
    const { container, rerender } = render(<Sketch lesson={fixtureLesson} step={0} revealed={1} />);
    const first = container.querySelector('[data-stroke-id="line-0-a"]')!;
    const geometry = ['x1', 'y1', 'x2', 'y2', 'stroke-width'].map((attribute) => first.getAttribute(attribute));
    expect(container.querySelectorAll('[data-stroke-id]')).toHaveLength(1);
    rerender(<Sketch lesson={fixtureLesson} step={2} revealed={1} />);
    expect(container.querySelectorAll('[data-stroke-id]')).toHaveLength(5);
    const retained = container.querySelector('[data-stroke-id="line-0-a"]')!;
    expect(['x1', 'y1', 'x2', 'y2', 'stroke-width'].map((attribute) => retained.getAttribute(attribute))).toEqual(geometry);
    expect(retained).toHaveAttribute('data-stroke-state', 'previous');
    expect(container.querySelector('[data-stroke-id="line-2-a"]')).toHaveAttribute('data-stroke-state', 'current');
    expect(fixtureLesson).toEqual(original);
  });
  it('reveals an individual line and displays the complete final blueprint', () => {
    const { container, rerender } = render(<Sketch lesson={fixtureLesson} step={0} revealed={2} />);
    expect(container.querySelectorAll('[data-stroke-id]')).toHaveLength(2);
    expect(container.querySelector('[data-stroke-id="line-0-b"]')).toHaveAttribute('data-stroke-state', 'current');
    rerender(<Sketch lesson={fixtureLesson} />);
    expect(container.querySelectorAll('[data-stroke-id]')).toHaveLength(8);
    expect(screen.getByRole('img')).toHaveAccessibleName('Friendly puppy, finished drawing');
  });
  it('constructs a restricted Bézier path only from numeric coordinates', () => {
    const lesson: Lesson = structuredClone(fixtureLesson);
    lesson.groups[0].strokes = [{ id: 'curve', kind: 'bezier', color: 'graphite', width: 6, opacity: 1, start: { x: 10, y: 20 }, segments: [{ control1: { x: 30, y: 40 }, control2: { x: 50, y: 60 }, end: { x: 70, y: 80 } }], closed: true, fill: 'none' }];
    const { container } = render(<Sketch lesson={lesson} step={0} />);
    expect(container.querySelector('path')).toHaveAttribute('d', 'M 10 20 C 30 40 50 60 70 80 Z');
  });
});
