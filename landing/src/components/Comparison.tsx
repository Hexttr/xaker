import { Check, X, Minus, Scale } from "lucide-react";

const comparisonData = [
  {
    criterion: "Annual Cost",
    pentestRed: "from $6,000",
    traditional: "$100,000+",
    bugBounty: "$50,000+",
    winner: "pentest",
  },
  {
    criterion: "Assessment Frequency",
    pentestRed: "24/7 continuous",
    traditional: "1-2 times/year",
    bugBounty: "Depends on researchers",
    winner: "pentest",
  },
  {
    criterion: "Time to First Report",
    pentestRed: "15 minutes",
    traditional: "2-4 weeks",
    bugBounty: "Unpredictable",
    winner: "pentest",
  },
  {
    criterion: "Coverage Guarantee",
    pentestRed: "AI pentest, OWASP Top 10",
    traditional: "Depends on expert",
    bugBounty: "No guarantees",
    winner: "pentest",
  },
  {
    criterion: "Compliance Reports",
    pentestRed: "Automatic",
    traditional: "Extra charge",
    bugBounty: "No",
    winner: "pentest",
  },
  {
    criterion: "CI/CD Integration",
    pentestRed: "Out of the box",
    traditional: "No",
    bugBounty: "No",
    winner: "pentest",
  },
  {
    criterion: "Scalability",
    pentestRed: "Unlimited",
    traditional: "Linear cost growth",
    bugBounty: "Hard to control",
    winner: "pentest",
  },
];

const Comparison = () => {
  return (
    <section id="comparison" className="py-24 bg-secondary/30 relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-primary/30 to-transparent" />

      <div className="container mx-auto px-6">
        {/* Section Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-md bg-primary/10 border border-primary/20 mb-6">
            <Scale className="h-4 w-4 text-primary" />
            <span className="text-sm font-medium text-primary">Comparison</span>
          </div>
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-6">
            Pentest.red vs{" "}
            <span className="text-gradient">alternatives</span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Objective comparison of security testing approaches
          </p>
        </div>

        {/* Comparison Table */}
        <div className="max-w-5xl mx-auto overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border/50">
                <th className="text-left py-4 px-4 text-muted-foreground font-medium">Criterion</th>
                <th className="text-center py-4 px-4">
                  <div className="inline-flex flex-col items-center gap-1">
                    <span className="text-primary font-bold">Pentest.red</span>
                    <span className="text-xs text-muted-foreground">AI Platform</span>
                  </div>
                </th>
                <th className="text-center py-4 px-4">
                  <div className="inline-flex flex-col items-center gap-1">
                    <span className="text-foreground font-medium">Traditional Pentest</span>
                    <span className="text-xs text-muted-foreground">Manual Audit</span>
                  </div>
                </th>
                <th className="text-center py-4 px-4">
                  <div className="inline-flex flex-col items-center gap-1">
                    <span className="text-foreground font-medium">Bug Bounty</span>
                    <span className="text-xs text-muted-foreground">Crowdsourcing</span>
                  </div>
                </th>
              </tr>
            </thead>
            <tbody>
              {comparisonData.map((row, index) => (
                <tr
                  key={row.criterion}
                  className="border-b border-border/30 hover:bg-card/50 transition-colors"
                >
                  <td className="py-4 px-4 text-foreground font-medium">{row.criterion}</td>
                  <td className="py-4 px-4 text-center">
                    <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-md bg-primary/10 text-primary font-medium">
                      <Check className="h-4 w-4" />
                      {row.pentestRed}
                    </div>
                  </td>
                  <td className="py-4 px-4 text-center text-muted-foreground">
                    {row.traditional}
                  </td>
                  <td className="py-4 px-4 text-center text-muted-foreground">
                    {row.bugBounty}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Bottom CTA */}
        <div className="mt-12 text-center">
          <p className="text-muted-foreground">
            Ready to see the difference?{" "}
            <a href="#" className="text-primary hover:underline font-medium">
              Launch free audit →
            </a>
          </p>
        </div>
      </div>
    </section>
  );
};

export default Comparison;
