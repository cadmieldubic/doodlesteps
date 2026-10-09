import { useEffect, useRef, useState } from 'react';
import { ArrowLeft, ArrowRight, Camera, Check, ChevronLeft, ChevronRight, Heart, ImagePlus, Leaf, LoaderCircle, Pencil, Plus, Printer, RotateCcw, ShieldCheck, Sparkles, Star, Trash2, X } from 'lucide-react';
import { fetchConfig, fetchDemos, generateLesson } from './api';
import type { AppConfig, Lesson } from './schema';
import { Sketch } from './components/Sketch';
import { Worksheet } from './components/Worksheet';

type Photo = { file: File; url: string };
const fallbackFormats = ['image/jpeg', 'image/png', 'image/webp'];

function Brand({ onHome }: { onHome: () => void }) {
  return <button className="brand" onClick={onHome} aria-label="DoodleSteps home"><span className="brand-icon"><Pencil size={26} strokeWidth={2.2} /></span><span>Doodle<span className="brand-soft">Steps</span><span className="brand-spark">✦</span></span></button>;
}
function ErrorNotice({ message, onDismiss }: { message: string; onDismiss?: () => void }) {
  return <div className="error-notice" role="alert"><span>{message}</span>{onDismiss && <button className="icon-button" aria-label="Dismiss message" onClick={onDismiss}><X size={18} /></button>}</div>;
}
function PaperStars() {
  return <div className="paper-stars" aria-hidden="true"><Star className="star-one" size={26} /><Star className="star-two" size={15} /><span className="dot-one" /><span className="dot-two" /></div>;
}
function DemoCards({ demos, loading, error, onSelect, onRetry }: { demos: Lesson[]; loading: boolean; error: string; onSelect: (lesson: Lesson) => void; onRetry: () => void }) {
  return <section className="demo-section" aria-labelledby="demo-heading">
    <div className="section-heading"><div><span className="eyebrow">A little inspiration</span><h2 id="demo-heading">Try a tiny masterpiece</h2></div><span className="hand-note">No photo needed <span aria-hidden="true">↙</span></span></div>
    <div className="demo-grid">
      {loading && [0, 1, 2].map((index) => <div className="demo-card demo-skeleton" key={index}><div className="skeleton-picture" /><div className="skeleton-title" /></div>)}
      {demos.map((demo, index) => <button key={demo.id} className={`demo-card demo-${index}`} onClick={() => onSelect(demo)} aria-label={`Try ${demo.title} demo lesson`}>
        <span className="demo-label">Demo lesson</span><div className="demo-picture"><Sketch lesson={demo} /></div><div className="demo-card-footer"><div><h3>{demo.title}</h3><p>{demo.groups.length} easy steps <span aria-hidden="true">·</span> Pencil & paper</p></div><span className="round-arrow"><ArrowRight size={21} /></span></div>
      </button>)}
    </div>
    {error && <div className="demo-error"><ErrorNotice message={error} /><button className="button secondary" onClick={onRetry}><RotateCcw size={16} />Try again</button></div>}
  </section>;
}

function Welcome({ demos, loading, demoError, onDemo, onRetry, onUpload, onCamera }: { demos: Lesson[]; loading: boolean; demoError: string; onDemo: (lesson: Lesson) => void; onRetry: () => void; onUpload: () => void; onCamera: () => void }) {
  return <>
    <section className="hero">
      <div className="hero-copy"><span className="pill"><Sparkles size={15} />Little lines, big imaginations</span><h1 aria-label="Every picture can become a drawing!">Every picture can<br />become a <span className="drawing-word">drawing<svg viewBox="0 0 320 20" aria-hidden="true"><path d="M4 12 C65 3 173 5 314 8 M15 18 C120 12 230 12 300 14" /></svg></span>!</h1><p>Turn a favorite photo into a playful drawing lesson.<br className="desktop-break" /> Grab a pencil. We’ll take it one little step at a time.</p>
        <div className="hero-actions"><button className="button primary" onClick={onUpload}><ImagePlus size={21} />Pick a photo<ArrowRight size={18} /></button><button className="button camera-button" onClick={onCamera}><Camera size={20} />Use camera</button></div>
        <div className="hero-footnote"><Heart size={14} />Made for little artists, with a grown-up nearby.</div>
      </div>
      <div className="hero-art"><PaperStars /><div className="sketchbook"><div className="spiral" aria-hidden="true">{Array.from({ length: 7 }, (_, index) => <span key={index} />)}</div><div className="sketchbook-title"><span>my little drawing book</span><Heart size={15} /></div>{demos[0] ? <Sketch lesson={demos[0]} label="A playful puppy drawing from a demo lesson" /> : <svg className="sketch" viewBox="0 0 1000 1000" role="img" aria-label="A simple illustrated flower"><g fill="none" stroke="#6b6172" strokeWidth="8" strokeLinecap="round"><path d="M500 555 Q505 700 480 810 M488 730 Q355 735 390 630 Q455 630 488 730 M500 685 Q620 705 633 608 Q548 605 500 685" /><ellipse cx="500" cy="395" rx="90" ry="95" /><ellipse cx="500" cy="249" rx="65" ry="85" /><ellipse cx="641" cy="346" rx="85" ry="65" /><ellipse cx="586" cy="514" rx="65" ry="85" /><ellipse cx="409" cy="514" rx="65" ry="85" /><ellipse cx="360" cy="346" rx="85" ry="65" /></g></svg>}<div className="sketchbook-caption">a few lines. a whole lot of joy.</div></div><span className="art-badge"><span aria-hidden="true">✦</span> You can draw this!</span><div className="pencil-decoration" aria-hidden="true" /></div>
    </section>
    <div className="how-it-works" aria-label="How it works"><div><span className="how-number peach-bg">1</span><span><strong>Pick a picture</strong><small>A pet, a flower, a favorite thing</small></span></div><span className="how-connector" aria-hidden="true">⤳</span><div><span className="how-number lavender-bg">2</span><span><strong>Meet your sketch</strong><small>Simple shapes with a little charm</small></span></div><span className="how-connector" aria-hidden="true">⤳</span><div><span className="how-number mint-bg">3</span><span><strong>Draw, step by step</strong><small>On real paper, at your own pace</small></span></div></div>
    <DemoCards demos={demos} loading={loading} error={demoError} onSelect={onDemo} onRetry={onRetry} />
    <div className="kind-note"><Leaf size={19} /><p>A little reminder: there’s no perfect drawing. There’s only <strong>your</strong> drawing.</p></div>
  </>;
}

function PhotoSelection({ photo, config, configError, busy, checkingPhoto, onReplace, onRemove, onGenerate, onCancel, onRetryConfig }: { photo: Photo; config: AppConfig | null; configError: string; busy: boolean; checkingPhoto: boolean; onReplace: () => void; onRemove: () => void; onGenerate: () => void; onCancel: () => void; onRetryConfig: () => void }) {
  return <section className="photo-section"><div className="center-heading"><span className="eyebrow">Your picture, your adventure</span><h1>{busy ? 'Finding the little lines…' : 'What shall we draw today?'}</h1><p>{busy ? 'We’re noticing the shapes and making a gentle drawing plan.' : 'Choose one clear subject. A pet, flower, toy, or simple object works beautifully.'}</p></div>
    <div className="photo-layout"><div className="photo-preview"><div className="photo-sticker">Our inspiration <Heart size={14} /></div><img src={photo.url} alt="Your selected photograph" /><span className="photo-filename">{photo.file.name}</span></div><div className="photo-details">
      {busy ? <div className="generation-card" role="status"><div className="generation-spinner"><Pencil size={28} /></div><h2>A little imagination is at work</h2><p>First we understand your photo. Then we build one drawing and its steps. This can take a minute or two.</p><div className="generation-dots" aria-hidden="true"><span /><span /><span /></div><button className="button secondary" onClick={onCancel}>Cancel request</button></div> : <>
        <h2>That’s a lovely starting point.</h2><p>We’ll turn the main subject into simple, friendly shapes you can draw with a pencil.</p>
        <div className="privacy-note"><ShieldCheck size={21} /><div><strong>A grown-up should help</strong><p>Use non-personal photos for this private prototype. Live AI sends the photo to OpenAI for processing. We don’t keep photos on our server.</p></div></div>
        {!config?.ai_available && <div className="developer-note"><strong>{configError ? 'The drawing service is unavailable' : 'Photo lessons need a little setup'}</strong><p>{configError || 'Demo lessons are ready to try. For live photo lessons, an adult developer must add OPENAI_API_KEY to the backend .env file and restart the backend. The key stays on the server.'}</p>{configError && <button className="text-button" onClick={onRetryConfig}>Check connection again</button>}</div>}
        <button className="button primary generate-button" onClick={onGenerate} disabled={!config?.ai_available || checkingPhoto}><Sparkles size={20} />Create my drawing lesson</button><div className="photo-edit-actions"><button className="button secondary" onClick={onReplace}><ImagePlus size={18} />Replace photo</button><button className="text-button" onClick={onRemove}><Trash2 size={16} />Remove</button></div>
      </>}
    </div></div>
  </section>;
}

function LessonView({ lesson, photo, onComplete, onNew }: { lesson: Lesson; photo: Photo | null; onComplete: () => void; onNew: () => void }) {
  const [view, setView] = useState<'finished' | 'steps'>('finished');
  const [step, setStep] = useState(0);
  const [revealed, setRevealed] = useState(1);
  const [showPhoto, setShowPhoto] = useState(false);
  const group = lesson.groups[step];
  const chooseStep = (index: number, showAll = false) => { setStep(index); setRevealed(showAll ? lesson.groups[index].strokes.length : 1); setView('steps'); };
  const print = () => window.print();
  return <section className="lesson-section">
    <div className="lesson-heading"><div><div className="lesson-meta"><span className={`pill ${lesson.source === 'demo' ? 'demo-pill' : 'ai-pill'}`}>{lesson.source === 'demo' ? 'Demo lesson' : 'Photo-inspired AI lesson'}</span><span>{lesson.groups.length} little steps <span aria-hidden="true">·</span> {lesson.analysis.difficulty === 'easy' ? 'Beginner friendly' : 'A little challenge'}</span></div><h1>{lesson.title}</h1><p>{lesson.description}</p></div><button className="button secondary print-button" onClick={print}><Printer size={18} />Print guide</button></div>
    <div className="view-switch" role="tablist" aria-label="Drawing views"><button id="finished-tab" role="tab" aria-controls="drawing-panel" aria-selected={view === 'finished'} className={view === 'finished' ? 'active' : ''} onClick={() => setView('finished')}><Sparkles size={18} />Finished sketch</button><button id="steps-tab" role="tab" aria-controls="drawing-panel" aria-selected={view === 'steps'} className={view === 'steps' ? 'active' : ''} onClick={() => setView('steps')}><Pencil size={18} />Step-by-step guide</button></div>
    <div className="lesson-layout" id="drawing-panel" role="tabpanel" aria-labelledby={view === 'finished' ? 'finished-tab' : 'steps-tab'}>
      <div className="drawing-stage"><div className="drawing-corner"><span aria-hidden="true">✦</span>{view === 'finished' ? 'Your little masterpiece' : `Step ${step + 1} of ${lesson.groups.length}`}</div><Sketch lesson={lesson} step={view === 'steps' ? step : undefined} revealed={view === 'steps' ? revealed : undefined} />
        {view === 'steps' && <div className="stroke-key"><span><i className="previous-dot" />Already drawn</span><span><i className="current-dot" />New little lines</span></div>}
        {photo && <div className="reference-area"><button className="reference-button" onClick={() => setShowPhoto(!showPhoto)} aria-expanded={showPhoto}><img src={photo.url} alt="" /><span>{showPhoto ? 'Hide' : 'See'} original photo</span><Plus size={16} /></button>{showPhoto && <img className="reference-expanded" src={photo.url} alt="Original photograph for your drawing reference" />}</div>}
      </div>
      <div className="instruction-card">
        {view === 'finished' ? <><span className="large-spark" aria-hidden="true">✦</span><span className="eyebrow">Look what you can make</span><h2>Big pictures start<br />with little lines.</h2><p>Grab some paper and a pencil. We’ll build this drawing together, one simple shape at a time.</p><div className="materials-note"><Pencil size={17} /><span>Paper + pencil + your imagination</span></div><button className="button primary" onClick={() => setView('steps')}>Let’s start drawing<ArrowRight size={19} /></button><p className="encouragement">Take your time. You’ve got this.</p></> : <>
          <div className="step-progress" aria-label={`Step ${step + 1} of ${lesson.groups.length}`}>{lesson.groups.map((item, index) => <span key={item.id} className={index <= step ? 'done' : ''} />)}</div><span className="eyebrow">Little step {step + 1}</span><h2>{group.title}</h2><p className="step-instruction" aria-live="polite">{group.instruction}</p>
          <div className="reveal-controls"><span>{revealed} of {group.strokes.length} lines shown</span><button className="button secondary" disabled={revealed >= group.strokes.length} onClick={() => setRevealed((count) => count + 1)}><Plus size={18} />Show next line</button>{revealed < group.strokes.length && <button className="text-button show-all" onClick={() => setRevealed(group.strokes.length)}>Show all lines in this step</button>}</div>
          <div className="lesson-nav"><button className="button secondary previous-button" disabled={step === 0} onClick={() => chooseStep(step - 1, true)}><ChevronLeft size={19} />Previous</button><button className="button primary next-button" onClick={() => step === lesson.groups.length - 1 ? onComplete() : chooseStep(step + 1)}>{step === lesson.groups.length - 1 ? 'Finish drawing' : 'Next step'}{step === lesson.groups.length - 1 ? <Check size={19} /> : <ChevronRight size={19} />}</button></div><p className="encouragement">Your lines don’t have to be perfect. Just yours.</p>
        </>}
      </div>
    </div>
    <div className="step-thumbnails" aria-label="Choose a drawing step">{lesson.groups.map((item, index) => <button key={item.id} onClick={() => chooseStep(index)} className={view === 'steps' && index === step ? 'active' : ''} aria-current={view === 'steps' && index === step ? 'step' : undefined} aria-label={`Go to step ${index + 1}: ${item.title}`}><span className="thumbnail-number">{index + 1}</span><Sketch lesson={lesson} step={index} highlight={false} /><span className="thumbnail-label">{item.title}</span></button>)}</div>
    <button className="text-button another-photo" onClick={onNew}><ImagePlus size={17} />Start with another picture</button>
  </section>;
}

function Completed({ lesson, onRestart, onNew }: { lesson: Lesson; onRestart: () => void; onNew: () => void }) {
  return <section className="completed-section"><div className="celebration" aria-hidden="true">{['✦', '•', '✧', '•', '✦', '•', '✧'].map((symbol, index) => <span key={index} style={{ '--index': index } as React.CSSProperties}>{symbol}</span>)}</div><span className="pill"><Star size={16} />Look at you, little artist!</span><h1>You made something<br /><span className="lavender-text">wonderful.</span></h1><p>A few little lines became a whole drawing. That’s your imagination at work!</p><div className="completed-sketch"><PaperStars /><Sketch lesson={lesson} /></div><div className="completed-actions"><button className="button primary" onClick={() => window.print()}><Printer size={19} />Print drawing guide</button><button className="button secondary" onClick={onRestart}><RotateCcw size={18} />Draw it again</button><button className="text-button" onClick={onNew}><ImagePlus size={18} />Pick another photo</button></div></section>;
}

export default function App() {
  const [config, setConfig] = useState<AppConfig | null>(null);
  const [demos, setDemos] = useState<Lesson[]>([]);
  const [loading, setLoading] = useState(true);
  const [demoError, setDemoError] = useState('');
  const [configError, setConfigError] = useState('');
  const [error, setError] = useState('');
  const [photo, setPhoto] = useState<Photo | null>(null);
  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [completed, setCompleted] = useState(false);
  const [busy, setBusy] = useState(false);
  const [checkingPhoto, setCheckingPhoto] = useState(false);
  const [loadVersion, setLoadVersion] = useState(0);
  const [lessonVersion, setLessonVersion] = useState(0);
  const uploadRef = useRef<HTMLInputElement>(null);
  const cameraRef = useRef<HTMLInputElement>(null);
  const requestRef = useRef<AbortController | null>(null);
  const photoSequence = useRef(0);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setDemoError('');
    setConfigError('');
    fetchConfig(controller.signal).then(setConfig).catch((issue: Error) => { if (!controller.signal.aborted) { setConfig(null); setConfigError(issue.message); } });
    fetchDemos(controller.signal).then(setDemos).catch((issue: Error) => { if (!controller.signal.aborted) setDemoError(issue.message); }).finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [loadVersion]);
  useEffect(() => () => { if (photo) URL.revokeObjectURL(photo.url); }, [photo]);
  useEffect(() => () => requestRef.current?.abort(), []);

  const home = () => { requestRef.current?.abort(); photoSequence.current += 1; setPhoto(null); setLesson(null); setCompleted(false); setBusy(false); setCheckingPhoto(false); setError(''); window.scrollTo({ top: 0, behavior: 'smooth' }); };
  const choosePhoto = async (file?: File) => {
    if (!file) return;
    const sequence = ++photoSequence.current;
    requestRef.current?.abort();
    requestRef.current = null;
    setBusy(false);
    setError('');
    setCheckingPhoto(false);
    const formats: string[] = config?.supported_formats ?? fallbackFormats;
    const max = config?.max_upload_bytes ?? 8 * 1024 * 1024;
    if (!formats.includes(file.type)) { setError('Please choose a JPEG, PNG, or WebP photograph.'); return; }
    if (!file.size || file.size > max) { setError(`Please choose a photo smaller than ${Math.round(max / 1024 / 1024)} MB.`); return; }
    setCheckingPhoto(true);
    const url = URL.createObjectURL(file);
    try {
      await new Promise<void>((resolve, reject) => {
        const image = new Image();
        const timeout = window.setTimeout(() => reject(new Error('decode timeout')), 10_000);
        image.onload = () => { window.clearTimeout(timeout); if (image.naturalWidth > 0 && image.naturalHeight > 0) resolve(); else reject(new Error('empty')); };
        image.onerror = () => { window.clearTimeout(timeout); reject(new Error('invalid')); };
        image.src = url;
      });
      if (sequence !== photoSequence.current) { URL.revokeObjectURL(url); return; }
      setPhoto({ file, url }); setLesson(null); setCompleted(false);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch { URL.revokeObjectURL(url); if (sequence === photoSequence.current) setError('That file doesn’t look like a readable photo. Please choose another image.'); }
    finally { if (sequence === photoSequence.current) setCheckingPhoto(false); }
  };
  const generate = async () => {
    if (!photo || !config?.ai_available || busy || checkingPhoto) return;
    const requestedPhoto = photo;
    const requestedSequence = photoSequence.current;
    const controller = new AbortController();
    requestRef.current = controller;
    setBusy(true); setError('');
    try { const result = await generateLesson(requestedPhoto.file, controller.signal); if (!controller.signal.aborted && requestedSequence === photoSequence.current) { setLesson(result); setCompleted(false); setLessonVersion((value) => value + 1); window.scrollTo({ top: 0, behavior: 'smooth' }); } }
    catch (issue) { if (!controller.signal.aborted) setError(issue instanceof Error ? issue.message : 'We couldn’t make that lesson. Please try again.'); }
    finally { if (requestRef.current === controller) { requestRef.current = null; setBusy(false); } }
  };
  const startDemo = (demo: Lesson) => { requestRef.current?.abort(); requestRef.current = null; photoSequence.current += 1; setCheckingPhoto(false); setBusy(false); setPhoto(null); setLesson(demo); setCompleted(false); setLessonVersion((value) => value + 1); setError(''); window.scrollTo({ top: 0, behavior: 'smooth' }); };
  const newPhoto = () => { home(); uploadRef.current?.click(); };

  return <>
    <div className="app-shell"><header className="site-header"><Brand onHome={home} /><span className="header-note"><span className="status-dot" />A little space to create</span>{(photo || lesson) && <button className="text-button back-home" onClick={home}><ArrowLeft size={16} />Back to home</button>}</header>
      <main>{error && <ErrorNotice message={error} onDismiss={() => setError('')} />}{checkingPhoto && <div className="checking-photo" role="status"><LoaderCircle size={18} className="spin" />Checking your photo…</div>}
        {lesson ? completed ? <Completed lesson={lesson} onRestart={() => { setCompleted(false); setLessonVersion((value) => value + 1); }} onNew={newPhoto} /> : <LessonView key={`${lesson.id}-${lessonVersion}`} lesson={lesson} photo={photo} onComplete={() => { setCompleted(true); window.scrollTo({ top: 0, behavior: 'smooth' }); }} onNew={newPhoto} /> : photo ? <PhotoSelection photo={photo} config={config} configError={configError} busy={busy} checkingPhoto={checkingPhoto} onReplace={() => uploadRef.current?.click()} onRemove={home} onGenerate={generate} onCancel={() => { requestRef.current?.abort(); setBusy(false); }} onRetryConfig={() => setLoadVersion((value) => value + 1)} /> : <Welcome demos={demos} loading={loading} demoError={demoError} onDemo={startDemo} onRetry={() => setLoadVersion((value) => value + 1)} onUpload={() => uploadRef.current?.click()} onCamera={() => cameraRef.current?.click()} />}
      </main>
      <footer className="site-footer"><span><Pencil size={14} />DoodleSteps <span aria-hidden="true">·</span> Made for the joy of making</span><span>Private prototype <span aria-hidden="true">·</span> Grown-up guidance required</span></footer>
      <input ref={uploadRef} className="visually-hidden" type="file" accept="image/jpeg,image/png,image/webp" aria-label="Upload a photograph" onChange={(event) => { void choosePhoto(event.target.files?.[0]); event.target.value = ''; }} />
      <input ref={cameraRef} className="visually-hidden" type="file" accept="image/jpeg,image/png,image/webp" capture="environment" aria-label="Take a photograph" onChange={(event) => { void choosePhoto(event.target.files?.[0]); event.target.value = ''; }} />
    </div>
    {lesson && <Worksheet lesson={lesson} />}
  </>;
}
