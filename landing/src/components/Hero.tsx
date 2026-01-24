import { Button } from "@/components/ui/button";
import { ArrowRight, Shield, Zap, Clock } from "lucide-react";
import HeroVisual from "./HeroVisual";
import { useRequestDemo } from "@/contexts/RequestDemoContext";

const Hero = () => {
  const { openModal } = useRequestDemo();
  
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-background">
      {/* Background Grid */}
      <div className="absolute inset-0 bg-grid opacity-30" />
      
      {/* Gradient Orbs */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/10 rounded-full blur-3xl animate-pulse-slow" />
      <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-primary/5 rounded-full blur-3xl animate-pulse-slow delay-500" />

      <div className="container mx-auto px-6 pt-32 pb-20 relative z-10">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          {/* Text Content */}
          <div className="text-center lg:text-left">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-md bg-primary/10 border border-primary/20 mb-10 animate-fade-up">
              <Shield className="h-4 w-4 text-primary" />
              <span className="text-sm font-medium text-primary">AI-Powered Security</span>
            </div>

            {/* Headline */}
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold leading-tight mb-8 animate-fade-up delay-100">
              Hackers find vulnerabilities in 15 minutes.{" "}
              <span className="text-gradient">We find them first.</span>
            </h1>

            {/* Subheadline */}
            <p className="text-lg md:text-xl text-muted-foreground mb-10 max-w-xl mx-auto lg:mx-0 animate-fade-up delay-200">
              <span className="text-foreground font-semibold">$499/mo</span> — continuous AI pentesting 24/7.{" "}
              That's 100× cheaper than a one-time audit.
            </p>

            {/* CTA */}
            <div className="flex flex-col items-center lg:items-start gap-4 mb-14 animate-fade-up delay-300">
              <Button variant="hero" size="xl" className="group" onClick={openModal}>
                Free audit in 15 minutes
                <ArrowRight className="h-5 w-5 transition-transform group-hover:translate-x-1" />
              </Button>
              <a 
                href="#solution" 
                className="text-sm text-muted-foreground hover:text-primary transition-colors flex items-center gap-1"
              >
                How it works
                <ArrowRight className="h-3 w-3" />
              </a>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-4 animate-fade-up delay-400">
              <div className="p-4 rounded-lg bg-card/50 border border-border/50 backdrop-blur-sm text-center lg:text-left">
                <div className="flex items-center justify-center lg:justify-start gap-2 mb-2">
                  <Zap className="h-4 w-4 text-primary" />
                  <span className="text-2xl md:text-3xl font-bold text-foreground">47</span>
                </div>
                <p className="text-sm text-muted-foreground">Critical/week</p>
              </div>
              <div className="p-4 rounded-lg bg-card/50 border border-border/50 backdrop-blur-sm text-center lg:text-left">
                <div className="flex items-center justify-center lg:justify-start gap-2 mb-2">
                  <Shield className="h-4 w-4 text-primary" />
                  <span className="text-2xl md:text-3xl font-bold text-foreground">0</span>
                </div>
                <p className="text-sm text-muted-foreground">Client breaches</p>
              </div>
              <div className="p-4 rounded-lg bg-card/50 border border-border/50 backdrop-blur-sm text-center lg:text-left">
                <div className="flex items-center justify-center lg:justify-start gap-2 mb-2">
                  <Clock className="h-4 w-4 text-primary" />
                  <span className="text-2xl md:text-3xl font-bold text-foreground">15 min</span>
                </div>
                <p className="text-sm text-muted-foreground">To first report</p>
              </div>
            </div>
          </div>

          {/* Visual */}
          <div className="relative animate-fade-up delay-300 hidden lg:block">
            <HeroVisual />
          </div>
        </div>
      </div>

      {/* Scroll indicator */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
        <div className="w-6 h-10 rounded-lg border-2 border-muted-foreground/30 flex items-start justify-center p-2">
          <div className="w-1 h-2 bg-primary rounded-full animate-pulse" />
        </div>
      </div>
    </section>
  );
};

export default Hero;
