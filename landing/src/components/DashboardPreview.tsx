import { useState, useEffect } from "react";
import { Search, Shield, Key, Database, AlertTriangle, ChevronRight, Activity } from "lucide-react";

const attackChainSteps = [
  {
    id: 1,
    phase: "Reconnaissance",
    icon: Search,
    status: "completed",
    details: [
      { label: "Subdomains", value: "47 found" },
      { label: "Open ports", value: "12 services" },
      { label: "Technologies", value: "React, Node.js, PostgreSQL" },
    ],
  },
  {
    id: 2,
    phase: "Vulnerabilities",
    icon: Shield,
    status: "completed",
    details: [
      { label: "SQL Injection", value: "/api/users?id=", severity: "critical" },
      { label: "Broken Auth", value: "/api/admin/reset", severity: "critical" },
      { label: "IDOR", value: "/api/documents/{id}", severity: "high" },
    ],
  },
  {
    id: 3,
    phase: "Exploitation",
    icon: Key,
    status: "in-progress",
    details: [
      { label: "Access gained", value: "Admin JWT Token" },
      { label: "Privileges", value: "Escalation to root" },
      { label: "Lateral movement", value: "3 servers" },
    ],
  },
  {
    id: 4,
    phase: "Impact",
    icon: Database,
    status: "pending",
    details: [
      { label: "Data at risk", value: "2.3M records" },
      { label: "PII exposure", value: "Email, passwords, cards" },
      { label: "Business risk", value: "$4.5M potential damage" },
    ],
  },
];

const DashboardPreview = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [isAnimating, setIsAnimating] = useState(true);

  useEffect(() => {
    if (!isAnimating) return;
    
    const interval = setInterval(() => {
      setActiveStep((prev) => (prev + 1) % attackChainSteps.length);
    }, 3000);

    return () => clearInterval(interval);
  }, [isAnimating]);

  const getStatusColor = (status: string, isActive: boolean) => {
    if (isActive) return "border-primary bg-primary/20";
    switch (status) {
      case "completed":
        return "border-green-500/50 bg-green-500/10";
      case "in-progress":
        return "border-yellow-500/50 bg-yellow-500/10";
      default:
        return "border-border/50 bg-secondary/30";
    }
  };

  const getSeverityColor = (severity?: string) => {
    switch (severity) {
      case "critical":
        return "text-destructive";
      case "high":
        return "text-orange-500";
      default:
        return "text-foreground";
    }
  };

  return (
    <div 
      className="bg-card rounded-lg border border-border/50 overflow-hidden shadow-2xl"
      onMouseEnter={() => setIsAnimating(false)}
      onMouseLeave={() => setIsAnimating(true)}
    >
      {/* Header */}
      <div className="px-6 py-4 border-b border-border/50 flex items-center justify-between bg-secondary/30">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-md bg-primary/10 flex items-center justify-center">
            <svg viewBox="0 0 32 32" fill="none" className="h-5 w-5 text-primary">
              <path d="M16 2L4 7V15C4 22.5 9.5 29 16 30C22.5 29 28 22.5 28 15V7L16 2Z" fill="currentColor" fillOpacity="0.15" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="miter" />
              <text x="16" y="19" textAnchor="middle" fill="currentColor" fontSize="9" fontWeight="700" fontFamily="system-ui">AI</text>
            </svg>
          </div>
          <div>
            <h3 className="font-semibold text-foreground text-sm">Attack Chain Analysis</h3>
            <p className="text-xs text-muted-foreground">Real attack simulation</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-destructive/10 border border-destructive/20">
            <AlertTriangle className="h-3 w-3 text-destructive" />
            <span className="text-xs font-medium text-destructive">2 Critical</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Activity className="h-3 w-3 text-primary animate-pulse" />
            <span className="text-xs text-muted-foreground">Live</span>
          </div>
        </div>
      </div>

      {/* Attack Chain Timeline */}
      <div className="p-6">
        {/* Steps indicator */}
        <div className="flex items-center justify-between mb-8">
          {attackChainSteps.map((step, index) => (
            <div key={step.id} className="flex items-center">
              <button
                onClick={() => setActiveStep(index)}
                className={`flex flex-col items-center gap-2 transition-all duration-300 ${
                  activeStep === index ? "scale-110" : "opacity-60 hover:opacity-100"
                }`}
              >
                <div
                  className={`h-12 w-12 rounded-md flex items-center justify-center border-2 transition-all duration-300 ${getStatusColor(
                    step.status,
                    activeStep === index
                  )}`}
                >
                  <step.icon className={`h-5 w-5 ${activeStep === index ? "text-primary" : "text-muted-foreground"}`} />
                </div>
                <span className={`text-xs font-medium ${activeStep === index ? "text-primary" : "text-muted-foreground"}`}>
                  {step.phase}
                </span>
              </button>
              {index < attackChainSteps.length - 1 && (
                <ChevronRight className="h-4 w-4 text-muted-foreground/50 mx-2" />
              )}
            </div>
          ))}
        </div>

        {/* Active Step Details */}
        <div className="bg-secondary/30 rounded-lg border border-border/30 p-5">
          <div className="flex items-center gap-3 mb-4">
            <div className="h-10 w-10 rounded-md bg-primary/10 flex items-center justify-center">
              {(() => {
                const StepIcon = attackChainSteps[activeStep].icon;
                return <StepIcon className="h-5 w-5 text-primary" />;
              })()}
            </div>
            <div>
              <h4 className="font-semibold text-foreground">
                Step {activeStep + 1}: {attackChainSteps[activeStep].phase}
              </h4>
              <p className="text-xs text-muted-foreground">
                {activeStep === 0 && "Target information gathering"}
                {activeStep === 1 && "Vulnerability detection"}
                {activeStep === 2 && "Exploitation confirmation"}
                {activeStep === 3 && "Potential damage assessment"}
              </p>
            </div>
          </div>

          <div className="space-y-3">
            {attackChainSteps[activeStep].details.map((detail, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between p-3 rounded-md bg-background/50 border border-border/30"
              >
                <span className="text-sm text-muted-foreground">{detail.label}</span>
                <span className={`text-sm font-mono font-medium ${getSeverityColor((detail as any).severity)}`}>
                  {detail.value}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Bottom summary */}
        <div className="mt-6 pt-4 border-t border-border/30 flex items-center justify-between">
          <div className="text-xs text-muted-foreground">
            Full attack chain in <span className="text-primary font-medium">12 minutes</span>
          </div>
          <div className="flex items-center gap-4 text-xs">
            <span className="flex items-center gap-1.5">
              <div className="h-2 w-2 rounded-sm bg-green-500" />
              Completed
            </span>
            <span className="flex items-center gap-1.5">
              <div className="h-2 w-2 rounded-sm bg-yellow-500" />
              In progress
            </span>
            <span className="flex items-center gap-1.5">
              <div className="h-2 w-2 rounded-sm bg-muted" />
              Pending
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPreview;
