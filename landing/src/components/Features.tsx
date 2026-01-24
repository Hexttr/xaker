import { 
  Shield, 
  Zap, 
  FileCheck, 
  GitBranch, 
  Bell, 
  Globe,
  Cpu,
  Lock
} from "lucide-react";
import DashboardPreview from "./DashboardPreview";

const topFeatures = [
  {
    icon: Cpu,
    title: "AI + Machine Learning",
    description: "Advanced algorithms automate what previously required expert pentesters. Continuous model training.",
  },
  {
    icon: Shield,
    title: "Continuous Scanning",
    description: "Constant monitoring of all web applications without downtime. Detect vulnerabilities as they appear.",
  },
  {
    icon: GitBranch,
    title: "DevOps Integrations",
    description: "GitHub, GitLab, Jira, Jenkins — integrates into your team's existing workflow.",
  },
  {
    icon: FileCheck,
    title: "Compliance Reports",
    description: "Ready-made reports for audits: ISO 27001, GDPR, PCI-DSS, SOC2.",
  },
];

const additionalFeatures = [
  { icon: Bell, text: "Real-time alerts in Slack, Telegram, Email" },
  { icon: Lock, text: "100× cheaper than traditional pentests" },
  { icon: Zap, text: "Start scanning in 5 minutes" },
];

const Features = () => {
  return (
    <section id="features" className="py-24 bg-background relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-primary/30 to-transparent" />

      <div className="container mx-auto px-6">
        {/* Section Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-md bg-primary/10 border border-primary/20 mb-6">
            <Zap className="h-4 w-4 text-primary" />
            <span className="text-sm font-medium text-primary">Features</span>
          </div>
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-6">
            Everything for{" "}
            <span className="text-gradient">enterprise security</span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Complete toolkit to protect your infrastructure
          </p>
        </div>

        {/* Two-column layout: Features + Dashboard */}
        <div className="grid lg:grid-cols-2 gap-12 items-start">
          {/* Left: Features */}
          <div className="space-y-8">
            {/* Top 4 Features as cards */}
            <div className="grid sm:grid-cols-2 gap-4">
              {topFeatures.map((feature) => (
                <div
                  key={feature.title}
                  className="group p-6 rounded-lg bg-card border border-border/50 hover:border-primary/30 transition-all duration-300 hover:shadow-xl"
                >
                  <div className="h-12 w-12 rounded-md bg-primary/10 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                    <feature.icon className="h-6 w-6 text-primary" />
                  </div>
                  <h3 className="text-base font-semibold mb-2 text-foreground">{feature.title}</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">{feature.description}</p>
                </div>
              ))}
            </div>

            {/* Additional features as compact list */}
            <div className="p-6 rounded-lg bg-secondary/30 border border-border/30">
              <h4 className="text-sm font-semibold text-foreground mb-4 uppercase tracking-wider">Also Included</h4>
              <div className="grid sm:grid-cols-2 gap-3">
                {additionalFeatures.map((feature, index) => (
                  <div key={index} className="flex items-center gap-3">
                    <div className="h-8 w-8 rounded-md bg-primary/10 flex items-center justify-center flex-shrink-0">
                      <feature.icon className="h-4 w-4 text-primary" />
                    </div>
                    <span className="text-sm text-foreground">{feature.text}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right: Interactive Dashboard */}
          <div className="lg:sticky lg:top-24">
            <DashboardPreview />
          </div>
        </div>
      </div>
    </section>
  );
};

export default Features;
