import { useState } from 'react'

const LANGUAGES = ['MR', 'HI', 'TA', 'TE', 'BN', 'EN']

export default function InputBar({ isRecording, onStartRecord, onStopRecord }) {
  const [text,    setText]    = useState('')
  const [lang,    setLang]    = useState('MR')

  const handleMic = () => {
    isRecording ? onStopRecord() : onStartRecord()
  }

  return (
    <div className="flex items-center gap-2 px-4 py-3 border-t border-border bg-surface2">
      {/* Doc Scan */}
      <button className="w-10 h-10 rounded-lg bg-surface border border-border text-muted hover:border-accent2 hover:text-accent2 transition-colors flex items-center justify-center text-base">
        📄
      </button>

      {/* Mic */}
      <button
        onClick={handleMic}
        className={`w-10 h-10 rounded-lg flex items-center justify-center text-base transition-all ${
          isRecording
            ? 'bg-critical text-white animate-pulse shadow-[0_0_16px_rgba(255,51,85,0.4)]'
            : 'bg-gradient-to-br from-accent to-blue-700 text-white hover:scale-105'
        }`}
      >
        🎙
      </button>

      {/* Text input */}
      <input
        value={text}
        onChange={e => setText(e.target.value)}
        placeholder="Type message or let AI transcribe speech..."
        className="flex-1 px-4 py-2.5 bg-bg border border-border rounded-lg text-sm text-text placeholder:text-muted outline-none focus:border-accent transition-colors"
      />

      {/* Language selector */}
      <div className="flex gap-1">
        {LANGUAGES.map(l => (
          <button
            key={l}
            onClick={() => setLang(l)}
            className={`px-2.5 py-1.5 rounded-md text-[11px] font-bold border transition-all ${
              lang === l
                ? 'bg-accent border-accent text-white'
                : 'border-border text-muted hover:border-accent hover:text-accent'
            }`}
          >
            {l}
          </button>
        ))}
      </div>
    </div>
  )
}