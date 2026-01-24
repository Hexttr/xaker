import Header from "@/components/Header";
import Hero from "@/components/Hero";
import TrustedBy from "@/components/TrustedBy";
import Problem from "@/components/Problem";
import Solution from "@/components/Solution";
import Features from "@/components/Features";
import Cases from "@/components/Cases";
import Comparison from "@/components/Comparison";
import Pricing from "@/components/Pricing";
import FAQ from "@/components/FAQ";
import CTA from "@/components/CTA";
import Footer from "@/components/Footer";
import StickyCTA from "@/components/StickyCTA";
import { RequestDemoProvider } from "@/contexts/RequestDemoContext";

const Index = () => {
  return (
    <RequestDemoProvider>
      <div className="min-h-screen bg-background dark">
        <Header />
        <main>
          <Hero />
          <TrustedBy />
          <Problem />
          <Solution />
          <Features />
          <Cases />
          <Comparison />
          <Pricing />
          <FAQ />
          <CTA />
        </main>
        <Footer />
        <StickyCTA />
      </div>
    </RequestDemoProvider>
  );
};

export default Index;
