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
    <div className="mt-4 pt-4 border-t border-gray-700">
      <h4 className="text-lg font-semibold mb-3 text-red-400 font-mono">
        🔴 Найденные уязвимости ({vulnerabilities.length})
      </h4>
      <div className="space-y-3">
        {vulnerabilities.map((vuln, index) => {
          const colors = getSeverityColors(vuln.severity);
          const label = getSeverityLabel(vuln.severity);
          
          return (
            <div
              key={index}
              className={`p-3 rounded-lg border-l-4 bg-gray-800 ${colors.border}`}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`px-2 py-1 rounded text-xs font-medium text-white ${colors.bg}`}>
                      {label}
                    </span>
                    <span className="font-semibold text-green-400 font-mono">{vuln.type}</span>
                  </div>
                  <p className="text-sm text-gray-300 font-mono">{vuln.title}</p>
                  {vuln.location && (
                    <p className="text-xs text-cyan-400 mt-1 font-mono">
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


