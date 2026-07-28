import whyBestImage from "../../assets/hero2.jpg";

const reasons = [
  {
    title: "Tailored to You",
    body: "Every lesson adapts dynamically to your pace, goals, and current depth of understanding. No generic lectures.",
  },
  {
    title: "Natural Voice Conversations",
    body: "Speak directly with an AI teacher that explains complex concepts step-by-step in fluid, real-time dialogue.",
  },
  {
    title: "Interactive Visual Whiteboard",
    body: "Watch concepts come to life as Kamara writes equations, draws visual diagrams, and solves problems together with you.",
  },
  {
    title: "Continuous Progress",
    body: "Pick up right where you left off. Revisit auto-generated session notes, review previous whiteboards, and master subjects at your speed.",
  },
];

export function WhyBestSection() {
  return (
    <section className="why-best-section" aria-labelledby="why-best-heading">
      <div className="why-best-shell">
        <div className="why-best-copy reveal">
          <h2 id="why-best-heading" className="reveal delay-1">
            Guided by Principles,
            <br />
            Driven by Innovation
          </h2>
          <p className="reveal delay-2">
            We believe in building educational experiences that prioritize
            clarity, support, and steady progress. Kamara is designed to help
            learners feel confident from the very first step.
          </p>

          <div className="why-best-layout">
            <div className="why-best-media reveal reveal-left">
              <img
                src={whyBestImage}
                alt="Students collaborating around a laptop"
              />
            </div>

            <div className="why-best-list" aria-label="Why Kamara AI is best">
              {reasons.map((reason, index) => (
                <article
                  className={`why-best-item${index === 0 ? " is-active" : ""} reveal delay-${index + 3}`}
                  key={reason.title}
                >
                  <span className="why-best-item-number" aria-hidden="true">
                    {index + 1}
                  </span>
                  <div className="why-best-item-content">
                    <h3>{reason.title}</h3>
                    <p>{reason.body}</p>
                  </div>
                </article>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
