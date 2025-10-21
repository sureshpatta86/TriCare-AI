'use client';

import { useEffect, useState } from 'react';
import { Moon, Sun } from 'lucide-react';
import { useTheme } from '@/contexts/ThemeContext';

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Don't render until mounted to avoid hydration mismatch
  if (!mounted) {
    return (
      <div className="fixed top-4 right-4 z-[100] p-3 rounded-full bg-white shadow-lg border border-gray-200 w-[44px] h-[44px]" />
    );
  }

  return (
    <button
      onClick={toggleTheme}
      className="fixed top-20 right-6 z-[100] p-4 rounded-full bg-gradient-to-br from-medical-500 to-medical-600 dark:from-yellow-500 dark:to-yellow-600 shadow-2xl border-2 border-white dark:border-gray-900 hover:scale-110 hover:shadow-medical-lg transition-all duration-200 focus:outline-none focus:ring-4 focus:ring-medical-300 dark:focus:ring-yellow-300"
      aria-label="Toggle theme"
      title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
    >
      {theme === 'light' ? (
        <Moon className="w-6 h-6 text-white" />
      ) : (
        <Sun className="w-6 h-6 text-white" />
      )}
    </button>
  );
}
