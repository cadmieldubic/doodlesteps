import { afterEach, describe, expect, it, vi } from 'vitest';
import { fetchConfig, generateLesson, request } from './api';
import { configSchema } from './schema';
import { fixtureConfig, fixtureLesson } from './test/fixtures';

afterEach(() => { vi.unstubAllGlobals(); vi.useRealTimers(); });
describe('API boundary', () => {
  it('accepts validated configuration and never exposes credentials', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => fixtureConfig }));
    expect(await fetchConfig()).toEqual(fixtureConfig);
  });
  it('surfaces actionable backend errors', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 422, json: async () => ({ detail: 'Try a photo of one simpler subject.' }) }));
    await expect(fetchConfig()).rejects.toThrow('Try a photo of one simpler subject.');
  });
  it('rejects broken or unsafe model responses', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => ({ ...fixtureConfig, api_key: 'not-allowed' }) }));
    await expect(fetchConfig()).rejects.toThrow('could not be safely displayed');
  });
  it('never accepts a demo as the result of an uploaded photo', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => fixtureLesson }));
    await expect(generateLesson(new File(['photo'], 'photo.png', { type: 'image/png' }), new AbortController().signal)).rejects.toThrow('could not be safely displayed');
  });
  it('aborts a slow request and explains the timeout', async () => {
    vi.useFakeTimers();
    vi.stubGlobal('fetch', vi.fn((_url, options: RequestInit) => new Promise((_resolve, reject) => options.signal?.addEventListener('abort', () => reject(new DOMException('Abort', 'AbortError'))))));
    const pending = request('/api/config', configSchema, {}, 100);
    const expectation = expect(pending).rejects.toThrow('took too long');
    await vi.advanceTimersByTimeAsync(101);
    await expectation;
  });
});
