import { expect, test, type Locator, type Page } from '@playwright/test';
import type { Lesson } from '../src/schema';

// A tiny valid PNG tests decoding and local preview without using personal photos.
const samplePng = Buffer.from(
  'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAAAI0lEQVR4nGM8dv8cAymAiSTVDKMaiANMRKqDg1ENxACSQwkAr7sCkxsenaAAAAAASUVORK5CYII=',
  'base64',
);
const photo = (name: string) => ({ name, mimeType: 'image/png', buffer: samplePng });

type Geometry = Record<string, Record<string, string>>;

async function geometry(stage: Locator): Promise<Geometry> {
  return stage.locator('[data-stroke-id]').evaluateAll((strokes) => {
    const attributes = ['d', 'x1', 'y1', 'x2', 'y2', 'points', 'cx', 'cy', 'rx', 'ry'];
    return Object.fromEntries(strokes.map((stroke) => [
      stroke.getAttribute('data-stroke-id')!,
      Object.fromEntries(attributes.filter((attribute) => stroke.hasAttribute(attribute))
        .map((attribute) => [attribute, stroke.getAttribute(attribute)!])),
    ]));
  });
}

async function demo(page: Page, id: string): Promise<Lesson> {
  const response = await page.request.get('/api/demos');
  expect(response.ok()).toBeTruthy();
  const lessons = await response.json() as Lesson[];
  const lesson = lessons.find((item) => item.id === id);
  expect(lesson, `Real backend should provide ${id}`).toBeDefined();
  expect(lesson!.source).toBe('demo');
  await page.getByRole('button', { name: `Try ${lesson!.title} demo lesson`, exact: true }).click();
  await expect(page.getByRole('heading', { level: 1, name: lesson!.title, exact: true })).toBeVisible();
  return lesson!;
}

async function assertNoOverflow(page: Page) {
  const sizes = await page.evaluate(() => ({
    document: document.documentElement.scrollWidth,
    viewport: document.documentElement.clientWidth,
  }));
  expect(sizes.document).toBeLessThanOrEqual(sizes.viewport + 1);
}

test.beforeEach(async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('button', { name: / demo lesson$/ })).toHaveCount(3);
});

for (const id of ['puppy', 'flower', 'house']) {
  test(`${id}: the guide cumulatively reproduces its finished sketch and can restart`, async ({ page }, testInfo) => {
    const lesson = await demo(page, id);
    const stage = page.locator('.drawing-stage > svg');
    const finalGeometry = await geometry(stage);
    const totalStrokes = lesson.groups.reduce((count, group) => count + group.strokes.length, 0);
    await expect(stage.locator('[data-stroke-id]')).toHaveCount(totalStrokes);
    await expect(page.getByRole('tab', { name: 'Finished sketch' })).toHaveAttribute('aria-selected', 'true');
    await page.screenshot({ path: testInfo.outputPath(`${id}-finished.png`), fullPage: true });
    await page.getByRole('button', { name: 'Let’s start drawing' }).click();
    await expect(page.getByRole('button', { name: 'Previous', exact: true })).toBeDisabled();
    await expect(stage.locator('[data-stroke-id]')).toHaveCount(1);

    let previousCount = 0;
    for (let index = 0; index < lesson.groups.length; index += 1) {
      const group = lesson.groups[index];
      await expect(page.locator('.drawing-corner')).toContainText(`Step ${index + 1} of ${lesson.groups.length}`);
      await expect(page.locator('.step-instruction')).toHaveText(group.instruction);
      await expect(stage.locator('[data-stroke-id]')).toHaveCount(previousCount + 1);
      if (group.strokes.length > 1) {
        const before = await geometry(stage);
        await page.getByRole('button', { name: 'Show next line', exact: true }).click();
        await expect(stage.locator('[data-stroke-id]')).toHaveCount(previousCount + 2);
        const after = await geometry(stage);
        for (const [strokeId, strokeGeometry] of Object.entries(before)) {
          expect(after[strokeId]).toEqual(strokeGeometry);
        }
        await expect(stage.locator('[data-stroke-state="current"]')).toHaveCount(1);
        await expect(stage.locator('[data-stroke-state="current"]')).toHaveAttribute('data-stroke-id', group.strokes[1].id);
      }
      const showAll = page.getByRole('button', { name: 'Show all lines in this step', exact: true });
      if (await showAll.count()) await showAll.click();
      await expect(page.getByRole('button', { name: 'Show next line', exact: true })).toBeDisabled();
      const currentIds = lesson.groups.slice(0, index + 1).flatMap((item) => item.strokes.map((stroke) => stroke.id));
      const expected = Object.fromEntries(currentIds.map((strokeId) => [strokeId, finalGeometry[strokeId]]));
      expect(await geometry(stage)).toEqual(expected);
      await expect(stage.locator('[data-group-id]')).toHaveCount(index + 1);
      await expect(stage.locator('[data-stroke-state="previous"]')).toHaveCount(previousCount);
      previousCount += group.strokes.length;

      if (index === 1) {
        await page.getByRole('button', { name: 'Previous', exact: true }).click();
        await expect(page.locator('.drawing-corner')).toContainText('Step 1 of');
        await expect(stage.locator('[data-stroke-id]')).toHaveCount(lesson.groups[0].strokes.length);
        await page.getByRole('button', { name: 'Next step', exact: true }).click();
        await page.getByRole('button', { name: 'Show all lines in this step', exact: true }).click();
        expect(await geometry(stage)).toEqual(expected);
      }
      if (index < lesson.groups.length - 1) {
        await page.getByRole('button', { name: 'Next step', exact: true }).click();
      }
    }

    await page.getByRole('tab', { name: 'Finished sketch' }).click();
    expect(await geometry(stage)).toEqual(finalGeometry);
    await page.getByRole('tab', { name: 'Step-by-step guide' }).click();
    await expect(page.locator('.drawing-corner')).toContainText('Step 6 of 6');
    await page.getByRole('button', { name: 'Finish drawing', exact: true }).click();
    await expect(page.getByRole('heading', { level: 1, name: /You made something/ })).toBeVisible();
    expect(await geometry(page.locator('.completed-sketch > svg'))).toEqual(finalGeometry);
    await page.getByRole('button', { name: 'Draw it again', exact: true }).click();
    await expect(page.getByRole('tab', { name: 'Finished sketch' })).toHaveAttribute('aria-selected', 'true');
    await page.getByRole('button', { name: 'Let’s start drawing' }).click();
    await expect(page.locator('.drawing-corner')).toContainText('Step 1 of 6');
    await expect(stage.locator('[data-stroke-id]')).toHaveCount(1);
  });
}

test('step thumbnails navigate directly and preserve the shared blueprint', async ({ page }) => {
  const lesson = await demo(page, 'puppy');
  const stage = page.locator('.drawing-stage > svg');
  const finished = await geometry(stage);
  await page.getByRole('button', { name: `Go to step 4: ${lesson.groups[3].title}`, exact: true }).click();
  await expect(page.locator('.drawing-corner')).toContainText('Step 4 of 6');
  const ids = lesson.groups.slice(0, 3).flatMap((group) => group.strokes.map((stroke) => stroke.id));
  ids.push(lesson.groups[3].strokes[0].id);
  expect(await geometry(stage)).toEqual(Object.fromEntries(ids.map((id) => [id, finished[id]])));
});

test('valid photos preview locally, replace, remove, and cannot generate without a key', async ({ page }) => {
  const config = await (await page.request.get('/api/config')).json();
  expect(config.ai_available, 'E2E runs use a credential-free backend').toBe(false);
  const generationRequests: string[] = [];
  page.on('request', (request) => {
    if (request.method() === 'POST' && request.url().includes('/api/lessons')) generationRequests.push(request.url());
  });
  await page.getByLabel('Upload a photograph', { exact: true }).setInputFiles(photo('first-photo.png'));
  await expect(page.getByRole('img', { name: 'Your selected photograph', exact: true })).toBeVisible();
  await expect(page.getByText('first-photo.png', { exact: true })).toBeVisible();
  await expect(page.getByText(/Use non-personal photos for this private prototype/)).toBeVisible();
  await expect(page.getByText(/adult developer must add OPENAI_API_KEY/)).toBeVisible();
  await expect(page.getByRole('button', { name: 'Create my drawing lesson', exact: true })).toBeDisabled();
  const firstUrl = await page.getByRole('img', { name: 'Your selected photograph', exact: true }).getAttribute('src');
  const chooser = page.waitForEvent('filechooser');
  await page.getByRole('button', { name: 'Replace photo', exact: true }).click();
  await (await chooser).setFiles(photo('replacement-photo.png'));
  await expect(page.getByText('replacement-photo.png', { exact: true })).toBeVisible();
  expect(await page.getByRole('img', { name: 'Your selected photograph', exact: true }).getAttribute('src')).not.toBe(firstUrl);
  await page.getByRole('button', { name: 'Remove', exact: true }).click();
  await expect(page.getByRole('button', { name: 'Pick a photo', exact: true })).toBeVisible();
  await expect(page.getByRole('img', { name: 'Your selected photograph', exact: true })).toHaveCount(0);
  expect(generationRequests).toEqual([]);
});

test('unsupported types, corrupt images, empty files, and oversized files show clear errors', async ({ page }) => {
  const upload = page.getByLabel('Upload a photograph', { exact: true });
  await upload.setInputFiles({ name: 'unsafe.svg', mimeType: 'image/svg+xml', buffer: Buffer.from('<svg/>') });
  await expect(page.getByRole('alert')).toContainText('JPEG, PNG, or WebP');
  await upload.setInputFiles({ name: 'corrupt.png', mimeType: 'image/png', buffer: Buffer.from('not an image') });
  await expect(page.getByRole('alert')).toContainText('readable photo');
  await upload.setInputFiles({ name: 'empty.png', mimeType: 'image/png', buffer: Buffer.alloc(0) });
  await expect(page.getByRole('alert')).toContainText('smaller than');
  const config = await (await page.request.get('/api/config')).json();
  await upload.setInputFiles({ name: 'too-large.png', mimeType: 'image/png', buffer: Buffer.alloc(config.max_upload_bytes + 1) });
  await expect(page.getByRole('alert')).toContainText('smaller than');
  await expect(page.getByRole('img', { name: 'Your selected photograph', exact: true })).toHaveCount(0);
  await page.getByRole('button', { name: 'Dismiss message', exact: true }).click();
  await expect(page.getByRole('alert')).toHaveCount(0);
});

test('camera option uses the rear-camera capture input and the same preview validation', async ({ page }) => {
  await expect(page.getByLabel('Take a photograph', { exact: true })).toHaveAttribute('capture', 'environment');
  const chooser = page.waitForEvent('filechooser');
  await page.getByRole('button', { name: 'Use camera', exact: true }).click();
  await (await chooser).setFiles(photo('camera-photo.png'));
  await expect(page.getByRole('img', { name: 'Your selected photograph', exact: true })).toBeVisible();
  await expect(page.getByText('camera-photo.png', { exact: true })).toBeVisible();
});

test('print calls the browser and reveals a cumulative six-step worksheet', async ({ page }) => {
  const lesson = await demo(page, 'flower');
  await page.evaluate(() => { window.print = () => { document.documentElement.dataset.printCalled = 'true'; }; });
  await page.getByRole('button', { name: 'Print guide', exact: true }).click();
  await expect(page.locator('html')).toHaveAttribute('data-print-called', 'true');
  await expect(page.getByLabel('Printable drawing worksheet', { exact: true })).toBeHidden();
  await page.emulateMedia({ media: 'print' });
  const worksheet = page.getByLabel('Printable drawing worksheet', { exact: true });
  await expect(worksheet).toBeVisible();
  await expect(page.locator('.app-shell')).toBeHidden();
  await expect(worksheet.locator('.worksheet-step')).toHaveCount(6);
  let count = 0;
  for (const [index, group] of lesson.groups.entries()) {
    count += group.strokes.length;
    const step = worksheet.locator('.worksheet-step').nth(index);
    await expect(step.locator('[data-stroke-id]')).toHaveCount(count);
    await expect(step).toContainText(group.instruction);
    await expect(step.locator('[data-stroke-state="previous"]')).toHaveCount(0);
  }
  await expect(worksheet.locator('.worksheet-overview [data-stroke-id]')).toHaveCount(count);
});

test('welcome and lesson fit narrow screens and keep main drawing controls touch-friendly', async ({ page }) => {
  for (const width of [320, 375, 1280]) {
    await page.setViewportSize({ width, height: 900 });
    await assertNoOverflow(page);
    const box = await page.getByRole('button', { name: 'Pick a photo', exact: true }).boundingBox();
    expect(box!.height).toBeGreaterThanOrEqual(44);
  }
  await demo(page, 'house');
  await page.getByRole('button', { name: 'Let’s start drawing' }).click();
  for (const width of [320, 375, 1280]) {
    await page.setViewportSize({ width, height: 900 });
    await assertNoOverflow(page);
    for (const name of ['Previous', 'Next step', 'Show next line']) {
      const box = await page.getByRole('button', { name, exact: true }).boundingBox();
      expect(box!.height).toBeGreaterThanOrEqual(44);
    }
  }
});
