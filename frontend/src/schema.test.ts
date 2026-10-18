import { describe, expect, it } from 'vitest';
import { configSchema, lessonSchema, strokeSchema } from './schema';
import { fixtureConfig, fixtureLesson } from './test/fixtures';

describe('drawing contract', () => {
  it('accepts a coherent lesson with all required fields', () => { expect(lessonSchema.parse(fixtureLesson)).toEqual(fixtureLesson); expect(configSchema.parse(fixtureConfig)).toEqual(fixtureConfig); });
  it('rejects untrusted SVG data, URLs, and missing stroke fields', () => {
    expect(strokeSchema.safeParse({ ...fixtureLesson.groups[0].strokes[0], svg: '<script/>' }).success).toBe(false);
    expect(strokeSchema.safeParse({ ...fixtureLesson.groups[0].strokes[0], color: 'url(https://example.com)' }).success).toBe(false);
    expect(strokeSchema.safeParse({ id: 'bad', kind: 'line', start: { x: 1, y: 1 }, end: { x: 10, y: 10 } }).success).toBe(false);
  });
  it('rejects non-finite coordinates and out-of-canvas ellipses', () => {
    expect(strokeSchema.safeParse({ ...fixtureLesson.groups[0].strokes[0], start: { x: Infinity, y: 2 } }).success).toBe(false);
    expect(strokeSchema.safeParse({ id: 'oval', kind: 'ellipse', color: 'graphite', width: 5, opacity: 1, center: { x: 50, y: 50 }, rx: 80, ry: 40, fill: 'none' }).success).toBe(false);
  });
  it('requires closed curves for filled shapes', () => {
    expect(strokeSchema.safeParse({ id: 'curve', kind: 'bezier', color: 'mint', width: 5, opacity: 1, start: { x: 50, y: 50 }, segments: [{ control1: { x: 80, y: 50 }, control2: { x: 80, y: 80 }, end: { x: 50, y: 80 } }], closed: false, fill: 'mint' }).success).toBe(false);
  });
  it('rejects reused IDs, excessive scene complexity, and unsuitable photos', () => {
    const duplicates = structuredClone(fixtureLesson);
    duplicates.groups[1].strokes[0].id = duplicates.groups[0].strokes[0].id;
    expect(lessonSchema.safeParse(duplicates).success).toBe(false);
    duplicates.groups[1].strokes[0].id = 'unique';
    duplicates.groups[1].id = duplicates.groups[0].id;
    expect(lessonSchema.safeParse(duplicates).success).toBe(false);
    const complex = structuredClone(fixtureLesson);
    complex.groups = Array.from({ length: 5 }, (_, group) => ({ ...complex.groups[0], id: `g-${group}`, strokes: Array.from({ length: 13 }, (_, index) => ({ ...complex.groups[0].strokes[0], id: `s-${group}-${index}` })) }));
    expect(lessonSchema.safeParse(complex).success).toBe(false);
    expect(lessonSchema.safeParse({ ...fixtureLesson, analysis: { ...fixtureLesson.analysis, suitable: false } }).success).toBe(false);
  });
  it('keeps frontend string bounds aligned with the backend', () => {
    expect(lessonSchema.safeParse({ ...fixtureLesson, title: 'x'.repeat(81) }).success).toBe(false);
    expect(lessonSchema.safeParse({ ...fixtureLesson, analysis: { ...fixtureLesson.analysis, recognizable_features: ['x'.repeat(181)] } }).success).toBe(false);
  });
});
