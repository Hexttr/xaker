// Компонент для отображения CVSS Score
import { getSeverityLevel, getSeverityColors, getSeverityLabel } from '../utils/severity';

interface CVSSBadgeProps {
  score: number;
  showLabel?: boolean;
  showBar?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

export default function CVSSBadge({ 
  score, 
  showLabel = true, 
  showBar = true,
  size = 'md' 
}: CVSSBadgeProps) {
  const level = getSeverityLevel(score);
  const colors = getSeverityColors(level);
  const label = getSeverityLabel(level);
  const percentage = (score / 10) * 100;

  const sizeClasses = {
    sm: 'text-xs px-2 py-1',
    md: 'text-sm px-3 py-1.5',
    lg: 'text-base px-4 py-2',
  };

  return (
    <div className="flex items-center gap-2">
      {showBar && (
        <div className="flex-1 max-w-[100px]">
          <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
            <div
              className={`h-full transition-all duration-300 ${colors.bg}`}
              style={{ width: `${percentage}%` }}
            />
          </div>
        </div>
      )}
      <div className="flex items-center gap-2">
        <span className={`font-bold ${colors.text}`}>
          {score.toFixed(1)}
        </span>
        {showLabel && (
          <span className={`${sizeClasses[size]} ${colors.bg} text-white rounded-full font-medium`}>
            {label}
          </span>
        )}
      </div>
    </div>
  );
}

