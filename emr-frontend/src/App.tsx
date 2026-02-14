import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';
import './App.css';
import { CernerTestPage } from './pages/cerner/TestPage';
import { EpicTestPage } from './pages/epic/EpicTestPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  const [activeView, setActiveView] = useState<'home' | 'cerner' | 'epic'>('home');

  return (
    <QueryClientProvider client={queryClient}>
      {activeView === 'cerner' ? (
        <CernerTestPage />
      ) : activeView === 'epic' ? (
        <EpicTestPage />
      ) : (
        <div className="min-h-screen bg-gray-100">
          <header className="bg-white shadow-sm p-4">
            <div className="max-w-7xl mx-auto flex justify-between items-center">
              <h1 className="text-2xl font-bold text-gray-900">
                EMR Practice System
              </h1>
              <div className="flex gap-3">
                <button
                  onClick={() => setActiveView('cerner')}
                  className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-all shadow-md"
                >
                  Cerner Demo
                </button>
                <button
                  onClick={() => setActiveView('epic')}
                  className="px-6 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 transition-all shadow-md"
                >
                  Epic Demo
                </button>
              </div>
            </div>
          </header>
          <main className="max-w-7xl mx-auto p-8">
            <div className="grid grid-cols-2 gap-6">
              {/* Cerner Card */}
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold mb-4 text-blue-900">
                  ✅ Cerner PowerChart
                </h2>
                <p className="text-gray-600 mb-4 text-sm">
                  TASK 1.2 Complete - Dark theme with blue accents
                </p>

                <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded">
                  <h3 className="font-semibold text-blue-800 mb-2 text-sm">Components</h3>
                  <ul className="text-xs text-blue-700 space-y-1">
                    <li>• CernerSidebar - Navigation + timer</li>
                    <li>• PatientBanner - Demographics</li>
                    <li>• SOAPNoteEditor - Full SOAP form</li>
                  </ul>
                </div>

                <div className="mt-4 text-center">
                  <button
                    onClick={() => setActiveView('cerner')}
                    className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all shadow-md font-semibold"
                  >
                    Launch Cerner Demo →
                  </button>
                </div>
              </div>

              {/* Epic Card */}
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold mb-4 text-purple-900">
                  ✅ Epic EHR
                </h2>
                <p className="text-gray-600 mb-4 text-sm">
                  TASK 1.3 Complete - Light theme with purple accents
                </p>

                <div className="mt-4 p-4 bg-purple-50 border border-purple-200 rounded">
                  <h3 className="font-semibold text-purple-800 mb-2 text-sm">Components</h3>
                  <ul className="text-xs text-purple-700 space-y-1">
                    <li>• EpicSidebar - Collapsible nav</li>
                    <li>• EpicPatientBanner - Enhanced alerts</li>
                    <li>• EpicNoteEditor - Tabbed interface</li>
                  </ul>
                </div>

                <div className="mt-4 text-center">
                  <button
                    onClick={() => setActiveView('epic')}
                    className="w-full px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-all shadow-md font-semibold"
                  >
                    Launch Epic Demo →
                  </button>
                </div>
              </div>
            </div>

            {/* Summary Section */}
            <div className="mt-6 bg-green-50 border border-green-200 rounded-lg p-6">
              <h3 className="font-semibold text-green-800 mb-3">🎉 Both Systems Complete!</h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <h4 className="font-semibold text-green-700 mb-2">Cerner Features:</h4>
                  <ul className="text-green-600 space-y-1 text-xs">
                    <li>• Dark sidebar (#2c3e50)</li>
                    <li>• SOAP note validation</li>
                    <li>• Auto-save (30s)</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold text-green-700 mb-2">Epic Features:</h4>
                  <ul className="text-green-600 space-y-1 text-xs">
                    <li>• Tabbed note editor</li>
                    <li>• Framer Motion animations</li>
                    <li>• Review of Systems grid</li>
                  </ul>
                </div>
              </div>
            </div>
          </main>
        </div>
      )}
    </QueryClientProvider>
  );
}

export default App;
