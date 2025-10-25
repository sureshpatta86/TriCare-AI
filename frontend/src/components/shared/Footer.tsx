/**
 * Footer Component
 * 
 * Application footer with important links and disclaimer
 */

import Link from 'next/link';
import { Heart, Github, Mail } from 'lucide-react';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* About */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-4">About TriCare AI</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
              An educational medical triage and information platform powered by AI.
              Not a diagnostic tool. Always consult healthcare professionals.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-4">Quick Links</h3>
            <ul className="space-y-2">
              <li>
                <Link href="/reports" className="text-sm text-gray-600 dark:text-gray-400 hover:text-medical-600 dark:hover:text-medical-400 transition-colors">
                  Report Simplifier
                </Link>
              </li>
              <li>
                <Link href="/symptoms" className="text-sm text-gray-600 dark:text-gray-400 hover:text-medical-600 dark:hover:text-medical-400 transition-colors">
                  Symptom Router
                </Link>
              </li>
              <li>
                <Link href="/imaging" className="text-sm text-gray-600 dark:text-gray-400 hover:text-medical-600 dark:hover:text-medical-400 transition-colors">
                  Imaging Pre-Screen
                </Link>
              </li>
            </ul>
          </div>

          {/* Contact & Legal */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-4">Information</h3>
            <ul className="space-y-2">
              <li className="text-sm text-gray-600 dark:text-gray-400">
                <span className="font-medium">Emergency?</span> Call 911
              </li>
              <li className="text-sm text-gray-600 dark:text-gray-400">
                Educational tool only
              </li>
              <li className="text-sm text-gray-600 dark:text-gray-400">
                Not FDA approved
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="mt-8 pt-8 border-t border-gray-200 dark:border-gray-700">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              © {currentYear} TriCare AI. Built with <Heart className="inline h-4 w-4 text-urgent-500" /> for UHG Hackathon 2025
            </p>
            
            <div className="flex items-center space-x-4">
              <Github className="h-5 w-5 text-gray-600 dark:text-gray-400" />
              <Mail className="h-5 w-5 text-gray-600 dark:text-gray-400" />
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
