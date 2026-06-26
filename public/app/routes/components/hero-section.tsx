import { useEffect, useRef, useState } from "react";
import { ArrowRight, Play } from "lucide-react";
import heroImage from "../../assets/hero1.jpg";

const mentors = ["AM", "JL", "RK", "TN"];

const stats = [
  { value: "10+", label: "Years Experience" },
  { value: "200+", label: "Positive Reviews" },
  { value: "108K+", label: "Satisfaction Rate" },
  { value: "310+", label: "Trusted Partners" },
];

function StatCounter({ value }: { value: string }) {
  const [displayValue, setDisplayValue] = useState(0);
  const [hasStarted, setHasStarted] = useState(false);
  const elementRef = useRef<HTMLElement>(null);

  // Extract the numeric part (e.g., 108) and the suffix (e.g., K+)
  const numericPart = parseInt(value.replace(/[^0-9]/g, ""), 10) || 0;
  const suffix = value.replace(/[0-9]/g, "");

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setHasStarted(true);
        } else {
          setHasStarted(false);
          setDisplayValue(0);
        }
      },
      { threshold: 0.1 }
    );

    if (elementRef.current) observer.observe(elementRef.current);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    if (!hasStarted) return;

    let startTimestamp: number | null = null;
    const duration = 2000; // Animation lasts 2 seconds

    const animate = (timestamp: number) => {
      if (!startTimestamp) startTimestamp = timestamp;
      const progress = Math.min((timestamp - startTimestamp) / duration, 1);
      const easedProgress = 1 - Math.pow(1 - progress, 3); // Cubic ease-out for a smooth finish
      setDisplayValue(Math.floor(easedProgress * numericPart));
      if (progress < 1) window.requestAnimationFrame(animate);
    };

    window.requestAnimationFrame(animate);
  }, [hasStarted, numericPart]);

  return <strong ref={elementRef}>{displayValue}{suffix}</strong>;
}

export function HeroSection() {
  return (
    <section className="hero-section" aria-labelledby="hero-heading">
      <nav className="hero-nav" aria-label="Main navigation">
        <a className="brand" href="/">
          Kamara AI
        </a>
        <div className="nav-links ">
          <a className="hover " href="/">Home</a>
          <a className="hover " href="/about">About</a>
          <a  className="hover " href="/services">Services</a>
          <a className="hover " href="/advisor">Advisor</a>
          <a className="hover " href="/blog">Blog</a>
        </div>
        <div className="nav-actions ">
          <a className="hover" href="/signup">Sign Up</a>
          <a className="login-button cta" href="/login">
            Log In
          </a>
        </div>
      </nav>

      <div className="hero-content">
        <div className="hero-copy reveal">
          <h1 id="hero-heading">Empower your learning with Kamara AI</h1>
          <p>
            Transform your learning journey unlock your potential and take control
            your growth with every step forward confidence starts with knowledge
          </p>
          <div className="hero-actions">
            <a className="primary-button cta" href="/#footer">
              Join-waitlist <ArrowRight size={18} aria-hidden="true" style={{ marginLeft: '8px' }} />
            </a>
            <a className="secondary-button hover" href="#about">
              Learn More
            </a>
          </div>
          
        </div>

        <div className="hero-visual reveal delay-1" aria-label="Student learning online">
          

          <div className="student-frame">
            <img
              className="student-photo"
              src={heroImage}
              alt="Student learning online"
            />
          </div>

          

          <div className="course-card">
            <div className="play-icon-wrap" aria-hidden="true">
              <Play size={16} fill="currentColor" />
            </div>
            <strong>20K+</strong>
            <small>Online Course</small>
          </div>
        </div>
      </div>

      <div className="stats-strip reveal delay-2" aria-label="Skillz achievements">
        {stats.map((stat) => (
          <div className="stat-item" key={stat.label}>
            <StatCounter value={stat.value} />
            <span>{stat.label}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
