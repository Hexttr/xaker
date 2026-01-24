import { createContext, useContext, useState, ReactNode } from 'react';
import RequestDemoModal from '@/components/RequestDemoModal';

interface RequestDemoContextType {
  openModal: () => void;
  closeModal: () => void;
}

const RequestDemoContext = createContext<RequestDemoContextType | undefined>(undefined);

export const useRequestDemo = () => {
  const context = useContext(RequestDemoContext);
  if (!context) {
    throw new Error('useRequestDemo must be used within RequestDemoProvider');
  }
  return context;
};

interface RequestDemoProviderProps {
  children: ReactNode;
}

export const RequestDemoProvider = ({ children }: RequestDemoProviderProps) => {
  const [isOpen, setIsOpen] = useState(false);

  const openModal = () => setIsOpen(true);
  const closeModal = () => setIsOpen(false);

  return (
    <RequestDemoContext.Provider value={{ openModal, closeModal }}>
      {children}
      <RequestDemoModal isOpen={isOpen} onClose={closeModal} />
    </RequestDemoContext.Provider>
  );
};

