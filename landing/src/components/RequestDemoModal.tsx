import { useState } from 'react';
import { X } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface RequestDemoModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const RequestDemoModal = ({ isOpen, onClose }: RequestDemoModalProps) => {
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle');

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitStatus('idle');

    try {
      const response = await fetch('/api/demo-requests', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, phone }),
      });

      if (response.ok) {
        setSubmitStatus('success');
        setName('');
        setPhone('');
        setTimeout(() => {
          onClose();
          setSubmitStatus('idle');
        }, 2000);
      } else {
        setSubmitStatus('error');
      }
    } catch (error) {
      console.error('Error submitting form:', error);
      setSubmitStatus('error');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className='fixed inset-0 z-50 flex items-center justify-center p-4'>
      <div
        className='absolute inset-0 bg-black/60 backdrop-blur-sm'
        onClick={onClose}
      />
      
      <div className='relative bg-card border border-border rounded-lg shadow-xl w-full max-w-md animate-fade-in'>
        <button
          onClick={onClose}
          className='absolute top-4 right-4 p-2 rounded-md hover:bg-secondary transition-colors'
          aria-label='Close'
        >
          <X className='h-5 w-5 text-muted-foreground' />
        </button>

        <div className='p-6'>
          <h2 className='text-2xl font-bold text-foreground mb-2'>
            Request Demo
          </h2>
          <p className='text-muted-foreground mb-6'>
            Fill out the form and we will contact you shortly.
          </p>

          {submitStatus === 'success' ? (
            <div className='text-center py-8'>
              <div className='text-green-500 text-4xl mb-4'>✓</div>
              <p className='text-foreground font-medium'>
                Thank you! We will contact you shortly.
              </p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className='space-y-4'>
              <div>
                <label
                  htmlFor='name'
                  className='block text-sm font-medium text-foreground mb-2'
                >
                  Name *
                </label>
                <input
                  id='name'
                  name='name'
                  type='text'
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  className='w-full px-4 py-2.5 rounded-md bg-background border border-border text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all'
                  placeholder='Enter your name'
                  disabled={isSubmitting}
                />
              </div>

              <div>
                <label
                  htmlFor='phone'
                  className='block text-sm font-medium text-foreground mb-2'
                >
                  Phone *
                </label>
                <input
                  id='phone'
                  name='phone'
                  type='tel'
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  required
                  className='w-full px-4 py-2.5 rounded-md bg-background border border-border text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all'
                  placeholder='+7 (999) 123-45-67'
                  disabled={isSubmitting}
                />
              </div>

              {submitStatus === 'error' && (
                <div className='text-sm text-destructive bg-destructive/10 p-3 rounded-md'>
                  An error occurred. Please try again.
                </div>
              )}

              <Button
                type='submit'
                variant='hero'
                size='lg'
                className='w-full'
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Submitting...' : 'Submit'}
              </Button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default RequestDemoModal;

