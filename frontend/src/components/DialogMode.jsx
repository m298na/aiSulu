import VoiceInput from "./VoiceInput";

function sourceLabel(source) {
  if (source === "knowledge_base") {
    return "Ответ из локальной базы знаний";
  }
  if (source === "openai") {
    return "Ответ через OpenAI";
  }
  if (source === "mock") {
    return "Mock-режим";
  }
  return "Fallback-режим";
}

export default function DialogMode({
  question,
  answer,
  source,
  fallbackUsed,
  isLoading,
  history,
  suggestions,
  onQuestionChange,
  onSubmit,
  onAskSuggestion,
  onCaptureVoice,
  isListening,
  onBack,
}) {
  return (
    <section className="dialog-layout">
      <div className="dialog-layout__header">
        <div>
          <span className="eyebrow">Диалоговый режим</span>
          <h2>Задайте вопрос AI.Sulu</h2>
        </div>
        <button className="ghost-button" onClick={onBack}>
          Завершить диалог
        </button>
      </div>

      <form className="question-form" onSubmit={onSubmit}>
        <textarea
          value={question}
          onChange={(event) => onQuestionChange(event.target.value)}
          placeholder="Например: где находится приемная комиссия?"
          rows={4}
        />
        <div className="question-form__actions">
          <VoiceInput isListening={isListening} onCapture={onCaptureVoice} />
          <button className="primary-button" type="submit" disabled={isLoading}>
            {isLoading ? "AI.Sulu отвечает..." : "Получить ответ"}
          </button>
        </div>
      </form>

      <div className="suggestions">
        {suggestions.slice(0, 4).map((item) => (
          <button
            className="suggestion-chip"
            key={item.id}
            onClick={() => onAskSuggestion(item.question)}
            type="button"
          >
            {item.question}
          </button>
        ))}
      </div>

      <div className="response-card">
        <div className="response-card__meta">
          <span>{sourceLabel(source)}</span>
          <span className={fallbackUsed ? "status-pill status-pill--warning" : "status-pill"}>
            {fallbackUsed ? "Нужен сотрудник университета" : "Ответ найден"}
          </span>
        </div>
        <p className="response-card__text">
          {answer || "Ответ появится здесь после отправки вопроса."}
        </p>
      </div>

      <div className="history-panel">
        <div className="history-panel__title">Последние вопросы</div>
        {history.length === 0 ? (
          <p className="support-text">
            Пока нет истории диалога. Задайте первый вопрос.
          </p>
        ) : (
          history.map((item) => (
            <article className="history-item" key={item.id}>
              <div className="history-item__question">{item.question}</div>
              <div className="history-item__answer">{item.answer}</div>
            </article>
          ))
        )}
      </div>
    </section>
  );
}
