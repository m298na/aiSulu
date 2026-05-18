export default function TriggerMode({ onTextStart, onVoiceStart, onBack }) {
  return (
    <section className="mode-panel">
      <span className="eyebrow">Режим активации</span>
      <h2>Чем могу помочь?</h2>
      <p className="support-text">
        Выберите удобный формат общения. В MVP голос работает через mock-режим,
        но интерфейс уже готов под реальный Speech-to-Text.
      </p>
      <div className="cta-grid">
        <button className="primary-button" onClick={onTextStart}>
          Ввести вопрос текстом
        </button>
        <button className="secondary-button" onClick={onVoiceStart}>
          Смоделировать голосовой вопрос
        </button>
      </div>
      <button className="ghost-button" onClick={onBack}>
        Вернуться в приветствие
      </button>
    </section>
  );
}
