import whyBestImage from "../../assets/hero2.jpg";

const reasons = [
  {
    title: "Discover Courses",
    body: "Your journey begins with just one click, from basics to pro, wherever your goal starts.",
  },
  {
    title: "Flexible course plan",
    body: "Build a learning rhythm that fits your schedule and keeps progress easy to follow.",
  },
  {
    title: "AI powered Instructors",
    body: "Learn with clear guidance from tutors who know how to make complex ideas practical.",
  },
  {
    title: "Align Skills & Goals",
    body: "Match each course to your ambitions so every lesson moves you closer to the future you want.",
  },
];

export function WhyBestSection() {
  return (
    <section className="why-best-section" aria-labelledby="why-best-heading">
      <div className="why-best-shell">
        <div className="why-best-media reveal reveal-left">
          <div className="why-best-cloud" aria-hidden="true" />
          <img
            src={whyBestImage}
            alt="Students collaborating around a laptop"
          />
        </div>

        <div className="why-best-copy reveal">
          <h2 id="why-best-heading" className="reveal delay-1">Why we are best from others?</h2>
          <p className="reveal delay-2">
            Education that empowers skills that last a lifetime. Join the best
            platform for learning, unlock your potential with every course, and
            transform your future today.
          </p>

          <div className="why-best-list" aria-label="Why Kamara AI is best">
            {reasons.map((reason, index) => (
              <article
                className={`why-best-item${index === 0 ? " is-active" : ""} reveal delay-${index + 3}`}
                key={reason.title}
              >
                <span>{index + 1}</span>
                <div>
                  <h3>{reason.title}</h3>
                  <p>{reason.body}</p>
                </div>
              </article>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
