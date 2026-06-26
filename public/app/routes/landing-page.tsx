import type { Route } from "./+types/landing-page";
import { HeroSection } from "./components/hero-section";
import { AboutSection } from "./components/about";
import { PricingSection } from "./components/pricing";
import { WhyBestSection } from "./components/why-best";
import { ReviewsSection } from "./components/reviews";
import { SiteFooter } from "./components/site-footer";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Kamara.AI | Learning Journey" },
    {
      name: "description",
      content: "Empower your learning journey with Artificial Intelligence.",
    },
  ];
}

export default function LandingPage() {
  return (
    <>
      <HeroSection />
      <AboutSection />
      <WhyBestSection />
      <PricingSection />
      <ReviewsSection />
      <SiteFooter />
    </>
  );
}
