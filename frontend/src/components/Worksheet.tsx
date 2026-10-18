import type { Lesson } from '../schema';
import { Sketch } from './Sketch';

export function Worksheet({ lesson }: { lesson: Lesson }) {
  return <section className="worksheet" aria-label="Printable drawing worksheet">
    <div className="worksheet-heading"><div><strong>DoodleSteps</strong><h1>{lesson.title}</h1><p>A little line at a time.</p></div><p className="name-line">My name: ____________________</p></div>
    <div className="worksheet-overview"><Sketch lesson={lesson} highlight={false} printable /><div><h2>Let’s draw!</h2><p>{lesson.description}</p><p>Grab a pencil and paper. Start with light lines, follow the steps, and make the drawing your own.</p><span>{lesson.source === 'demo' ? 'Demo lesson' : 'Photo-inspired AI lesson'} · {lesson.groups.length} steps</span></div></div>
    <div className="worksheet-grid">{lesson.groups.map((group, index) => <div className="worksheet-step" key={group.id}>
      <Sketch lesson={lesson} step={index} highlight={false} printable />
      <h2>{index + 1}. {group.title}</h2><p>{group.instruction}</p>
    </div>)}</div>
    <footer>There’s no perfect drawing. There’s only your drawing. ✨ · DoodleSteps private prototype</footer>
  </section>;
}
