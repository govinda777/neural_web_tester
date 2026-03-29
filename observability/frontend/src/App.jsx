import React, { useState, useEffect } from 'react';
import LivePreview from './components/LivePreview';
import FeatureImportance from './components/FeatureImportance';
import StateGraph from './components/StateGraph';

const App = () => {
  const [session, setSession] = useState(null);
  const [steps, setSteps] = useState([]);
  const [currentStepIdx, setCurrentStepIdx] = useState(0);
  const [ws, setWs] = useState(null);
  const [isLive, setIsLive] = useState(true);

  useEffect(() => {
    const socket = new WebSocket('ws://localhost:8000/ws');

    socket.onopen = () => {
        console.log('Connected to Telemetry WS');
    };

    socket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'init_session') {
        setSession(message.data);
        setSteps([]);
        setCurrentStepIdx(0);
      } else if (message.type === 'step_update') {
        setSteps(prev => {
          const newSteps = [...prev, message.data];
          // Use current isLive state from the component's state during message handling
          return newSteps;
        });
      }
    };

    setWs(socket);
    return () => socket.close();
  }, []); // Run only once

  // Separately handle step updates when steps change or isLive changes
  useEffect(() => {
    if (isLive && steps.length > 0) {
      setCurrentStepIdx(steps.length - 1);
    }
  }, [steps.length, isLive]);

  const currentStep = steps[currentStepIdx];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 p-6 flex flex-col font-sans text-gray-900 dark:text-gray-100">
      <header className="mb-8 flex justify-between items-center border-b pb-4 border-gray-200 dark:border-gray-800">
        <div>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-500 bg-clip-text text-transparent">
            Neural Web Tester - Vision
          </h1>
          {session && (
            <p className="text-sm text-gray-500 mt-1 italic">
              Objetivo: {session.bdd_goal} | URL: {session.url}
            </p>
          )}
        </div>
        <div className="flex items-center gap-4">
          <button
            onClick={() => setIsLive(!isLive)}
            className={`px-4 py-2 rounded-full font-semibold text-sm transition-all shadow-sm flex items-center gap-2 ${
                isLive ? 'bg-red-500 text-white animate-pulse' : 'bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-300'
            }`}
          >
            <div className={`w-2 h-2 rounded-full ${isLive ? 'bg-white' : 'bg-gray-400'}`}></div>
            {isLive ? 'AO VIVO' : 'PAUSADO'}
          </button>
        </div>
      </header>

      <main className="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-8 overflow-hidden">
        {/* Painel Central: Preview e Timeline */}
        <section className="lg:col-span-2 space-y-6 flex flex-col min-h-0">
          <div className="flex-1 bg-white dark:bg-gray-900 rounded-xl shadow-xl overflow-hidden border border-gray-200 dark:border-gray-800">
            <LivePreview stepData={currentStep} />
          </div>

          {/* Timeline Control */}
          <div className="p-6 bg-white dark:bg-gray-900 rounded-xl shadow-lg border border-gray-200 dark:border-gray-800">
            <div className="flex justify-between items-center mb-4">
              <span className="text-sm font-medium">Fluxo Temporal (Passos)</span>
              <span className="text-sm text-blue-500 font-bold">{currentStepIdx + 1} / {steps.length}</span>
            </div>
            <input
              type="range"
              min="0"
              max={Math.max(0, steps.length - 1)}
              value={currentStepIdx}
              onChange={(e) => {
                setIsLive(false);
                setCurrentStepIdx(parseInt(e.target.value));
              }}
              className="w-full h-2 bg-gray-200 dark:bg-gray-800 rounded-lg appearance-none cursor-pointer accent-blue-500"
            />
          </div>
        </section>

        {/* Barra Lateral: Decisões e Features */}
        <aside className="space-y-6 overflow-y-auto pr-2 custom-scrollbar">
          {/* Action Card */}
          <div className="p-6 bg-white dark:bg-gray-900 rounded-xl shadow-lg border border-gray-200 dark:border-gray-800">
            <h3 className="text-sm font-bold uppercase tracking-wider text-gray-500 mb-4">Intenção do Agente</h3>
            {currentStep?.action ? (
                <div className="space-y-4">
                    <div className="flex justify-between items-end">
                        <span className="text-3xl font-black text-indigo-600">{currentStep.action.type}</span>
                        <div className="text-right">
                            <div className="text-[10px] text-gray-400 font-bold">CONFIANÇA</div>
                            <div className="text-xl font-mono text-green-500">{(currentStep.action.confidence * 100).toFixed(1)}%</div>
                        </div>
                    </div>
                    <div className="text-xs p-3 bg-blue-50 dark:bg-blue-900/20 text-blue-800 dark:text-blue-300 rounded-lg border border-blue-100 dark:border-blue-900/50 italic leading-relaxed">
                        "O agente identificou que {currentStep.action.type} no elemento ID {currentStep.action.element_id} é o caminho mais provável para atingir o objetivo Gherkin."
                    </div>
                </div>
            ) : (
                <div className="text-gray-400 italic text-sm py-4">Nenhuma ação registrada neste passo (Reset / Inicialização)</div>
            )}
          </div>

          {/* Feature Monitor */}
          <div className="bg-white dark:bg-gray-900 rounded-xl shadow-lg border border-gray-200 dark:border-gray-800 overflow-hidden">
            <FeatureImportance weights={currentStep?.observation?.features_weights} />
          </div>

          {/* State Graph */}
          <div className="p-6 bg-white dark:bg-gray-900 rounded-xl shadow-lg border border-gray-200 dark:border-gray-800">
            <h3 className="text-sm font-bold uppercase tracking-wider text-gray-500 mb-4 text-left">Mapa Mental de Estados</h3>
            <StateGraph steps={steps} />
            <p className="text-[10px] text-gray-400 mt-2 italic text-left">Nós representam hashes do DOM; arestas mostram transições por ação.</p>
          </div>
        </aside>
      </main>
    </div>
  );
};

export default App;
