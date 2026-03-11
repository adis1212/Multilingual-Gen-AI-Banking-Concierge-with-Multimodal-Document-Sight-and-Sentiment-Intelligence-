import { useRef, useEffect, useState, useCallback } from 'react'
import { useSessionStore }  from '@/store/sessionStore'
import { useWebSocket }     from '@/hooks/useWebSocket'
import { useAudioCapture }  from '@/hooks/useAudioCapture'
import { extractIntent }    from '@/services/gpt4oService'
import { checkCompliance }  from '@/services/gpt4oService'
import MessageBubble        from './MessageBubble'
import InputBar             from './InputBar'
import toast                from 'react-hot-toast'

// Demo messages to show on load
const DEMO_MESSAGES = [
  {
    id: '1', speaker: 'customer', channel: 'A', language: 'mr',
    text: 'मला माझे कार्ड हरवले आहे. मला खूप काळजी वाटत आहे!',
    translation: 'I lost my card. I am very worried!',
    intent: { intent: 'lost_card', urgency: 'critical', emotion: 'distressed',
              staff_advisory: 'CRITICAL: Customer reported a lost card. Initiate card block immediately.' },
    timestamp: new Date().toISOString(),
  },
  {
    id: '2', speaker: 'ai', channel: null, language: 'en',
    text: '🔴 CRITICAL: Customer reported a lost card. Stress level elevated (78%).\n\n1. Acknowledge distress warmly in Marathi\n2. Initiate card block (Card #4829)\n3. Offer expedited re-issue (3 business days)\n4. Verify KYC before proceeding',
    timestamp: new Date().toISOString(),
  },
  {
    id: '3', speaker: 'staff', channel: 'B', language: 'en',
    text: "Don't worry, Priya ji. We'll block your card right now and help you get a new one today.",
    translation: 'काळजी करू नका, प्रिया जी. आम्ही आत्ताच तुमचे कार्ड ब्लॉक करतो.',
    timestamp: new Date().toISOString(),
  },
]

export default function ConversationPanel() {
  const bottomRef  = useRef(null)
  const [language, setLanguage] = useState('mr')
  const { sessionId, messages, addMessage } = useSessionStore()

  const { sendAudioChunk } = useWebSocket(sessionId)
  const { isRecording, startRecording, stopRecording } = useAudioCapture({
    onChunk: sendAudioChunk,
    language,
  })

  // Seed demo messages
  useEffect(() => {
    if (messages.length === 0) {
      DEMO_MESSAGES.forEach(m => addMessage(m))
    }
  }, [])

  // Auto-scroll to bottom
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // --- Handle text submit from InputBar ---
  const handleSendText = useCallback(async (text, lang) => {
    // 1. Add staff message to conversation
    addMessage({
      speaker: 'staff',
      channel: 'B',
      language: lang || 'en',
      text,
      translation: '',
    })

    // 2. Run compliance check silently in background
    checkCompliance(text, sessionId).then(compliance => {
      if (compliance && !compliance.compliant) {
        toast.error(`⚠ Compliance: ${compliance.warning_message || 'Potential RBI violation detected'}`, {
          duration: 6000,
        })
        addMessage({
          speaker: 'ai',
          channel: null,
          language: 'en',
          text: `⚠ COMPLIANCE ALERT: ${compliance.warning_message || 'Review RBI guidelines'}\n\nViolations: ${(compliance.violations || []).join(', ')}`,
        })
      }
    }).catch(() => {})

    // 3. Extract intent from staff message for AI advisory
    try {
      const intent = await extractIntent(text, lang || 'en', {}, sessionId)
      if (intent && intent.staff_advisory) {
        const advisoryLines = [
          intent.urgency ? `${intent.urgency === 'critical' ? '🔴' : intent.urgency === 'high' ? '🟡' : '🟢'} ${intent.urgency.toUpperCase()}: ${intent.staff_advisory}` : intent.staff_advisory,
        ]

        if (intent.suggested_actions && intent.suggested_actions.length > 0) {
          advisoryLines.push('')
          intent.suggested_actions.forEach((action, i) => {
            advisoryLines.push(`${i + 1}. ${action.replace(/_/g, ' ').replace(/^./, c => c.toUpperCase())}`)
          })
        }

        addMessage({
          speaker: 'ai',
          channel: null,
          language: 'en',
          text: advisoryLines.join('\n'),
          intent,
        })
      }
    } catch (err) {
      // Intent extraction failed silently — don't block the conversation
      console.warn('Intent extraction failed:', err.message)
    }
  }, [addMessage, sessionId])

  // --- Handle doc scan button ---
  const handleDocScan = useCallback(() => {
    // Trigger click on the document upload input in the sidebar
    const fileInput = document.querySelector('#doc-ocr-file-input')
    if (fileInput) {
      fileInput.click()
    } else {
      toast('📄 Use the Document Sight panel on the right to upload documents', { icon: '👉' })
    }
  }, [])

  // --- Handle language change ---
  const handleLanguageChange = useCallback((lang) => {
    setLanguage(lang)
  }, [])

  const allMessages = messages.length > 0 ? messages : DEMO_MESSAGES

  return (
    <>
      <div className="flex-1 overflow-y-auto px-5 py-4 flex flex-col gap-4">
        {allMessages.map(msg => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        <div ref={bottomRef} />
      </div>

      <InputBar
        isRecording={isRecording}
        onStartRecord={() => startRecording('A')}
        onStopRecord={stopRecording}
        onSendText={handleSendText}
        onDocScan={handleDocScan}
        onLanguageChange={handleLanguageChange}
      />
    </>
  )
}