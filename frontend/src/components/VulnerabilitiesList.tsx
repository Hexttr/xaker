// Компонент для отображения найденных уязвимостей в виде карточек
import { Vulnerability } from '../services/api';
import { getSeverityColors, getSeverityLabel } from '../utils/severity';
import { FiAlertCircle, FiMapPin } from 'react-icons/fi';

interface VulnerabilitiesListProps {
  vulnerabilities: Vulnerability[];
}

export default function VulnerabilitiesList({ vulnerabilities }: VulnerabilitiesListProps) {
  if (vulnerabilities.length === 0) {
    return (
      <div className="text-center py-8">
        <FiAlertCircle className="w-12 h-12 text-gray-600 mx-auto mb-2" />
        <p className="text-sm text-gray-500">Уязвимости не найдены</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {vulnerabilities.map((vuln, index) => {
        const colors = getSeverityColors(vuln.severity);
        const label = getSeverityLabel(vuln.severity);
        
        return (
          <div
            key={`${vuln.type}-${vuln.title}-${index}`}
            className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-lg p-3 border border-gray-700 shadow-lg hover:shadow-xl transition-all duration-200"
            style={{
              borderLeftColor: colors.border.includes('red') ? '#ef4444' : 
                              colors.border.includes('orange') ? '#f97316' :
                              colors.border.includes('yellow') ? '#eab308' :
                              colors.border.includes('cyan') ? '#06b6d4' : '#6b7280',
              borderLeftWidth: '4px',
            }}
          >
            {/* Header: Severity badge and Type in one line */}
            <div className="flex items-center justify-between gap-2 mb-1.5">
              <div className="flex items-center gap-1.5">
                <div className={`p-1 ${colors.light} rounded`}>
                  <FiAlertCircle className={`w-3 h-3 ${colors.text}`} />
                </div>
                <span className={`px-1.5 py-0.5 rounded text-xs font-semibold text-white ${colors.bg}`}>
                  {label}
                </span>
              </div>
              <span className="text-xs font-mono text-green-400 truncate">{vuln.type}</span>
            </div>

            {/* Title */}
            <p className="text-sm text-white font-medium line-clamp-2 mb-1.5">{vuln.title}</p>

            {/* Location */}
            {vuln.location && (
              <div className="flex items-center gap-1 text-xs text-cyan-400 pt-1.5 border-t border-gray-700">
                <FiMapPin className="w-3 h-3 flex-shrink-0" />
                <span className="font-mono truncate">{vuln.location}</span>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
