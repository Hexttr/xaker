import { DollarSign, Clock, RefreshCw, AlertTriangle } from "lucide-react";

const problems = [
  {
    icon: DollarSign,
    title: "Prohibitive Cost",
    description: "Traditional pentests cost $50,000–500,000 per assessment. Out of reach for most companies.",
    stat: "$50K+",
    statLabel: "per assessment",
  },
  {
    icon: Clock,
    title: "Infrequent Testing",
    description: "Assessments are conducted 1-2 times a year. The rest of the time your infrastructure remains vulnerable.",
    stat: "1-2",
    statLabel: "times per year",
  },
  {
    icon: RefreshCw,
    title: "Constant Changes",
    description: "Web applications change daily, creating new vulnerabilities between rare assessments.",
    stat: "100+",
    statLabel: "changes/month",
  },
];

const Problem = () => {
  return (
    <section id="problem" className="py-28 bg-secondary/30 relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-primary/30 to-transparent" />
      
      <div className="container mx-auto px-6">
        {/* Section Header */}
        <div className="text-center mb-20">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-md bg-destructive/10 border border-destructive/20 mb-8">
            <AlertTriangle className="h-4 w-4 text-destructive" />
            <span className="text-sm font-medium text-destructive">The Problem</span>
          </div>
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-8">
            Average cost of a data breach —{" "}
            <span className="text-gradient">$4.45M</span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            And traditional pentesting only checks you 1-2 times a year. 
            How many vulnerabilities will appear between assessments?
          </p>
        </div>

        {/* Problem Cards */}
        <div className="grid md:grid-cols-3 gap-10 mb-16">
          {problems.map((problem, index) => (
            <div
              key={problem.title}
              className="group relative bg-card rounded-lg p-8 border border-border/50 hover:border-destructive/30 transition-all duration-300 hover:shadow-xl"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              {/* Stat - now prominent at top */}
              <div className="mb-6">
                <span className="text-4xl md:text-5xl font-bold text-gradient">{problem.stat}</span>
                <span className="text-sm text-muted-foreground ml-2">{problem.statLabel}</span>
              </div>

              {/* Icon + Title */}
              <div className="flex items-center gap-3 mb-4">
                <div className="h-10 w-10 rounded-md bg-destructive/10 flex items-center justify-center">
                  <problem.icon className="h-5 w-5 text-destructive" />
                </div>
                <h3 className="text-lg font-semibold text-foreground">{problem.title}</h3>
              </div>

              {/* Description */}
              <p className="text-muted-foreground leading-relaxed">{problem.description}</p>

              {/* Hover gradient */}
              <div className="absolute inset-0 rounded-lg bg-gradient-to-br from-destructive/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
            </div>
          ))}
        </div>

      </div>
    </section>
  );
};

export default Problem;
