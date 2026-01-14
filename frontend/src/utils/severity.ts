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
        bg: 'bg-red-500',
        text: 'text-red-700',
        border: 'border-red-300',
        light: 'bg-red-50',
      };
    case 'high':
      return {
        bg: 'bg-orange-500',
        text: 'text-orange-700',
        border: 'border-orange-300',
        light: 'bg-orange-50',
      };
    case 'medium':
      return {
        bg: 'bg-yellow-500',
        text: 'text-yellow-700',
        border: 'border-yellow-300',
        light: 'bg-yellow-50',
      };
    case 'low':
      return {
        bg: 'bg-blue-500',
        text: 'text-blue-700',
        border: 'border-blue-300',
        light: 'bg-blue-50',
      };
    default:
      return {
        bg: 'bg-gray-500',
        text: 'text-gray-700',
        border: 'border-gray-300',
        light: 'bg-gray-50',
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

