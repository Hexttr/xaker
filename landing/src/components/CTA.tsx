import { Button } from "@/components/ui/button";
import { ArrowRight, Mail, MessageCircle, Linkedin, Shield } from "lucide-react";

const CTA = () => {
  return (
    <section className="py-24 bg-background relative overflow-hidden">
      {/* Background effects */}
      <div className="absolute inset-0 bg-grid opacity-20" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-primary/10 rounded-full blur-3xl" />

      <div className="container mx-auto px-6 relative z-10">
        <div className="max-w-4xl mx-auto text-center">
          {/* Main CTA */}
          <div className="mb-16">
            <div className="inline-flex items-center justify-center h-20 w-20 rounded-lg bg-primary/10 mb-8 animate-glow">
              <Shield className="h-10 w-10 text-primary" />
            </div>
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-6">
              Get a free audit{" "}
              <span className="text-gradient">in 15 minutes</span>
            </h2>
            <p className="text-lg md:text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
              Discover how many vulnerabilities are hidden in your infrastructure right now. 
              No commitments, no hidden fees.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button variant="hero" size="xl" className="group" asChild>
                <a href="/app">
                  Launch free audit
                  <ArrowRight className="h-5 w-5 transition-transform group-hover:translate-x-1" />
                </a>
              </Button>
              <Button variant="heroOutline" size="xl" asChild>
                <a href="/app">Watch demo</a>
              </Button>
            </div>
          </div>

          {/* Contact Info */}
          <div className="pt-16 border-t border-border/50">
            <p className="text-sm text-muted-foreground mb-6">Contact us</p>
            <div className="flex flex-wrap justify-center gap-6">
              <a
                href="mailto:sales@pentest.red"
                className="flex items-center gap-2 px-6 py-3 rounded-lg bg-card border border-border/50 hover:border-primary/30 transition-colors group"
              >
                <Mail className="h-5 w-5 text-primary" />
                <span className="text-foreground group-hover:text-primary transition-colors">sales@pentest.red</span>
              </a>
              <a
                href="https://t.me/pentestred"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 px-6 py-3 rounded-lg bg-card border border-border/50 hover:border-primary/30 transition-colors group"
              >
                <MessageCircle className="h-5 w-5 text-primary" />
                <span className="text-foreground group-hover:text-primary transition-colors">@pentestred</span>
              </a>
              <a
                href="https://linkedin.com/company/pentestred"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 px-6 py-3 rounded-lg bg-card border border-border/50 hover:border-primary/30 transition-colors group"
              >
                <Linkedin className="h-5 w-5 text-primary" />
                <span className="text-foreground group-hover:text-primary transition-colors">/company/pentestred</span>
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default CTA;
