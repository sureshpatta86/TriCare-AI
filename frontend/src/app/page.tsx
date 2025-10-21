import Link from 'next/link';
import { FileText, Stethoscope, Image as ImageIcon, ArrowRight, Shield, Zap, Users, MapPin } from 'lucide-react';
import DisclaimerBanner from '@/components/shared/DisclaimerBanner';

export default function HomePage() {
  const features = [
    {
      icon: FileText,
      title: 'Medical Report Simplifier',
      description: 'Upload medical reports and get plain-language explanations.',
      href: '/reports',
      color: 'from-blue-500 to-cyan-500',
    },
    {
      icon: Stethoscope,
      title: 'Symptom Router',
      description: 'Get guidance on which healthcare provider to consult.',
      href: '/symptoms',
      color: 'from-purple-500 to-pink-500',
    },
    {
      icon: ImageIcon,
      title: 'X-ray Pre-Screen',
      description: 'AI-powered preliminary analysis of medical imaging.',
      href: '/imaging',
      color: 'from-green-500 to-emerald-500',
    },
    {
      icon: MapPin,
      title: 'Find Nearby Doctors',
      description: 'Search for recommended doctors based on your location.',
      href: '/doctors',
      color: 'from-orange-500 to-red-500',
    },
  ];

  const benefits = [
    { icon: Zap, title: 'Fast & Accurate', description: 'Powered by GPT-5 and advanced AI models.' },
    { icon: Shield, title: 'Educational Focus', description: 'Designed to help you understand medical information.' },
    { icon: Users, title: 'Patient-Friendly', description: 'Medical jargon translated into clear language.' },
  ];

  return (
    <div className="min-h-screen bg-white dark:bg-gray-900">
      <section className="py-20 bg-gradient-to-br from-medical-50 via-white to-health-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-medical-600 to-medical-800 dark:from-medical-400 dark:to-medical-600 bg-clip-text text-transparent">
              Understand Your Health Better
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-300 mb-8">
              TriCare AI helps you navigate complex medical information with confidence.
            </p>
            <div className="max-w-2xl mx-auto mb-12">
              <DisclaimerBanner type="general" />
            </div>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/reports" className="inline-flex items-center justify-center px-8 py-4 bg-medical-600 dark:bg-medical-500 text-white rounded-lg font-semibold hover:bg-medical-700 dark:hover:bg-medical-600 transition-colors">
                Get Started <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
              <Link href="#features" className="inline-flex items-center justify-center px-8 py-4 bg-white dark:bg-gray-800 text-medical-600 dark:text-medical-400 rounded-lg font-semibold border-2 border-medical-600 dark:border-medical-500 hover:bg-medical-50 dark:hover:bg-gray-700 transition-colors">
                Learn More
              </Link>
            </div>
          </div>
        </div>
      </section>

      <section id="features" className="py-20 bg-white dark:bg-gray-900">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4 text-gray-900 dark:text-white">Four Powerful Features</h2>
            <p className="text-lg text-gray-600 dark:text-gray-400">Choose the tool that fits your needs</p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-7xl mx-auto">
            {features.map((feature) => {
              const Icon = feature.icon;
              return (
                <Link key={feature.href} href={feature.href} className="group relative overflow-hidden rounded-2xl bg-white dark:bg-gray-800 p-8 shadow-xl hover:shadow-2xl transition-all border border-gray-100 dark:border-gray-700">
                  <div className={`absolute inset-0 bg-gradient-to-br ${feature.color} opacity-0 group-hover:opacity-10 transition-opacity`} />
                  <div className={`inline-flex p-3 rounded-lg bg-gradient-to-br ${feature.color} mb-4`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-xl font-bold mb-3 text-gray-900 dark:text-white">{feature.title}</h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">{feature.description}</p>
                  <div className="flex items-center text-medical-600 dark:text-medical-400 font-semibold">
                    Learn more <ArrowRight className="ml-2 h-4 w-4" />
                  </div>
                </Link>
              );
            })}
          </div>
        </div>
      </section>

      <section className="py-20 bg-gray-50 dark:bg-gray-800">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12 text-gray-900 dark:text-white">Why Choose TriCare AI?</h2>
          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            {benefits.map((benefit) => {
              const Icon = benefit.icon;
              return (
                <div key={benefit.title} className="text-center">
                  <div className="inline-flex p-4 rounded-full bg-medical-100 dark:bg-medical-900/30 mb-4">
                    <Icon className="w-8 h-8 text-medical-600 dark:text-medical-400" />
                  </div>
                  <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">{benefit.title}</h3>
                  <p className="text-gray-600 dark:text-gray-400">{benefit.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      <section className="py-20 bg-gradient-to-br from-medical-600 to-medical-800 dark:from-medical-700 dark:to-medical-900">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto text-center text-white">
            <h2 className="text-4xl font-bold mb-6">Ready to Understand Your Health Better?</h2>
            <p className="text-xl mb-8 text-medical-100 dark:text-medical-200">Start using our AI-powered tools today.</p>
            <Link href="/reports" className="inline-flex items-center justify-center px-8 py-4 bg-white text-medical-600 dark:bg-gray-100 dark:text-medical-700 rounded-lg font-semibold hover:bg-gray-100 dark:hover:bg-white transition-colors">
              Get Started Now <ArrowRight className="ml-2 h-5 w-5" />
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
