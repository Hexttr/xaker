import { Github, GitBranch, Cloud, Server, Workflow, Container } from "lucide-react";

const integrations = [
  { name: "GitHub", icon: Github },
  { name: "GitLab", icon: GitBranch },
  { name: "AWS", icon: Cloud },
  { name: "Azure", icon: Server },
  { name: "Jira", icon: Workflow },
  { name: "Jenkins", icon: Container },
];

const TrustedBy = () => {
  return (
    <section className="py-12 border-y border-border/30 bg-secondary/20 overflow-hidden">
      <div className="container mx-auto px-6">
        <p className="text-center text-sm text-muted-foreground mb-8">
          Integrates with your tech stack
        </p>
        
        {/* Infinite scroll container */}
        <div className="relative">
          {/* Gradient masks */}
          <div className="absolute left-0 top-0 bottom-0 w-20 bg-gradient-to-r from-background to-transparent z-10" />
          <div className="absolute right-0 top-0 bottom-0 w-20 bg-gradient-to-l from-background to-transparent z-10" />
          
          {/* Scrolling content */}
          <div className="flex animate-scroll">
            {/* First set */}
            <div className="flex gap-12 items-center shrink-0 px-6">
              {integrations.map((integration) => (
                <div
                  key={integration.name}
                  className="flex items-center gap-3 px-6 py-3 rounded-lg bg-card/50 border border-border/30 hover:border-primary/30 transition-colors group"
                >
                  <integration.icon className="h-6 w-6 text-muted-foreground group-hover:text-primary transition-colors" />
                  <span className="text-foreground font-medium whitespace-nowrap">{integration.name}</span>
                </div>
              ))}
            </div>
            {/* Duplicate for seamless loop */}
            <div className="flex gap-12 items-center shrink-0 px-6">
              {integrations.map((integration) => (
                <div
                  key={`${integration.name}-2`}
                  className="flex items-center gap-3 px-6 py-3 rounded-lg bg-card/50 border border-border/30 hover:border-primary/30 transition-colors group"
                >
                  <integration.icon className="h-6 w-6 text-muted-foreground group-hover:text-primary transition-colors" />
                  <span className="text-foreground font-medium whitespace-nowrap">{integration.name}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default TrustedBy;
