import { act, cleanup, render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import App from './App';
import { fixtureConfig, fixtureDemos, fixtureLesson } from './test/fixtures';

function mockService(live = false) {
  vi.stubGlobal('fetch', vi.fn(async (url: string) => ({ ok: true, json: async () => url === '/api/config' ? { ...fixtureConfig, ai_available: live } : url === '/api/lessons' ? { ...fixtureLesson, source: 'ai' } : fixtureDemos })));
}
async function openDemo() {
  await userEvent.click(await screen.findByRole('button', { name: 'Try Friendly puppy demo lesson' }));
  await userEvent.click(screen.getByRole('button', { name: /let’s start drawing/i }));
}
beforeEach(() => {
  mockService();
  vi.spyOn(window, 'scrollTo').mockImplementation(() => undefined);
  vi.spyOn(window, 'print').mockImplementation(() => undefined);
  vi.stubGlobal('URL', class extends URL { static createObjectURL = vi.fn(() => 'blob:test-photo'); static revokeObjectURL = vi.fn(); });
  vi.stubGlobal('Image', class { naturalWidth = 100; naturalHeight = 100; onload: (() => void) | null = null; onerror: (() => void) | null = null; set src(_value: string) { queueMicrotask(() => this.onload?.()); } });
});
afterEach(() => { cleanup(); vi.restoreAllMocks(); vi.unstubAllGlobals(); });

describe('drawing tutor journey', () => {
  it('offers three labeled demos and device camera input', async () => {
    render(<App />);
    expect(screen.getByRole('heading', { name: /Every picture can become a drawing!/ })).toBeInTheDocument();
    expect(await screen.findByRole('button', { name: 'Try Friendly puppy demo lesson' })).toBeInTheDocument();
    expect(screen.getAllByText('Demo lesson')).toHaveLength(3);
    expect(screen.getByLabelText('Take a photograph')).toHaveAttribute('capture', 'environment');
  });
  it('builds cumulative steps, reveals lines, completes and restarts a demo', async () => {
    const { container } = render(<App />);
    await openDemo();
    const stage = () => container.querySelector('.drawing-stage')!;
    expect(stage().querySelectorAll('[data-stroke-id]')).toHaveLength(1);
    await userEvent.click(screen.getByRole('button', { name: 'Show next line' }));
    expect(stage().querySelectorAll('[data-stroke-id]')).toHaveLength(2);
    await userEvent.click(screen.getByRole('button', { name: 'Next step' }));
    expect(stage().querySelectorAll('[data-stroke-id]')).toHaveLength(3);
    await userEvent.click(screen.getByRole('button', { name: 'Previous' }));
    expect(stage().querySelectorAll('[data-stroke-id]')).toHaveLength(2);
    for (let index = 0; index < 3; index++) await userEvent.click(screen.getByRole('button', { name: 'Next step' }));
    await userEvent.click(screen.getByRole('button', { name: 'Finish drawing' }));
    expect(screen.getByRole('heading', { name: /You made something wonderful/ })).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: 'Draw it again' }));
    expect(screen.getByRole('button', { name: /Let’s start drawing/ })).toBeInTheDocument();
  });
  it('includes the final drawing and every cumulative step in the print worksheet', async () => {
    render(<App />);
    await openDemo();
    await userEvent.click(screen.getByRole('button', { name: 'Print guide' }));
    expect(window.print).toHaveBeenCalledOnce();
    const worksheet = screen.getByLabelText('Printable drawing worksheet');
    expect(worksheet.querySelectorAll('svg')).toHaveLength(5);
    expect(worksheet.querySelectorAll('.worksheet-step')).toHaveLength(4);
    expect(within(worksheet).getByText('1. Make the head')).toBeInTheDocument();
  });
  it('previews, replaces and removes an upload while explaining missing live AI setup', async () => {
    render(<App />);
    await screen.findByRole('button', { name: 'Try Friendly puppy demo lesson' });
    const input = screen.getByLabelText('Upload a photograph');
    await userEvent.upload(input, new File(['photo'], 'flower.png', { type: 'image/png' }));
    expect(await screen.findByAltText('Your selected photograph')).toHaveAttribute('src', 'blob:test-photo');
    expect(screen.getByRole('button', { name: 'Create my drawing lesson' })).toBeDisabled();
    expect(screen.getByText(/OPENAI_API_KEY/)).toBeInTheDocument();
    await userEvent.upload(input, new File(['replacement'], 'puppy.jpg', { type: 'image/jpeg' }));
    expect(await screen.findByText('puppy.jpg')).toBeInTheDocument();
    expect(URL.revokeObjectURL).toHaveBeenCalled();
    await userEvent.click(screen.getByRole('button', { name: 'Remove' }));
    expect(screen.getByRole('heading', { name: /Every picture can become a drawing!/ })).toBeInTheDocument();
  });
  it('rejects unsupported, oversized, and corrupt image uploads', async () => {
    render(<App />);
    await screen.findByRole('button', { name: 'Try Friendly puppy demo lesson' });
    const user = userEvent.setup({ applyAccept: false });
    const input = screen.getByLabelText('Upload a photograph');
    await user.upload(input, new File(['text'], 'notes.txt', { type: 'text/plain' }));
    expect(screen.getByRole('alert')).toHaveTextContent('JPEG, PNG, or WebP');
    const large = new File(['photo'], 'huge.png', { type: 'image/png' });
    Object.defineProperty(large, 'size', { value: 9 * 1024 * 1024 });
    await user.upload(input, large);
    expect(screen.getByRole('alert')).toHaveTextContent('smaller than 8 MB');
    vi.stubGlobal('Image', class { onerror: (() => void) | null = null; set src(_value: string) { queueMicrotask(() => this.onerror?.()); } });
    await user.upload(input, new File(['not a photo'], 'corrupt.png', { type: 'image/png' }));
    await waitFor(() => expect(screen.getByRole('alert')).toHaveTextContent('readable photo'));
  });
  it('uses live lesson responses with an original photo reference', async () => {
    mockService(true);
    render(<App />);
    await screen.findByRole('button', { name: 'Try Friendly puppy demo lesson' });
    await userEvent.upload(screen.getByLabelText('Upload a photograph'), new File(['photo'], 'photo.png', { type: 'image/png' }));
    await userEvent.click(await screen.findByRole('button', { name: 'Create my drawing lesson' }));
    expect(await screen.findByText('Photo-inspired AI lesson')).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: /See original photo/ }));
    expect(screen.getByAltText('Original photograph for your drawing reference')).toBeInTheDocument();
    const post = vi.mocked(fetch).mock.calls.find((call) => call[0] === '/api/lessons');
    expect(post?.[1]?.method).toBe('POST');
    expect(post?.[1]?.body).toBeInstanceOf(FormData);
  });
  it('discards a stale photo decode after a second invalid selection', async () => {
    let loaded = () => undefined;
    vi.stubGlobal('Image', class { naturalWidth = 100; naturalHeight = 100; onload: (() => void) | null = null; set src(_value: string) { loaded = () => { this.onload?.(); }; } });
    render(<App />);
    await screen.findByRole('button', { name: 'Try Friendly puppy demo lesson' });
    const user = userEvent.setup({ applyAccept: false });
    const input = screen.getByLabelText('Upload a photograph');
    await user.upload(input, new File(['photo'], 'first.png', { type: 'image/png' }));
    expect(screen.getByRole('status')).toHaveTextContent('Checking your photo');
    await user.upload(input, new File(['text'], 'second.txt', { type: 'text/plain' }));
    expect(screen.queryByRole('status')).not.toBeInTheDocument();
    await act(async () => loaded());
    expect(screen.queryByAltText('Your selected photograph')).not.toBeInTheDocument();
    expect(URL.revokeObjectURL).toHaveBeenCalledWith('blob:test-photo');
  });
  it('keeps the photo available when AI fails and never falls back to an unrelated demo', async () => {
    mockService(true);
    render(<App />);
    await screen.findByRole('button', { name: 'Try Friendly puppy demo lesson' });
    await userEvent.upload(screen.getByLabelText('Upload a photograph'), new File(['photo'], 'photo.png', { type: 'image/png' }));
    vi.mocked(fetch).mockResolvedValueOnce(new Response(JSON.stringify({ detail: 'The AI service is unavailable. Please try again later.' }), { status: 503 }));
    await userEvent.click(await screen.findByRole('button', { name: 'Create my drawing lesson' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('AI service is unavailable');
    expect(screen.getByAltText('Your selected photograph')).toBeInTheDocument();
    expect(screen.queryByRole('tab', { name: 'Finished sketch' })).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Create my drawing lesson' })).toBeEnabled();
  });
  it('disables generation until a replacement photo has finished decoding', async () => {
    mockService(true);
    render(<App />);
    await screen.findByRole('button', { name: 'Try Friendly puppy demo lesson' });
    const input = screen.getByLabelText('Upload a photograph');
    await userEvent.upload(input, new File(['first'], 'first.png', { type: 'image/png' }));
    expect(await screen.findByRole('button', { name: 'Create my drawing lesson' })).toBeEnabled();
    let loaded = () => undefined;
    vi.stubGlobal('Image', class { naturalWidth = 100; naturalHeight = 100; onload: (() => void) | null = null; set src(_value: string) { loaded = () => { this.onload?.(); }; } });
    await userEvent.upload(input, new File(['second'], 'second.png', { type: 'image/png' }));
    expect(screen.getByRole('button', { name: 'Create my drawing lesson' })).toBeDisabled();
    await userEvent.click(screen.getByRole('button', { name: 'Create my drawing lesson' }));
    expect(vi.mocked(fetch).mock.calls.some((call) => call[0] === '/api/lessons')).toBe(false);
    await act(async () => loaded());
    expect(screen.getByText('second.png')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Create my drawing lesson' })).toBeEnabled();
  });
  it('aborts generation for photo A when photo B is selected and never pairs A’s drawing with B', async () => {
    mockService(true);
    render(<App />);
    await screen.findByRole('button', { name: 'Try Friendly puppy demo lesson' });
    const input = screen.getByLabelText('Upload a photograph');
    await userEvent.upload(input, new File(['first'], 'first.png', { type: 'image/png' }));
    let finish: ((value: Response) => void) | undefined;
    let signal: AbortSignal | null | undefined;
    vi.mocked(fetch).mockImplementationOnce((_url, options) => { signal = options?.signal; return new Promise((resolve) => { finish = resolve; }); });
    await userEvent.click(await screen.findByRole('button', { name: 'Create my drawing lesson' }));
    expect(screen.getByRole('button', { name: 'Cancel request' })).toBeInTheDocument();
    await userEvent.upload(input, new File(['second'], 'second.png', { type: 'image/png' }));
    expect(signal?.aborted).toBe(true);
    expect(await screen.findByText('second.png')).toBeInTheDocument();
    await act(async () => finish?.(new Response(JSON.stringify({ ...fixtureLesson, source: 'ai' }), { status: 200 })));
    expect(screen.queryByText('Photo-inspired AI lesson')).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Create my drawing lesson' })).toBeEnabled();
    expect(screen.getByText('second.png')).toBeInTheDocument();
  });
  it('handles unavailable services with an actionable message and retry', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('offline')));
    render(<App />);
    expect(await screen.findByRole('alert')).toHaveTextContent('start the backend');
    mockService();
    await userEvent.click(screen.getByRole('button', { name: 'Try again' }));
    expect(await screen.findByRole('button', { name: 'Try Friendly puppy demo lesson' })).toBeInTheDocument();
  });
  it('lets an adult cancel a live generation without displaying a stale result', async () => {
    mockService(true);
    render(<App />);
    await screen.findByRole('button', { name: 'Try Friendly puppy demo lesson' });
    await userEvent.upload(screen.getByLabelText('Upload a photograph'), new File(['photo'], 'photo.png', { type: 'image/png' }));
    const fetchMock = vi.mocked(fetch);
    let finish: ((value: Response) => void) | undefined;
    fetchMock.mockImplementationOnce(() => new Promise((resolve) => { finish = resolve; }));
    await userEvent.click(await screen.findByRole('button', { name: 'Create my drawing lesson' }));
    await userEvent.click(screen.getByRole('button', { name: 'Cancel request' }));
    await act(async () => finish?.(new Response(JSON.stringify({ ...fixtureLesson, source: 'ai' }), { status: 200 })));
    expect(screen.queryByText('Photo-inspired AI lesson')).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Create my drawing lesson' })).toBeEnabled();
  });
});
