import Logo from "./Logo";

const Footer = () => {
  const currentYear = new Date().getFullYear();

  const links = {
    product: [
      { label: "Features", href: "#features" },
      { label: "Pricing", href: "#pricing" },
      { label: "Cases", href: "#cases" },
    ],
    company: [
      { label: "About Us", href: "#solution" },
      { label: "Contact", href: "#" },
    ],
    legal: [
      { label: "Privacy Policy", href: "#" },
      { label: "Terms of Service", href: "#" },
    ],
  };

  return (
    <footer className="bg-card border-t border-border/50">
      <div className="container mx-auto px-6 py-16">
        <div className="grid lg:grid-cols-5 gap-12 mb-12">
          {/* Logo & Description */}
          <div className="lg:col-span-2">
            <a href="#" className="inline-block mb-4">
              <Logo size="md" />
            </a>
            <p className="text-muted-foreground mb-6 leading-relaxed">
              AI-powered continuous security for modern business. 
              Enterprise-level protection at an affordable price.
            </p>
            <div className="flex items-center gap-4">
              <span className="text-sm text-muted-foreground">Compliance:</span>
              <div className="flex gap-2">
                {["ISO 27001", "GDPR", "SOC2"].map((cert) => (
                  <span
                    key={cert}
                    className="px-2 py-1 text-xs rounded bg-secondary text-secondary-foreground"
                  >
                    {cert}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Links */}
          <div>
            <h4 className="font-semibold text-foreground mb-4">Product</h4>
            <ul className="space-y-3">
              {links.product.map((link) => (
                <li key={link.label}>
                  <a href={link.href} className="text-muted-foreground hover:text-foreground transition-colors">
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h4 className="font-semibold text-foreground mb-4">Company</h4>
            <ul className="space-y-3">
              {links.company.map((link) => (
                <li key={link.label}>
                  <a href={link.href} className="text-muted-foreground hover:text-foreground transition-colors">
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h4 className="font-semibold text-foreground mb-4">Legal</h4>
            <ul className="space-y-3">
              {links.legal.map((link) => (
                <li key={link.label}>
                  <a href={link.href} className="text-muted-foreground hover:text-foreground transition-colors">
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-8 border-t border-border/50 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-sm text-muted-foreground">
            © {currentYear} Pentest.red. All rights reserved.
          </p>
          <p className="text-sm text-muted-foreground">
            Made with ❤️ for a secure internet
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
