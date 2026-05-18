import { useEffect, useState } from "react";
import {
  createFaq,
  deleteFaq,
  getAdminFaqs,
  getAdminStatus,
  getLogsStats,
  getQuestionLogs,
  reloadKnowledgeBase,
  updateFaq,
} from "../api/client";

const INITIAL_FORM = {
  question: "",
  answer: "",
  category: "general",
  tags: "",
  source: "manual",
  is_active: true,
};

export default function AdminPanel() {
  const [status, setStatus] = useState(null);
  const [stats, setStats] = useState(null);
  const [faqs, setFaqs] = useState([]);
  const [logs, setLogs] = useState([]);
  const [form, setForm] = useState(INITIAL_FORM);
  const [editingId, setEditingId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  async function loadAll() {
    setLoading(true);
    setError("");
    try {
      const [statusResponse, statsResponse, faqResponse, logsResponse] = await Promise.all([
        getAdminStatus(),
        getLogsStats(),
        getAdminFaqs(),
        getQuestionLogs(),
      ]);
      setStatus(statusResponse);
      setStats(statsResponse);
      setFaqs(faqResponse);
      setLogs(logsResponse);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadAll();
  }, []);

  function updateForm(field, value) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  }

  function resetForm() {
    setEditingId(null);
    setForm(INITIAL_FORM);
  }

  function startEditing(faq) {
    setEditingId(faq.id);
    setForm({
      question: faq.question,
      answer: faq.answer,
      category: faq.category,
      tags: faq.tags.join(", "),
      source: faq.source,
      is_active: faq.is_active,
    });
    setSuccess("");
    setError("");
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setSuccess("");

    const payload = {
      question: form.question.trim(),
      answer: form.answer.trim(),
      category: form.category.trim(),
      tags: form.tags
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean),
      source: form.source.trim(),
      is_active: form.is_active,
    };

    try {
      if (editingId) {
        await updateFaq(editingId, payload);
        setSuccess("FAQ обновлен.");
      } else {
        await createFaq(payload);
        setSuccess("FAQ добавлен.");
      }
      resetForm();
      await loadAll();
    } catch (requestError) {
      setError(requestError.message);
    }
  }

  async function handleDelete(id) {
    setError("");
    setSuccess("");
    try {
      await deleteFaq(id);
      if (editingId === id) {
        resetForm();
      }
      setSuccess("FAQ удален.");
      await loadAll();
    } catch (requestError) {
      setError(requestError.message);
    }
  }

  async function handleReload() {
    setError("");
    setSuccess("");
    try {
      const response = await reloadKnowledgeBase();
      setSuccess(response.message);
      await loadAll();
    } catch (requestError) {
      setError(requestError.message);
    }
  }

  return (
    <section className="admin-shell">
      <div className="admin-shell__header">
        <div>
          <span className="eyebrow">Админ-панель</span>
          <h1>Управление AI.Sulu</h1>
        </div>
        <button className="secondary-button" onClick={handleReload}>
          Обновить базу знаний
        </button>
      </div>

      {error ? <div className="feedback feedback--error">{error}</div> : null}
      {success ? <div className="feedback feedback--success">{success}</div> : null}

      {loading ? (
        <div className="admin-placeholder">Загрузка данных...</div>
      ) : (
        <>
          <div className="stats-grid">
            <div className="stat-card">
              <span>FAQ</span>
              <strong>{status?.faq_count ?? 0}</strong>
            </div>
            <div className="stat-card">
              <span>Вопросы</span>
              <strong>{stats?.total_questions ?? 0}</strong>
            </div>
            <div className="stat-card">
              <span>Fallback</span>
              <strong>{stats?.fallback_count ?? 0}</strong>
            </div>
            <div className="stat-card">
              <span>Mock Mode</span>
              <strong>{status?.use_mock_services ? "ON" : "OFF"}</strong>
            </div>
          </div>

          <div className="admin-grid">
            <form className="admin-form" onSubmit={handleSubmit}>
              <h2>{editingId ? "Редактировать FAQ" : "Добавить FAQ"}</h2>
              <input
                placeholder="Вопрос"
                value={form.question}
                onChange={(event) => updateForm("question", event.target.value)}
              />
              <textarea
                placeholder="Ответ"
                rows={6}
                value={form.answer}
                onChange={(event) => updateForm("answer", event.target.value)}
              />
              <input
                placeholder="Категория"
                value={form.category}
                onChange={(event) => updateForm("category", event.target.value)}
              />
              <input
                placeholder="Теги через запятую"
                value={form.tags}
                onChange={(event) => updateForm("tags", event.target.value)}
              />
              <input
                placeholder="Источник"
                value={form.source}
                onChange={(event) => updateForm("source", event.target.value)}
              />
              <label className="checkbox-row">
                <input
                  type="checkbox"
                  checked={form.is_active}
                  onChange={(event) => updateForm("is_active", event.target.checked)}
                />
                Активен
              </label>
              <div className="form-actions">
                <button className="primary-button" type="submit">
                  {editingId ? "Сохранить изменения" : "Добавить FAQ"}
                </button>
                <button className="ghost-button" onClick={resetForm} type="button">
                  Сбросить
                </button>
              </div>
            </form>

            <div className="admin-list">
              <h2>FAQ</h2>
              {faqs.map((faq) => (
                <article className="faq-card" key={faq.id}>
                  <div className="faq-card__header">
                    <strong>{faq.question}</strong>
                    <span className={faq.is_active ? "status-pill" : "status-pill status-pill--warning"}>
                      {faq.is_active ? "Активен" : "Скрыт"}
                    </span>
                  </div>
                  <p>{faq.answer}</p>
                  <div className="faq-card__meta">
                    <span>{faq.category}</span>
                    <span>{faq.tags.join(", ") || "без тегов"}</span>
                  </div>
                  <div className="faq-card__actions">
                    <button className="secondary-button" onClick={() => startEditing(faq)}>
                      Изменить
                    </button>
                    <button className="ghost-button" onClick={() => handleDelete(faq.id)}>
                      Удалить
                    </button>
                  </div>
                </article>
              ))}
            </div>
          </div>

          <div className="logs-panel">
            <h2>Логи вопросов</h2>
            <div className="logs-list">
              {logs.map((log) => (
                <article className="log-card" key={log.id}>
                  <div className="log-card__header">
                    <strong>{log.question}</strong>
                    <span>{log.created_at}</span>
                  </div>
                  <p>{log.answer}</p>
                  <div className="faq-card__meta">
                    <span>Источник: {log.source}</span>
                    <span>Режим: {log.input_mode}</span>
                  </div>
                </article>
              ))}
            </div>
          </div>
        </>
      )}
    </section>
  );
}
