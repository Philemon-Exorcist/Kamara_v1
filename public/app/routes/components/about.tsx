import { BookOpenCheck, Target, Sparkles } from "lucide-react";

const featureCards = [
  {
    title: "User-friendly Platform to learn more",
    body: "Explore small, focused lesson paths that help classroom learning sink in and become conveniently clear.",
    icon: <BookOpenCheck size={24} />,
  },
  {
    title: "Consistent study routines",
    body: "Build useful study routines with lessons, practice, and guidance that make progress easier to follow.",
    icon: <Target size={24} />,
  },
];

export function AboutSection() {
  return (
    <section id="about" className="about-section" aria-labelledby="about-heading">
      <div className="about-shell">
        <div className="about-copy reveal">
          <span className="about-eyebrow">Online Learning</span>
          <h2 id="about-heading">
            <span>Designed</span> For Real Life
          </h2>
          <p className="reveal delay-1">
            From foundational courses that lay the groundwork for your
            educational journey to advanced specializations, Kamara AI helps you
            build confidence through learning that fits real schedules.
          </p>

          <div className="about-features" aria-label="Learning benefits">
            {featureCards.map((feature, index) => (
              <article className={`about-feature-card reveal delay-${index + 2}`} key={feature.body}>
                <div className="about-card-icon" aria-hidden="true">
                  {feature.icon}
                </div>
                <h3>{feature.title}</h3>
                <p>{feature.body}</p>
              </article>
            ))}
          </div>
        </div>

        <div className="about-visual reveal delay-2" aria-label="Educational learning tools">
          <article className="about-floating-card reveal delay-4">
            <div className="about-card-icon" aria-hidden="true">
              <Sparkles size={24} />
            </div>
            <h3>User-friendly platform to learn</h3>
            <p>
              Packed with modern study classroom learning tools to be done
              conveniently.
            </p>
          </article>

          <div className="study-scene" aria-hidden="true">
            <div className="globe">
              <span className="globe-sphere" />
              <span className="globe-neck" />
              <span className="globe-stand" />
            </div>
            <div className="book-stack">
              <span className="book green" />
              <span className="book white" />
              <span className="book orange" />
              <span className="book yellow" />
              <span className="book blue" />
              <span className="book cream" />
              <span className="book red" />
              <span className="book gray" />
            </div>
            <div className="pencil" />
            <div className="paper paper-one" />
            <div className="paper paper-two" />
          </div>
        </div>
      </div>
    </section>
  );
}
