// Утилиты для работы с критичностью уязвимостей

export type SeverityLevel = 'critical' | 'high' | 'medium' | 'low' | 'info';

export interface SeverityColors {
  bg: string;
  text: string;
  border: string;
  light: string;
}

export const getSeverityLevel = (cvss: number): SeverityLevel => {
  if (cvss >= 9.0) return 'critical';
  if (cvss >= 7.0) return 'high';
  if (cvss >= 4.0) return 'medium';
  if (cvss > 0) return 'low';
  return 'info';
};

export const getSeverityColors = (severity: SeverityLevel): SeverityColors => {
  switch (severity) {
    case 'critical':
      return {
        bg: 'bg-red-600',
        text: 'text-red-400',
        border: 'border-red-500',
        light: 'bg-red-900/30',
      };
    case 'high':
      return {
        bg: 'bg-orange-600',
        text: 'text-orange-400',
        border: 'border-orange-500',
        light: 'bg-orange-900/30',
      };
    case 'medium':
      return {
        bg: 'bg-yellow-600',
        text: 'text-yellow-400',
        border: 'border-yellow-500',
        light: 'bg-yellow-900/30',
      };
    case 'low':
      return {
        bg: 'bg-cyan-600',
        text: 'text-cyan-400',
        border: 'border-cyan-500',
        light: 'bg-cyan-900/30',
      };
    default:
      return {
        bg: 'bg-gray-600',
        text: 'text-gray-400',
        border: 'border-gray-500',
        light: 'bg-gray-800',
      };
  }
};

export const getSeverityLabel = (severity: SeverityLevel): string => {
  switch (severity) {
    case 'critical':
      return 'Критический';
    case 'high':
      return 'Высокий';
    case 'medium':
      return 'Средний';
    case 'low':
      return 'Низкий';
    default:
      return 'Информационный';
  }
};

export const getCVSSColor = (cvss: number): string => {
  const level = getSeverityLevel(cvss);
  const colors = getSeverityColors(level);
  return colors.bg;
};


