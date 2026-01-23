import { Brain, Cpu, Database, Network, Workflow, Zap } from "lucide-react";

const AIVisual = () => {
  return (
    <div className="relative w-full aspect-square max-w-md mx-auto">
      {/* Central Brain */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="relative">
          {/* Rotating rings */}
          <div className="absolute inset-0 -m-12 rounded-full border-2 border-dashed border-primary/30 animate-spin" style={{ animationDuration: '20s' }} />
          <div className="absolute inset-0 -m-20 rounded-full border border-primary/20 animate-spin" style={{ animationDuration: '30s', animationDirection: 'reverse' }} />
          
          {/* Core */}
          <div className="h-24 w-24 rounded-full bg-gradient-to-br from-primary to-primary/70 flex items-center justify-center shadow-2xl">
            <Brain className="h-12 w-12 text-primary-foreground" />
          </div>
          
          {/* Pulse effect */}
          <div className="absolute inset-0 rounded-full bg-primary/30 animate-ping" style={{ animationDuration: '2s' }} />
        </div>
      </div>

      {/* Orbiting nodes */}
      <div className="absolute inset-0">
        {/* Node 1 - Top */}
        <div className="absolute top-4 left-1/2 -translate-x-1/2 animate-float">
          <div className="h-12 w-12 rounded-xl bg-card border border-primary/30 flex items-center justify-center shadow-lg">
            <Cpu className="h-5 w-5 text-primary" />
          </div>
        </div>

        {/* Node 2 - Right */}
        <div className="absolute right-4 top-1/2 -translate-y-1/2 animate-float delay-200">
          <div className="h-12 w-12 rounded-xl bg-card border border-primary/30 flex items-center justify-center shadow-lg">
            <Database className="h-5 w-5 text-primary" />
          </div>
        </div>

        {/* Node 3 - Bottom */}
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 animate-float delay-300">
          <div className="h-12 w-12 rounded-xl bg-card border border-primary/30 flex items-center justify-center shadow-lg">
            <Network className="h-5 w-5 text-primary" />
          </div>
        </div>

        {/* Node 4 - Left */}
        <div className="absolute left-4 top-1/2 -translate-y-1/2 animate-float delay-100">
          <div className="h-12 w-12 rounded-xl bg-card border border-primary/30 flex items-center justify-center shadow-lg">
            <Workflow className="h-5 w-5 text-primary" />
          </div>
        </div>
      </div>

      {/* Data flow particles */}
      <svg className="absolute inset-0 w-full h-full" viewBox="0 0 300 300">
        <defs>
          <linearGradient id="particleGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="hsl(0, 72%, 51%)" stopOpacity="0" />
            <stop offset="50%" stopColor="hsl(0, 72%, 51%)" stopOpacity="1" />
            <stop offset="100%" stopColor="hsl(0, 72%, 51%)" stopOpacity="0" />
          </linearGradient>
        </defs>
        
        {/* Animated data streams */}
        <circle r="3" fill="hsl(0, 72%, 51%)">
          <animateMotion dur="3s" repeatCount="indefinite" path="M150,30 Q200,150 150,270 Q100,150 150,30" />
        </circle>
        <circle r="2" fill="hsl(0, 72%, 51%)" opacity="0.7">
          <animateMotion dur="2.5s" repeatCount="indefinite" path="M270,150 Q150,100 30,150 Q150,200 270,150" />
        </circle>
        <circle r="2" fill="hsl(0, 72%, 51%)" opacity="0.5">
          <animateMotion dur="4s" repeatCount="indefinite" path="M50,50 Q150,150 250,250" />
        </circle>
      </svg>

      {/* Stats card */}
      <div className="absolute -bottom-4 -right-4 px-4 py-3 rounded-xl bg-card border border-border/50 shadow-xl backdrop-blur-sm">
        <div className="flex items-center gap-2">
          <Zap className="h-4 w-4 text-primary" />
          <span className="text-sm font-semibold text-foreground">ML Model v3.2</span>
        </div>
        <p className="text-xs text-muted-foreground mt-1">1000+ правил • 95% точность</p>
      </div>

      {/* Background glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-48 h-48 bg-primary/15 rounded-full blur-3xl" />
    </div>
  );
};

export default AIVisual;
