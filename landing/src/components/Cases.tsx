import { Quote, Building2, ShoppingCart, Heart } from "lucide-react";

const cases = [
  {
    icon: Building2,
    industry: "Fintech",
    company: "Payment System",
    quote: "In the first week, Pentest.red discovered 47 critical vulnerabilities in our mobile app. We fixed them before release and avoided a potential data breach affecting 100,000 customers.",
    author: "Marcus Chen",
    role: "CTO",
    avatar: "MC",
    result: "47 critical",
    resultLabel: "vulnerabilities found",
    savings: "$194K",
    savingsLabel: "damage prevented",
  },
  {
    icon: ShoppingCart,
    industry: "E-commerce",
    company: "Marketplace",
    quote: "We used to spend $200,000 a year on manual pentests and still missed vulnerabilities between assessments. Now we have continuous protection and full coverage.",
    author: "Sarah Mitchell",
    role: "CISO",
    avatar: "SM",
    result: "24/7",
    resultLabel: "continuous monitoring",
    savings: "12x",
    savingsLabel: "more checks/year",
  },
  {
    icon: Heart,
    industry: "Healthcare",
    company: "Telemedicine",
    quote: "Pentest.red's automatic compliance reports helped us pass SOC2 Type II on the first attempt. Savings — 3 months of preparation and $80,000 on consultants.",
    author: "David Nakamura",
    role: "CEO",
    avatar: "DN",
    result: "SOC2 Type II",
    resultLabel: "first attempt",
    savings: "3 mo",
    savingsLabel: "faster to compliance",
  },
];

const Cases = () => {
  return (
    <section id="cases" className="py-24 bg-background relative overflow-hidden">
      {/* Background glow */}
      <div className="absolute top-1/2 right-0 w-96 h-96 bg-primary/5 rounded-full blur-3xl" />

      <div className="container mx-auto px-6 relative z-10">
        {/* Section Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-md bg-primary/10 border border-primary/20 mb-6">
            <Quote className="h-4 w-4 text-primary" />
            <span className="text-sm font-medium text-primary">Case Studies</span>
          </div>
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-6">
            Customer{" "}
            <span className="text-gradient">success stories</span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            How enterprise companies protect their infrastructure with Pentest.red
          </p>
        </div>

        {/* Cases Grid */}
        <div className="grid lg:grid-cols-3 gap-8">
          {cases.map((caseItem, index) => (
            <div
              key={caseItem.company}
              className="group relative bg-card rounded-lg p-8 border border-border/50 hover:border-primary/30 transition-all duration-300 hover:shadow-xl flex flex-col"
            >
              {/* Industry Badge */}
              <div className="flex items-center gap-3 mb-6">
                <div className="h-12 w-12 rounded-md bg-primary/10 flex items-center justify-center">
                  <caseItem.icon className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <p className="text-sm font-medium text-primary">{caseItem.industry}</p>
                  <p className="text-sm text-muted-foreground">{caseItem.company}</p>
                </div>
              </div>

              {/* Quote */}
              <blockquote className="text-foreground mb-6 flex-grow leading-relaxed">
                <Quote className="h-8 w-8 text-primary/20 mb-2" />
                "{caseItem.quote}"
              </blockquote>

              {/* Author */}
              <div className="flex items-center gap-3 mb-6">
                <div className="h-10 w-10 rounded-md bg-primary/10 flex items-center justify-center text-sm font-semibold text-primary">
                  {caseItem.avatar}
                </div>
                <div>
                  <p className="font-medium text-foreground">{caseItem.author}</p>
                  <p className="text-sm text-muted-foreground">{caseItem.role}, {caseItem.company}</p>
                </div>
              </div>

              {/* Results */}
              <div className="grid grid-cols-2 gap-4 pt-6 border-t border-border/50">
                <div>
                  <p className="text-lg font-bold text-foreground">{caseItem.result}</p>
                  <p className="text-xs text-muted-foreground">{caseItem.resultLabel}</p>
                </div>
                <div>
                  <p className="text-lg font-bold text-primary">{caseItem.savings}</p>
                  <p className="text-xs text-muted-foreground">{caseItem.savingsLabel}</p>
                </div>
              </div>

              {/* Hover gradient */}
              <div className="absolute inset-0 rounded-lg bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
            </div>
          ))}
        </div>

        {/* Stats Summary */}
        <div className="mt-16 p-8 rounded-lg bg-card border border-border/50">
          <div className="grid md:grid-cols-4 gap-8 text-center">
            {[
              { value: "50,000+", label: "Vulnerabilities discovered" },
              { value: "10+", label: "Pilot customers" },
              { value: "$2M+", label: "Saved by clients" },
              { value: "100%", label: "Passed compliance" },
            ].map((stat) => (
              <div key={stat.label}>
                <p className="text-3xl md:text-4xl font-bold text-gradient mb-2">{stat.value}</p>
                <p className="text-sm text-muted-foreground">{stat.label}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default Cases;
