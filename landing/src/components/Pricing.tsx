import { Button } from "@/components/ui/button";
import { Check, Star, ArrowRight } from "lucide-react";
import { useRequestDemo } from "@/contexts/RequestDemoContext";

const plans = [
  {
    name: "Starter",
    price: "$499",
    period: "",
    description: "Package of 3 audits: 1 app 3 times or 3 apps once each",
    audience: "Startups, SaaS",
    features: [
      "3 audits in package",
      "Full vulnerability report",
      "Attack Chain visualization",
      "Email support (24h SLA)",
      "GitHub/GitLab integration",
      "OWASP Top 10 coverage",
    ],
    cta: "Buy Package",
    popular: false,
  },
  {
    name: "Pro",
    price: "$2499",
    period: "/mo",
    description: "For growing companies with security teams",
    audience: "Mid-market, SaaS",
    features: [
      "Up to 15 applications",
      "Continuous scanning 24/7",
      "AI vulnerability analysis",
      "CI/CD pipeline integration",
      "Priority support (4h SLA)",
      "API access",
      "Real-time alerts",
    ],
    cta: "Choose Pro",
    popular: true,
  },
  {
    name: "Enterprise",
    price: "Custom",
    period: "",
    description: "For corporations with compliance requirements",
    audience: "Enterprise, Fintech",
    features: [
      "Unlimited applications",
      "Dedicated Success Manager",
      "SLA 99.9% + 1h response",
      "On-premise deployment",
      "Custom integrations",
      "Team training",
      "Pentest experts on demand",
    ],
    cta: "Request Demo",
    popular: false,
  },
];

const Pricing = () => {
  const { openModal } = useRequestDemo();
  
  return (
    <section id="pricing" className="py-24 bg-secondary/30 relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-primary/30 to-transparent" />

      <div className="container mx-auto px-6">
        {/* Section Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-md bg-primary/10 border border-primary/20 mb-6">
            <Star className="h-4 w-4 text-primary" />
            <span className="text-sm font-medium text-primary">Pricing</span>
          </div>
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-6">
            Transparent{" "}
            <span className="text-gradient">pricing</span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Choose the plan that fits your business. Start with a free trial.
          </p>
        </div>

        {/* Pricing Cards */}
        <div className="grid lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {plans.map((plan) => (
            <div
              key={plan.name}
              className={`relative rounded-lg p-8 border transition-all duration-300 hover:shadow-xl flex flex-col ${
                plan.popular
                  ? "bg-card border-primary shadow-lg scale-105"
                  : "bg-card border-border/50 hover:border-primary/30"
              }`}
            >
              {/* Popular Badge */}
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                  <div className="px-4 py-1 rounded-md bg-gradient-hero text-primary-foreground text-sm font-semibold">
                    Popular
                  </div>
                </div>
              )}

              {/* Plan Header */}
              <div className="mb-8">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-2xl font-bold text-foreground">{plan.name}</h3>
                  <span className="text-xs px-2 py-1 rounded-md bg-primary/10 text-primary">{plan.audience}</span>
                </div>
                <p className="text-muted-foreground mb-4 text-sm">{plan.description}</p>
                <div className="flex items-baseline">
                  <span className="text-4xl font-bold text-foreground">{plan.price}</span>
                  <span className="text-muted-foreground ml-1">{plan.period}</span>
                </div>
              </div>

              {/* Features */}
              <ul className="space-y-4 mb-8 flex-grow">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-center gap-3">
                    <div className="h-5 w-5 rounded-md bg-primary/10 flex items-center justify-center flex-shrink-0">
                      <Check className="h-3 w-3 text-primary" />
                    </div>
                    <span className="text-foreground">{feature}</span>
                  </li>
                ))}
              </ul>

              {/* CTA */}
              <Button
                variant={plan.popular ? "hero" : "heroOutline"}
                size="lg"
                className="w-full group"
                onClick={openModal}
              >
                {plan.cta}
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </Button>
            </div>
          ))}
        </div>

        {/* Additional Services */}
        <div className="mt-20">
          <p className="text-center text-muted-foreground mb-8 text-lg">Additional Services</p>
          <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            <div className="p-6 rounded-lg bg-card border border-border/50 hover:border-primary/30 transition-colors">
              <h4 className="text-lg font-semibold text-foreground mb-3">Vulnerability Remediation Consulting</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>• Expert review of each vulnerability</li>
                <li>• Code fix recommendations</li>
                <li>• Business impact prioritization</li>
                <li>• Post-fix validation</li>
              </ul>
            </div>
            <div className="p-6 rounded-lg bg-card border border-border/50 hover:border-primary/30 transition-colors">
              <h4 className="text-lg font-semibold text-foreground mb-3">Security Audit</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>• Comprehensive infrastructure assessment</li>
                <li>• Security policies & procedures analysis</li>
                <li>• Standards compliance testing</li>
                <li>• Improvement roadmap</li>
              </ul>
            </div>
            <div className="p-6 rounded-lg bg-card border border-border/50 hover:border-primary/30 transition-colors">
              <h4 className="text-lg font-semibold text-foreground mb-3">Incident Response</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>• 24/7 emergency response</li>
                <li>• Threat analysis & containment</li>
                <li>• System recovery</li>
                <li>• Post-incident report & recommendations</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Pricing;
