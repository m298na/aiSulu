export default function IdleMode({ greeting, onStart }) {
  return (
    <section className="mode-panel mode-panel--idle">
      <span className="eyebrow">Цифровой ассистент университета</span>
      <h1>AI.Sulu</h1>
      <p className="lead-text">
        {greeting}
      </p>
      <p className="support-text">
        Я помогу найти аудитории, отделы, базовую информацию о поступлении и
        учебном процессе.
      </p>
      <button className="primary-button" onClick={onStart}>
        Начать диалог
      </button>
    </section>
  );
}
