"use client"

import React, { useState, useEffect } from 'react';
import { Play, Square, Globe, ExternalLink, Loader2, CheckCircle, AlertCircle } from 'lucide-react';

type Status = 'IDLE' | 'RUNNING' | 'STOPPED' | 'FINISHED' | 'ERROR';

export default function NeuralTesterDashboard() {
  const [url, setUrl] = useState('');
  const [bddGoal, setBddGoal] = useState('Navegar no site');
  const [status, setStatus] = useState<Status>('IDLE');

  useEffect(() => {
    const savedUrl = localStorage.getItem('last_test_url');
    if (savedUrl) setUrl(savedUrl);
  }, []);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [message, setMessage] = useState('');

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const res = await fetch('http://localhost:8000/status');
        const data = await res.json();
        setStatus(data.status);
        if (data.session_id) setSessionId(data.session_id);
      } catch (err) {
        console.error('Failed to fetch status', err);
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleStart = async () => {
    if (!url) {
      setMessage('Por favor, insira uma URL válida.');
      return;
    }

    localStorage.setItem('last_test_url', url);
    setStatus('RUNNING');
    setMessage('');

    try {
      const res = await fetch('http://localhost:8000/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, bdd_goal: bddGoal }),
      });
      const data = await res.json();
      if (data.status === 'success') {
        setSessionId(data.session_id);
      } else {
        setStatus('ERROR');
        setMessage(data.message);
      }
    } catch (err) {
      setStatus('ERROR');
      setMessage('Erro ao conectar com a API.');
    }
  };

  const handleStop = async () => {
    try {
      await fetch('http://localhost:8000/stop', { method: 'POST' });
      setStatus('STOPPED');
    } catch (err) {
      console.error('Failed to stop agent', err);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-8 font-sans">
      <header className="max-w-4xl mx-auto mb-12 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
            Neural Web Tester
          </h1>
          <p className="text-slate-400 mt-1">Interface de Controle do Agente Autônomo</p>
        </div>
        <div className="flex gap-4">
          <a
            href="https://govinda777.github.io"
            target="_blank"
            className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors text-sm"
          >
            <Globe size={16} />
            Site do Projeto
            <ExternalLink size={14} className="opacity-50" />
          </a>
        </div>
      </header>

      <main className="max-w-4xl mx-auto space-y-6">
        {/* Welcome & Setup Section */}
        <section className="bg-slate-800/50 border border-slate-700 p-6 rounded-2xl">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            Configuração do Teste
          </h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-400 mb-1">URL de Destino</label>
              <input
                type="text"
                placeholder="https://exemplo.com"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                disabled={status === 'RUNNING'}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500 outline-none transition-all disabled:opacity-50"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-400 mb-1">Objetivo Gherkin (When)</label>
              <input
                type="text"
                placeholder="Ex: Ao clicar no botão de login"
                value={bddGoal}
                onChange={(e) => setBddGoal(e.target.value)}
                disabled={status === 'RUNNING'}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500 outline-none transition-all disabled:opacity-50"
              />
            </div>
          </div>
        </section>

        {/* Controller Bar */}
        <section className="bg-slate-800 border border-slate-700 p-6 rounded-2xl flex flex-wrap items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <div className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium ${
              status === 'IDLE' ? 'bg-slate-700 text-slate-300' :
              status === 'RUNNING' ? 'bg-blue-500/20 text-blue-400 animate-pulse' :
              status === 'FINISHED' ? 'bg-emerald-500/20 text-emerald-400' :
              status === 'STOPPED' ? 'bg-yellow-500/20 text-yellow-400' :
              'bg-red-500/20 text-red-400'
            }`}>
              {status === 'IDLE' && <span>Aguardando</span>}
              {status === 'RUNNING' && <><Loader2 size={16} className="animate-spin" /> Executando</>}
              {status === 'FINISHED' && <><CheckCircle size={16} /> Finalizado</>}
              {status === 'STOPPED' && <><Square size={16} fill="currentColor" /> Parado</>}
              {status === 'ERROR' && <><AlertCircle size={16} /> Erro</>}
            </div>
            {message && <span className="text-sm text-red-400">{message}</span>}
          </div>

          <div className="flex gap-3">
            <button
              onClick={handleStart}
              disabled={status === 'RUNNING' || !url}
              className="flex items-center gap-2 px-6 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-700 disabled:text-slate-500 rounded-lg font-semibold transition-all shadow-lg shadow-emerald-900/20"
            >
              <Play size={18} fill="currentColor" />
              Iniciar
            </button>
            <button
              onClick={handleStop}
              disabled={status !== 'RUNNING'}
              className="flex items-center gap-2 px-6 py-2 bg-red-600 hover:bg-red-500 disabled:bg-slate-700 disabled:text-slate-500 rounded-lg font-semibold transition-all shadow-lg shadow-red-900/20"
            >
              <Square size={18} fill="currentColor" />
              Parar
            </button>
          </div>
        </section>

        {/* Dashboard Placeholder */}
        {status !== 'IDLE' && (
          <section className="bg-slate-800/30 border border-slate-700 border-dashed p-12 rounded-2xl text-center">
            <div className="text-slate-500">
              {status === 'RUNNING' ? (
                <div className="flex flex-col items-center gap-4">
                  <Loader2 size={48} className="animate-spin text-blue-500 opacity-50" />
                  <p>O agente está explorando {url}...</p>
                  <p className="text-sm">Abra os logs do terminal para ver o "pensamento" da IA em tempo real.</p>
                </div>
              ) : (
                <p>Relatório da sessão {sessionId?.slice(0, 8)} disponível nos artefatos do projeto.</p>
              )}
            </div>
          </section>
        )}
      </main>

      <footer className="max-w-4xl mx-auto mt-12 text-center text-slate-600 text-sm">
        <p>&copy; 2024 Neural Web Tester - Edição Educacional</p>
      </footer>
    </div>
  );
}
