import { ArrowRight, BadgeCheck, BrainCircuit, ShieldCheck, Sparkles } from "lucide-react";

const pricingPlans = [
  {
    name: "Starter",
    price: "₦0",
    period: "/month",
    description: "A simple way to test AI-guided learning and get started quickly.",
    accent: "starter",
    features: [
      "2 AI tutoring sessions per week",
      "Basic curriculum guidance",
      "Quick progress dashboard",
      "Community support",
    ],
    cta: "Start free",
    icon: <BrainCircuit size={18} />,
  },
  {
    name: "Pro",
    price: "₦10,000",
    period: "/month",
    description: "For learners who want deeper feedback, live whiteboard coaching, and a stronger study routine.",
    accent: "featured",
    badge: "Most popular",
    features: [
      "Unlimited AI tutor sessions",
      "Live whiteboard + screen tools",
      "Curriculum builder and quiz mode",
      "Weekly progress summaries",
    ],
    cta: "Go Pro",
    icon: <Sparkles size={18} />,
  },
  {
    name: "Group",
    price: "₦20,000",
    period: "/month",
    description: "For ambitious learners and families who want full guidance, personalization, and coaching support.",
    accent: "premium",
    features: [
      "Everything in Pro",
      "Priority tutor access",
      "Advanced analytics and learning plans",
      "Dedicated parent / student support",
    ],
    cta: "Choose Premium",
    icon: <ShieldCheck size={18} />,
  },
];

export function PricingSection() {
  return (
    <section id="pricing" className="pricing-section" aria-labelledby="pricing-heading">
      <div className="pricing-shell">
        <div className="pricing-intro reveal">
          <span className="pricing-eyebrow">Pricing</span>
          <h2 id="pricing-heading">Choose the learning plan that fits your pace.</h2>
          <p>
            From first steps to confident mastery, each plan is built to match the
            same modern learning experience across the Kamara platform.
          </p>
        </div>

        <div className="pricing-grid" aria-label="Pricing options">
          {pricingPlans.map((plan, index) => (
            <article
              className={`pricing-card ${plan.accent} reveal delay-${index + 1}`}
              key={plan.name}
            >
              {plan.badge ? <span className="pricing-badge">{plan.badge}</span> : null}

              <div className="pricing-card-top">
                <div className="pricing-icon-wrap" aria-hidden="true">{plan.icon}</div>
                <h3>{plan.name}</h3>
                <p>{plan.description}</p>
              </div>

              <div className="pricing-price-row">
                <strong>{plan.price}</strong>
                <span>{plan.period}</span>
              </div>

              <ul className="pricing-features" aria-label={`${plan.name} features`}>
                {plan.features.map((feature) => (
                  <li key={feature}>
                    <BadgeCheck size={16} />
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>

              <a className={`pricing-cta ${plan.accent === "featured" ? "pricing-cta-primary" : ""}`} href="/signup">
                {plan.cta}
                <ArrowRight size={16} />
              </a>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
