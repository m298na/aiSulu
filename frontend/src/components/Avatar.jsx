export default function Avatar({ mode, isSpeaking, isThinking }) {
  const avatarClassName = [
    "avatar-shell",
    `avatar-shell--${mode}`,
    isSpeaking ? "avatar-shell--speaking" : "",
    isThinking ? "avatar-shell--thinking" : "",
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div className={avatarClassName}>
      <div className="avatar-aura" />
      <div className="avatar-core">
        <div className="avatar-face">
          <span className="avatar-eye" />
          <span className="avatar-eye" />
        </div>
        <div className="avatar-smile" />
      </div>
      <div className="avatar-ring avatar-ring--outer" />
      <div className="avatar-ring avatar-ring--inner" />
    </div>
  );
}
