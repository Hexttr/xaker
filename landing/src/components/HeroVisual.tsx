import { Shield, Lock, Eye, Radar, AlertTriangle, CheckCircle } from "lucide-react";

const HeroVisual = () => {
  return (
    <div className="relative w-full aspect-square max-w-lg mx-auto">
      {/* Central Shield */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="relative">
          {/* Outer ring - pulsing */}
          <div className="absolute inset-0 -m-16 rounded-full border border-primary/20 animate-pulse-slow" />
          <div className="absolute inset-0 -m-24 rounded-full border border-primary/10 animate-pulse-slow delay-300" />
          <div className="absolute inset-0 -m-32 rounded-full border border-primary/5 animate-pulse-slow delay-500" />
          
          {/* Main shield container */}
          <div className="h-32 w-32 rounded-2xl bg-gradient-to-br from-primary to-primary/80 flex items-center justify-center shadow-2xl animate-glow">
            <svg viewBox="0 0 32 32" fill="none" className="h-16 w-16 text-primary-foreground">
              <path d="M16 3L5 7.5V14.5C5 21.5 10 27.5 16 29C22 27.5 27 21.5 27 14.5V7.5L16 3Z" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" strokeLinecap="round" />
              <text x="16" y="19" textAnchor="middle" fill="currentColor" fontSize="8" fontWeight="700" fontFamily="system-ui, sans-serif">AI</text>
            </svg>
          </div>
        </div>
      </div>

      {/* Floating security nodes */}
      <div className="absolute top-8 left-8 animate-float">
        <div className="h-14 w-14 rounded-xl bg-card border border-border/50 flex items-center justify-center shadow-lg backdrop-blur-sm">
          <Lock className="h-6 w-6 text-primary" />
        </div>
      </div>

      <div className="absolute top-12 right-12 animate-float delay-200">
        <div className="h-12 w-12 rounded-xl bg-card border border-border/50 flex items-center justify-center shadow-lg backdrop-blur-sm">
          <Eye className="h-5 w-5 text-primary" />
        </div>
      </div>

      <div className="absolute bottom-16 left-12 animate-float delay-300">
        <div className="h-12 w-12 rounded-xl bg-card border border-border/50 flex items-center justify-center shadow-lg backdrop-blur-sm">
          <Radar className="h-5 w-5 text-primary" />
        </div>
      </div>

      <div className="absolute bottom-8 right-8 animate-float delay-100">
        <div className="h-14 w-14 rounded-xl bg-card border border-border/50 flex items-center justify-center shadow-lg backdrop-blur-sm">
          <CheckCircle className="h-6 w-6 text-green-500" />
        </div>
      </div>

      {/* Connecting lines (decorative) */}
      <svg className="absolute inset-0 w-full h-full" viewBox="0 0 400 400">
        <defs>
          <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="hsl(0, 72%, 51%)" stopOpacity="0.3" />
            <stop offset="100%" stopColor="hsl(0, 72%, 51%)" stopOpacity="0" />
          </linearGradient>
        </defs>
        {/* Lines from center to nodes */}
        <line x1="200" y1="200" x2="70" y2="70" stroke="url(#lineGradient)" strokeWidth="1" strokeDasharray="4 4">
          <animate attributeName="stroke-dashoffset" from="0" to="8" dur="1s" repeatCount="indefinite" />
        </line>
        <line x1="200" y1="200" x2="330" y2="85" stroke="url(#lineGradient)" strokeWidth="1" strokeDasharray="4 4">
          <animate attributeName="stroke-dashoffset" from="0" to="8" dur="1.2s" repeatCount="indefinite" />
        </line>
        <line x1="200" y1="200" x2="85" y2="300" stroke="url(#lineGradient)" strokeWidth="1" strokeDasharray="4 4">
          <animate attributeName="stroke-dashoffset" from="0" to="8" dur="0.8s" repeatCount="indefinite" />
        </line>
        <line x1="200" y1="200" x2="330" y2="330" stroke="url(#lineGradient)" strokeWidth="1" strokeDasharray="4 4">
          <animate attributeName="stroke-dashoffset" from="0" to="8" dur="1.4s" repeatCount="indefinite" />
        </line>
      </svg>

      {/* Alert notification - floating */}
      <div className="absolute top-1/3 right-4 animate-fade-in">
        <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-destructive/10 border border-destructive/30 backdrop-blur-sm">
          <AlertTriangle className="h-4 w-4 text-destructive" />
          <span className="text-xs font-medium text-destructive">3 Critical</span>
        </div>
      </div>

      {/* Background glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-primary/20 rounded-full blur-3xl" />
    </div>
  );
};

export default HeroVisual;
