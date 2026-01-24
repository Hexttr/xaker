import { HelpCircle } from "lucide-react";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

const faqs = [
  {
    question: "What compliance standards does Pentest.red support?",
    answer: "We generate reports for SOC 2 Type I/II, ISO 27001, PCI DSS, HIPAA, and GDPR. Reports are automatically generated based on scan results and ready to present to auditors.",
  },
  {
    question: "Where is scanning data stored?",
    answer: "All data is stored in secure Tier III data centers in Europe. We don't store your application source code — only metadata about discovered vulnerabilities.",
  },
  {
    question: "What is the support SLA?",
    answer: "For Enterprise customers, we guarantee response time up to 1 hour for critical incidents, up to 4 hours for high priority. A dedicated 24/7 support line and personal manager are available.",
  },
  {
    question: "Is on-premise deployment available?",
    answer: "Yes, on-premise deployment is available for Enterprise customers in your infrastructure.",
  },
  {
    question: "How is Pentest.red different from Bug Bounty?",
    answer: "Bug Bounty depends on researcher motivation and doesn't guarantee full coverage. Pentest.red is systematic AI-powered pentesting with guaranteed OWASP Top 10 coverage.",
  },
];

const FAQ = () => {
  return (
    <section id="faq" className="py-24 bg-background relative overflow-hidden">
      {/* Background glow */}
      <div className="absolute bottom-0 left-1/4 w-96 h-96 bg-primary/5 rounded-full blur-3xl" />

      <div className="container mx-auto px-6 relative z-10">
        {/* Section Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-md bg-primary/10 border border-primary/20 mb-6">
            <HelpCircle className="h-4 w-4 text-primary" />
            <span className="text-sm font-medium text-primary">FAQ</span>
          </div>
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-6">
            Frequently Asked{" "}
            <span className="text-gradient">Questions</span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Answers to key questions about security, compliance, and integration
          </p>
        </div>

        {/* FAQ Accordion */}
        <div className="max-w-3xl mx-auto">
          <Accordion type="single" collapsible className="space-y-4">
            {faqs.map((faq, index) => (
              <AccordionItem
                key={index}
                value={`item-${index}`}
                className="bg-card rounded-lg border border-border/50 px-6 data-[state=open]:border-primary/30 transition-colors"
              >
                <AccordionTrigger className="text-left text-foreground hover:text-primary hover:no-underline py-6">
                  {faq.question}
                </AccordionTrigger>
                <AccordionContent className="text-muted-foreground pb-6 leading-relaxed">
                  {faq.answer}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </div>

        {/* Still have questions */}
        <div className="mt-12 text-center">
          <p className="text-muted-foreground">
            Still have questions?{" "}
            <a href="mailto:sales@pentest.red" className="text-primary hover:underline">
              Email us
            </a>{" "}
            or{" "}
            <a href="https://t.me/pentestred" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
              contact us on Telegram
            </a>
          </p>
        </div>
      </div>
    </section>
  );
};

export default FAQ;
