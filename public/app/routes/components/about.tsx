import { Check } from "lucide-react";
import aboutMainImage from "../../assets/abt.jpg";
import aboutSecondaryImage from "../../assets/abt2.jpg";

const storyPoints = [
  "Empowering learning with AI guidance",
  "Personalized support for every student",
  "Flexible help when you need it most",
  "Built to make learning feel simpler",
];

export function AboutSection() {
  return (
    <section id="about" className="about-section" aria-labelledby="about-heading">
      <div className="about-shell">
        <div className="about-visual reveal" aria-label="Kamara story imagery">
          <div className="about-photo about-photo-large">
            <img
              className="about-photo-image"
              src={aboutMainImage}
              alt="Kamara story main visual"
            />
          </div>
          <div className="about-photo about-photo-small">
            <img
              className="about-photo-image"
              src={aboutSecondaryImage}
              alt="Kamara story secondary visual"
            />
          </div>
        </div>

        <div className="about-copy reveal delay-1">
          <span className="about-eyebrow">About Kamara</span>
          <h2 id="about-heading">kamara.study</h2>
          <p className="about-intro">
            Learning shouldn't depend on your postcode, your budget, or whether you can afford a private
            tutor. At Kamara, we believe every student deserves a personal teacher tailored to their pace,
            goals, and unique way of understanding.
          </p>

          <div className="about-story">
            <p>
              Kamara is an AI-powered educator that delivers real-time, interactive lessons through natural
              voice conversations and an intelligent digital whiteboard. Instead of just giving answers, Kamara
              teaches step-by-step—drawing diagrams, breaking down complex formulas, adapting to your
              progress, and generating structured notes as you learn.
            </p>
            <p>
              We’re starting with high-impact STEM subjects—including Mathematics, Physics, Chemistry, and
              university-level courses—with a single goal: to make high-quality education as accessible as the
              internet itself.
            </p>
          </div>

          <ul className="about-points" aria-label="About Kamara highlights">
            {storyPoints.map((point) => (
              <li key={point}>
                <Check size={16} aria-hidden="true" />
                <span>{point}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}
