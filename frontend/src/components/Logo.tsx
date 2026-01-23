interface LogoProps {
  size?: "sm" | "md" | "lg";
  showText?: boolean;
  className?: string;
}

const Logo = ({ size = "md", showText = true, className = "" }: LogoProps) => {
  console.log('Logo component rendering:', { size, showText });
  
  const sizes = {
    sm: { icon: "h-6 w-6", text: "text-lg" },
    md: { icon: "h-8 w-8", text: "text-xl" },
    lg: { icon: "h-10 w-10", text: "text-2xl" },
  };

  return (
    <div className={`flex items-center gap-3 ${className}`}>
      {/* Shield with AI */}
      <div className="relative flex-shrink-0">
        <svg
          viewBox="0 0 32 32"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className={`${sizes[size].icon} text-red-600`}
          style={{ display: 'block', width: '100%', height: '100%' }}
          data-testid="logo-svg"
        >
          {/* Sharp Shield Shape */}
          <path
            d="M16 2L4 7V15C4 22.5 9.5 29 16 30C22.5 29 28 22.5 28 15V7L16 2Z"
            fill="currentColor"
            fillOpacity="0.15"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinejoin="miter"
          />
          {/* AI Text */}
          <text
            x="16"
            y="19"
            textAnchor="middle"
            fill="currentColor"
            fontSize="10"
            fontWeight="700"
            fontFamily="system-ui, sans-serif"
            letterSpacing="-0.5"
          >
            AI
          </text>
        </svg>
      </div>
      
      {showText && (
        <div className="flex flex-col">
          <span className={`${sizes[size].text} font-bold text-white`}>
            Pentest<span className="text-red-600">.red</span>
          </span>
          <span className="text-gray-400 text-xs">ENTERPRISE</span>
        </div>
      )}
    </div>
  );
};

export default Logo;

