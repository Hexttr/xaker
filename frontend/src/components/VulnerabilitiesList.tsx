// Компонент для отображения найденных уязвимостей
import { Vulnerability } from '../services/api';
import { getSeverityColors, getSeverityLabel } from '../utils/severity';

interface VulnerabilitiesListProps {
  vulnerabilities: Vulnerability[];
}

export default function VulnerabilitiesList({ vulnerabilities }: VulnerabilitiesListProps) {
  if (vulnerabilities.length === 0) {
    return null;
  }

  return (
    <div className="mt-3 pt-3 border-t border-gray-700">
      <h4 className="text-sm font-medium mb-2 text-red-400 font-mono">
        🔴 Найденные уязвимости ({vulnerabilities.length})
      </h4>
      <div className="space-y-2">
        {vulnerabilities.map((vuln, index) => {
          const colors = getSeverityColors(vuln.severity);
          const label = getSeverityLabel(vuln.severity);
          
          return (
            <div
              key={index}
              className={`p-2 rounded border-l-2 bg-gray-800 ${colors.border}`}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1">
                  <div className="flex items-center gap-1.5 mb-1">
                    <span className={`px-1.5 py-0.5 rounded text-xs font-normal text-white ${colors.bg}`}>
                      {label}
                    </span>
                    <span className="font-medium text-green-400 font-mono text-xs">{vuln.type}</span>
                  </div>
                  <p className="text-xs text-gray-400 font-mono">{vuln.title}</p>
                  {vuln.location && (
                    <p className="text-xs text-cyan-500 mt-0.5 font-mono">
                      📍 {vuln.location}
                    </p>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}


