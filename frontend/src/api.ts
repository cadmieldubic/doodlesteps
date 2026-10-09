import { z } from 'zod';
import { configSchema, lessonSchema } from './schema';
import type { Lesson } from './schema';

export class ApiError extends Error {
  constructor(message: string, public status?: number) { super(message); this.name = 'ApiError'; }
}

export async function request<T>(path: string, schema: z.ZodType<T>, options: RequestInit = {}, timeoutMs = 120_000): Promise<T> {
  const controller = new AbortController();
  let timedOut = false;
  const abort = () => controller.abort();
  options.signal?.addEventListener('abort', abort, { once: true });
  if (options.signal?.aborted) controller.abort();
  const timeout = window.setTimeout(() => { timedOut = true; controller.abort(); }, timeoutMs);
  try {
    const response = await fetch(path, { ...options, signal: controller.signal });
    let data: unknown;
    try { data = await response.json(); } catch { throw new ApiError('The drawing service sent an unreadable response. Please try again.'); }
    if (!response.ok) {
      const detail = z.object({ detail: z.string().max(1000) }).safeParse(data);
      throw new ApiError(detail.success ? detail.data.detail : 'The drawing service could not finish. Please try again.', response.status);
    }
    const result = schema.safeParse(data);
    if (!result.success) throw new ApiError('This drawing could not be safely displayed. Please try another photo or a demo lesson.');
    return result.data;
  } catch (error) {
    if (error instanceof ApiError) throw error;
    if (controller.signal.aborted) throw new ApiError(timedOut ? 'The lesson took too long. Please try a simpler photo.' : 'Drawing request cancelled.');
    throw new ApiError('We cannot reach the drawing service. Ask an adult to start the backend, then try again.');
  } finally {
    window.clearTimeout(timeout);
    options.signal?.removeEventListener('abort', abort);
  }
}
export const fetchConfig = (signal?: AbortSignal) => request('/api/config', configSchema, { signal }, 10_000);
export const fetchDemos = (signal?: AbortSignal) => request('/api/demos', z.array(lessonSchema.refine((lesson) => lesson.source === 'demo')).min(1).max(10), { signal }, 10_000);
export const generateLesson = (file: File, signal: AbortSignal): Promise<Lesson> => {
  const form = new FormData();
  form.append('image', file);
  return request('/api/lessons', lessonSchema.refine((lesson) => lesson.source === 'ai'), { method: 'POST', body: form, signal });
};
