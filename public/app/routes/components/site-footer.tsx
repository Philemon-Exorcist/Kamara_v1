import footerImage from "../../assets/hero1.jpg";
import { WaitlistForm } from "./waitlist";

const footerGroups = [
  {
    title: "Platform",
    links: ["AI Tutor", "Courses", "Study Plans", "Progress Tracking", "Pricing"],
  },
  {
    title: "Company",
    links: ["About Kamara", "Careers", "Blog", "Contact", "Partners"],
  },
  {
    title: "Resources",
    links: ["Help Center", "Student Guide", "Instructor Guide", "Privacy", "Terms"],
  },
  {
    title: "Learn",
    links: ["For Students", "For Schools", "For Teams", "Community", "Waitlist"],
  },
];

const socialLinks = ["IG", "IN", "X", "YT"];

export function SiteFooter() {
  return (
    <footer id="footer" className="site-footer" aria-labelledby="footer-heading">
      <div className="footer-shell reveal">
        <section className="footer-cta reveal delay-1" aria-labelledby="footer-heading">
          <img src={footerImage} alt="" aria-hidden="true" />
          <div className="footer-cta-copy reveal delay-2">
            <h2 id="footer-heading">Learn without limits</h2>
            <p>Join the Kamara AI waitlist for smarter study tools and early access.</p>
          </div>

          <WaitlistForm />
        </section>

        <div className="footer-links reveal delay-3">
          <div className="footer-brand-block">
            <a className="footer-brand" href="/">
              <span aria-hidden="true">K</span>
              Kamara AI
            </a>
            <p>
              Kamara AI is an e-learning platform helping learners build skills
              with guided courses, practical study plans, and AI support.
            </p>
          </div>

          {footerGroups.map((group) => (
            <nav className="footer-column reveal" aria-label={group.title} key={group.title}>
              <h3>{group.title}</h3>
              {group.links.map((link) => (
                <a href="/" key={link}>
                  {link}
                </a>
              ))}
            </nav>
          ))}

          <div className="footer-social">
            <h3>Follow Us</h3>
            <div>
              {socialLinks.map((link) => (
                <a href="/" key={link} aria-label={`Kamara AI on ${link}`}>
                  {link}
                </a>
              ))}
            </div>
          </div>
        </div>

        <div className="footer-bottom">
          <p>Copyright c 2026 Kamara AI. All rights reserved.</p>
          <div>
            <a href="/">Privacy Policy</a>
            <a href="/">Terms of Use</a>
          </div>
        </div>
      </div>
    </footer>
  );
}
