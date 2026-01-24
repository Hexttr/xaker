import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { ArrowRight, X } from "lucide-react";
import RequestDemoModal from "./RequestDemoModal";

const StickyCTA = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [isDismissed, setIsDismissed] = useState(false);
  const [isDemoModalOpen, setIsDemoModalOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      // Show after scrolling past 600px (approximately past Hero section)
      const shouldShow = window.scrollY > 600;
      setIsVisible(shouldShow && !isDismissed);
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, [isDismissed]);

  if (!isVisible) return null;

  return (
    <div className="fixed bottom-6 right-6 z-50 animate-fade-up">
      <div className="relative">
        <button
          onClick={() => setIsDismissed(true)}
          className="absolute -top-2 -right-2 h-6 w-6 rounded-md bg-secondary border border-border flex items-center justify-center hover:bg-muted transition-colors"
          aria-label="Close"
        >
          <X className="h-3 w-3 text-muted-foreground" />
        </button>
        <Button variant="hero" size="lg" className="shadow-xl group" onClick={() => setIsDemoModalOpen(true)}>
          Request Demo
          <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
        </Button>
      </div>
      <RequestDemoModal isOpen={isDemoModalOpen} onClose={() => setIsDemoModalOpen(false)} />
    </div>
  );
};

export default StickyCTA;
