import type { AppConfig, Lesson, Stroke } from '../schema';

export const fixtureConfig: AppConfig = { ai_available: false, max_upload_bytes: 8 * 1024 * 1024, supported_formats: ['image/jpeg', 'image/png', 'image/webp'] };
const stroke = (id: string, y: number): Stroke => ({ id, kind: 'line', color: 'graphite', width: 6, opacity: 1, start: { x: 300, y }, end: { x: 700, y } });
export const fixtureLesson: Lesson = {
  schema_version: '1', id: 'puppy', source: 'demo', title: 'Friendly puppy', subject: 'Puppy', description: 'A happy little puppy with soft, floppy ears.',
  analysis: { subject: 'Puppy', recognizable_features: ['Floppy ears'], simplifications: ['Soft simple shapes'], proportions: 'Round head and small body', composition: 'Centered on the page', difficulty: 'easy', suitable: true, reason: '' },
  groups: Array.from({ length: 4 }, (_, index) => ({ id: `group-${index}`, title: ['Make the head', 'Add floppy ears', 'Draw a happy face', 'Add little paws'][index], instruction: `Draw two soft lines for step ${index + 1}. You’re doing great!`, strokes: [stroke(`line-${index}-a`, 200 + index * 100), stroke(`line-${index}-b`, 230 + index * 100)] })),
};
export const fixtureDemos = [fixtureLesson, { ...fixtureLesson, id: 'flower', title: 'Happy flower', subject: 'Flower' }, { ...fixtureLesson, id: 'house', title: 'Little house', subject: 'House' }];
