export default function VoiceInput({ isListening, onCapture }) {
  return (
    <button
      className={`voice-button ${isListening ? "voice-button--active" : ""}`}
      onClick={onCapture}
      type="button"
    >
      <span className="voice-button__pulse" />
      {isListening ? "Слушаю..." : "Голосовой ввод"}
    </button>
  );
}
