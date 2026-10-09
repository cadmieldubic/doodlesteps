import { z } from 'zod';

const coordinate = z.number().finite().min(0).max(1000);
export const pointSchema = z.object({ x: coordinate, y: coordinate }).strict();
export const colorSchema = z.enum(['graphite', 'lavender', 'peach', 'mint']);
const fillSchema = z.union([z.literal('none'), colorSchema]);
const identifier = z.string().min(1).max(64).regex(/^[A-Za-z0-9][A-Za-z0-9_-]*$/);
const base = { id: identifier, color: colorSchema, width: z.number().finite().min(2).max(12), opacity: z.number().finite().min(0.2).max(1) };
const line = z.object({ ...base, kind: z.literal('line'), start: pointSchema, end: pointSchema }).strict();
const polyline = z.object({ ...base, kind: z.literal('polyline'), points: z.array(pointSchema).min(2).max(16) }).strict();
const ellipse = z.object({ ...base, kind: z.literal('ellipse'), center: pointSchema, rx: z.number().finite().positive().max(500), ry: z.number().finite().positive().max(500), fill: fillSchema }).strict();
const polygon = z.object({ ...base, kind: z.literal('polygon'), points: z.array(pointSchema).min(3).max(16), fill: fillSchema }).strict();
const bezier = z.object({
  ...base, kind: z.literal('bezier'), start: pointSchema,
  segments: z.array(z.object({ control1: pointSchema, control2: pointSchema, end: pointSchema }).strict()).min(1).max(6),
  closed: z.boolean(), fill: fillSchema,
}).strict();
export const strokeSchema = z.discriminatedUnion('kind', [line, polyline, ellipse, polygon, bezier]).superRefine((stroke, context) => {
  if (stroke.kind === 'ellipse' && (stroke.center.x - stroke.rx < 0 || stroke.center.x + stroke.rx > 1000 || stroke.center.y - stroke.ry < 0 || stroke.center.y + stroke.ry > 1000)) {
    context.addIssue({ code: z.ZodIssueCode.custom, message: 'Ellipse must fit inside the drawing canvas.' });
  }
  if (stroke.kind === 'bezier' && !stroke.closed && stroke.fill !== 'none') {
    context.addIssue({ code: z.ZodIssueCode.custom, message: 'An open curve cannot have a fill.' });
  }
});
export const analysisSchema = z.object({
  subject: z.string().min(1).max(120),
  recognizable_features: z.array(z.string().min(1).max(180)).min(1).max(10),
  simplifications: z.array(z.string().min(1).max(180)).min(1).max(10),
  proportions: z.string().min(1).max(400), composition: z.string().min(1).max(400),
  difficulty: z.enum(['easy', 'medium']), suitable: z.boolean(), reason: z.string().max(240),
}).strict();
export const groupSchema = z.object({ id: identifier, title: z.string().min(1).max(80), instruction: z.string().min(1).max(240), strokes: z.array(strokeSchema).min(1).max(16) }).strict();
export const lessonSchema = z.object({
  schema_version: z.literal('1'), id: identifier, source: z.enum(['demo', 'ai']), title: z.string().min(1).max(80), subject: z.string().min(1).max(120),
  description: z.string().min(1).max(500), analysis: analysisSchema, groups: z.array(groupSchema).min(4).max(6),
}).strict().superRefine((lesson, context) => {
  const groupIds = lesson.groups.map((group) => group.id);
  const strokeIds = lesson.groups.flatMap((group) => group.strokes.map((stroke) => stroke.id));
  if (new Set(groupIds).size !== groupIds.length) context.addIssue({ code: z.ZodIssueCode.custom, message: 'Drawing groups must have unique IDs.' });
  if (new Set(strokeIds).size !== strokeIds.length) context.addIssue({ code: z.ZodIssueCode.custom, message: 'Drawing strokes must have unique IDs.' });
  if (strokeIds.length > 64) context.addIssue({ code: z.ZodIssueCode.custom, message: 'This drawing has too many strokes.' });
  if (!lesson.analysis.suitable) context.addIssue({ code: z.ZodIssueCode.custom, message: 'This subject needs a simpler photo.' });
});
export const configSchema = z.object({
  ai_available: z.boolean(), max_upload_bytes: z.number().int().positive().max(30 * 1024 * 1024),
  supported_formats: z.array(z.enum(['image/jpeg', 'image/png', 'image/webp'])).min(1).max(3),
}).strict();
export type Point = z.infer<typeof pointSchema>;
export type Stroke = z.infer<typeof strokeSchema>;
export type Lesson = z.infer<typeof lessonSchema>;
export type AppConfig = z.infer<typeof configSchema>;
