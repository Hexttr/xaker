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
            key={vuln.id || index}
            className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-4 border border-gray-700 shadow-lg hover:shadow-xl transition-all duration-200"
            style={{
              borderLeftColor: colors.border.includes('red') ? '#ef4444' : 
                              colors.border.includes('orange') ? '#f97316' :
                              colors.border.includes('yellow') ? '#eab308' :
                              colors.border.includes('cyan') ? '#06b6d4' : '#6b7280',
              borderLeftWidth: '4px',
            }}
          >
            {/* Header with severity badge */}
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-2">
                <div className={`p-2 ${colors.light} rounded-lg`}>
                  <FiAlertCircle className={`w-4 h-4 ${colors.text}`} />
                </div>
                <div>
                  <span className={`px-2 py-0.5 rounded text-xs font-semibold text-white ${colors.bg}`}>
                    {label}
                  </span>
                </div>
              </div>
            </div>

            {/* Type */}
            <div className="mb-2">
              <span className="text-xs text-gray-400 font-medium">Тип:</span>
              <p className="text-sm font-mono text-green-400 mt-0.5 truncate">{vuln.type}</p>
            </div>

            {/* Title */}
            <div className="mb-3">
              <p className="text-sm text-white font-medium line-clamp-2">{vuln.title}</p>
            </div>

            {/* Location */}
            {vuln.location && (
              <div className="flex items-center gap-1.5 text-xs text-cyan-400 mt-3 pt-3 border-t border-gray-700">
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
