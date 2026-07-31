import { useState } from "react";
import { Plus, Minus } from "lucide-react";

const faqItems = [
  {
    question: "How does Kamara AI help me learn faster?",
    answer:
      "Kamara AI adapts lessons to your pace, explains concepts step by step, and helps you practice with guided support so learning feels clearer and more personal.",
  },
  {
    question: "Which subjects are supported?",
    answer:
      "We are starting with high-impact STEM subjects like Mathematics, Physics, Chemistry, Biology, and Computer Science, with more learning paths planned over time.",
  },
  {
    question: "Can I use Kamara AI on mobile?",
    answer:
      "Yes. The platform is designed to work smoothly across desktop and mobile so you can study wherever it is convenient.",
  },
  {
    question: "Do I need prior experience to get started?",
    answer:
      "No prior experience is needed. Kamara AI is built to support beginners as well as advanced learners by adjusting to your level.",
  },
];

export function FaqSection() {
  const [openIndex, setOpenIndex] = useState(0);

  return (
    <section id="faq" className="faq-section" aria-labelledby="faq-heading">
      <div className="faq-shell">
        <div className="faq-header reveal">
          <span className="faq-eyebrow">FAQs</span>
          <h2 id="faq-heading">
            <span className="faq-heading-line">Frequently Asked</span>
            <span className="faq-heading-line">Questions</span>
          </h2>
          <p>
            We are here to help with common questions about Kamara AI, how it works, and what you can expect.
          </p>
        </div>

        <div className="faq-panel reveal delay-1" aria-label="Frequently asked questions">
          {faqItems.map((item, index) => {
            const isOpen = index === openIndex;

            return (
              <article className={`faq-item${isOpen ? " is-open" : ""}`} key={item.question}>
                <button
                  type="button"
                  className="faq-question"
                  aria-expanded={isOpen}
                  aria-controls={`faq-answer-${index}`}
                  onClick={() => setOpenIndex(isOpen ? -1 : index)}
                >
                  <span className="faq-icon" aria-hidden="true">
                    {isOpen ? <Minus size={16} /> : <Plus size={16} />}
                  </span>
                  <span>{item.question}</span>
                </button>

                {isOpen ? (
                  <div id={`faq-answer-${index}`} className="faq-answer">
                    <p>{item.answer}</p>
                  </div>
                ) : null}
              </article>
            );
          })}
        </div>
      </div>
    </section>
  );
}
