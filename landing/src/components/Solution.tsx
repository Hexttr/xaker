import { Button } from "@/components/ui/button";
import { ArrowRight, Sparkles, Clock, DollarSign, Shield } from "lucide-react";
import AIVisual from "./AIVisual";

const transformation = [
  { before: "2 pentests per year", after: "Continuous protection 24/7" },
  { before: "$50,000+ per assessment", after: "From $499/mo" },
  { before: "Report in 2 weeks", after: "Real-time alerts" },
  { before: "Manual test launches", after: "Auto CI/CD integration" },
];

const metrics = [
  {
    icon: Clock,
    value: "1000+",
    label: "Scanning Rules",
    description: "Constantly updated threat database",
  },
  {
    icon: DollarSign,
    value: "50+",
    label: "Integrations",
    description: "With popular DevOps tools",
  },
  {
    icon: Shield,
    value: "99.9%",
    label: "Uptime",
    description: "Guaranteed service availability",
  },
];

const Solution = () => {
  return (
    <section id="solution" className="py-24 bg-background relative overflow-hidden">
      {/* Background glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-primary/5 rounded-full blur-3xl" />

      <div className="container mx-auto px-6 relative z-10">
        {/* Section Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-md bg-primary/10 border border-primary/20 mb-6">
            <Sparkles className="h-4 w-4 text-primary" />
            <span className="text-sm font-medium text-primary">Solution</span>
          </div>
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-6">
            AI-powered platform for{" "}
            <span className="text-gradient">continuous pentesting</span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-3xl mx-auto">
            Pentest.red automates the vulnerability discovery process using 
            artificial intelligence and machine learning
          </p>
        </div>

        {/* Main Content */}
        <div className="grid lg:grid-cols-2 gap-16 items-center mb-20">
          {/* Left - Transformation */}
          <div>
            <h3 className="text-2xl font-bold mb-8 text-foreground">How your security transforms</h3>
            <div className="space-y-4 mb-8">
              {transformation.map((item, index) => (
                <div
                  key={item.after}
                  className="flex items-center gap-4 p-4 rounded-lg bg-card border border-border/50 hover:border-primary/30 transition-colors"
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  <div className="flex-1">
                    <p className="text-muted-foreground line-through text-sm">{item.before}</p>
                  </div>
                  <ArrowRight className="h-4 w-4 text-primary flex-shrink-0" />
                  <div className="flex-1">
                    <p className="font-semibold text-foreground">{item.after}</p>
                  </div>
                </div>
              ))}
            </div>
            <Button variant="hero" size="lg" className="group">
              Start free trial
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
            </Button>
          </div>

          {/* Right - AI Visual */}
          <div className="relative hidden lg:block">
            <AIVisual />
          </div>
        </div>

        {/* Metrics */}
        <div className="grid md:grid-cols-3 gap-8">
          {metrics.map((metric) => (
            <div
              key={metric.label}
              className="text-center p-8 rounded-lg bg-card border border-border/50 hover:border-primary/30 transition-all duration-300 hover:shadow-xl group"
            >
              <div className="h-16 w-16 rounded-lg bg-primary/10 flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform">
                <metric.icon className="h-8 w-8 text-primary" />
              </div>
              <div className="metric-value mb-2">{metric.value}</div>
              <h4 className="text-lg font-semibold mb-2 text-foreground">{metric.label}</h4>
              <p className="text-sm text-muted-foreground">{metric.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Solution;
