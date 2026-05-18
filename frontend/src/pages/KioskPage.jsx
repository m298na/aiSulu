import { useEffect, useMemo, useState } from "react";
import Avatar from "../components/Avatar";
import DialogMode from "../components/DialogMode";
import IdleMode from "../components/IdleMode";
import TriggerMode from "../components/TriggerMode";
import { askQuestion, getKnowledgeFaqs, transcribeAudio } from "../api/client";

const GREETINGS = [
  "Добро пожаловать в AIU. Нажмите кнопку, и я помогу с навигацией и вопросами.",
  "Здравствуйте. Я AI.Sulu, цифровой ассистент университета для гостей и студентов.",
  "Могу подсказать, где находятся нужные отделы, аудитории и основные сервисы кампуса.",
];

function createSessionId() {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return `session-${Date.now()}`;
}

export default function KioskPage() {
  const [mode, setMode] = useState("idle");
  const [greetingIndex, setGreetingIndex] = useState(0);
  const [sessionId] = useState(() => createSessionId());
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [source, setSource] = useState("knowledge_base");
  const [fallbackUsed, setFallbackUsed] = useState(false);
  const [history, setHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [suggestions, setSuggestions] = useState([]);

  useEffect(() => {
    const intervalId = window.setInterval(() => {
      setGreetingIndex((current) => (current + 1) % GREETINGS.length);
    }, 6000);

    return () => window.clearInterval(intervalId);
  }, []);

  useEffect(() => {
    getKnowledgeFaqs()
      .then((items) => setSuggestions(items))
      .catch(() => setSuggestions([]));
  }, []);

  useEffect(() => {
    if (mode === "idle") {
      return undefined;
    }

    const timeoutId = window.setTimeout(() => {
      setMode("idle");
      setQuestion("");
    }, 90000);

    return () => window.clearTimeout(timeoutId);
  }, [mode, question, answer]);

  const greeting = useMemo(() => GREETINGS[greetingIndex], [greetingIndex]);

  async function submitQuestion(questionText, inputMode = "text") {
    const preparedQuestion = questionText.trim();
    if (!preparedQuestion) {
      return;
    }

    setIsLoading(true);
    setMode("dialog");

    try {
      const response = await askQuestion({
        question: preparedQuestion,
        input_mode: inputMode,
        session_id: sessionId,
      });

      setAnswer(response.answer);
      setSource(response.source);
      setFallbackUsed(response.fallback_used);
      setQuestion(preparedQuestion);
      setHistory((current) => [
        {
          id: `${Date.now()}-${current.length}`,
          question: preparedQuestion,
          answer: response.answer,
        },
        ...current,
      ].slice(0, 6));
    } catch (requestError) {
      setAnswer(
        requestError.message ||
          "Не удалось получить ответ. Обратитесь к сотруднику университета.",
      );
      setSource("fallback");
      setFallbackUsed(true);
    } finally {
      setIsLoading(false);
    }
  }

  async function handleVoiceCapture() {
    setIsListening(true);
    try {
      const response = await transcribeAudio();
      setQuestion(response.transcript);
      await submitQuestion(response.transcript, "voice");
    } catch (requestError) {
      setAnswer(requestError.message);
      setFallbackUsed(true);
      setSource("fallback");
    } finally {
      setIsListening(false);
    }
  }

  function handleDialogSubmit(event) {
    event.preventDefault();
    submitQuestion(question, "text");
  }

  function resetToIdle() {
    setMode("idle");
    setQuestion("");
    setAnswer("");
    setSource("knowledge_base");
    setFallbackUsed(false);
  }

  return (
    <main className="kiosk-page">
      <div className="ambient-orb ambient-orb--left" />
      <div className="ambient-orb ambient-orb--right" />

      <section className="kiosk-stage">
        <div className="kiosk-stage__avatar">
          <Avatar
            mode={mode}
            isSpeaking={Boolean(answer) && !isLoading}
            isThinking={isLoading || isListening}
          />
        </div>

        <div className="kiosk-stage__content">
          {mode === "idle" ? (
            <IdleMode greeting={greeting} onStart={() => setMode("trigger")} />
          ) : null}

          {mode === "trigger" ? (
            <TriggerMode
              onTextStart={() => setMode("dialog")}
              onVoiceStart={handleVoiceCapture}
              onBack={resetToIdle}
            />
          ) : null}

          {mode === "dialog" ? (
            <DialogMode
              question={question}
              answer={answer}
              source={source}
              fallbackUsed={fallbackUsed}
              isLoading={isLoading}
              history={history}
              suggestions={suggestions}
              isListening={isListening}
              onQuestionChange={setQuestion}
              onSubmit={handleDialogSubmit}
              onCaptureVoice={handleVoiceCapture}
              onAskSuggestion={(suggestedQuestion) => submitQuestion(suggestedQuestion)}
              onBack={resetToIdle}
            />
          ) : null}
        </div>
      </section>
    </main>
  );
}
