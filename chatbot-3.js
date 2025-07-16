window.addEventListener('load', function () {
  const DEBUG = true; // Enable/disable debug logging
  
  function log(...args) {
    if (DEBUG) console.log('🤖 Chatbot:', ...args);
  }

  function error(...args) {
    if (DEBUG) console.error('🔥 Chatbot Error:', ...args);
  }

  log("✅ Chatbot script loaded");

  (function () {
    // Analytics tracking
    const analytics = {
      events: [],
      track(event, data) {
        this.events.push({
          event,
          data,
          timestamp: new Date().toISOString()
        });
        if (this.events.length > 1000) this.events.shift();
        log('Analytics:', event, data);
      }
    };

    // Helper Functions
    function createEl(tag, attrs, text) {
      const el = document.createElement(tag);
      if (attrs) for (const k in attrs) el.setAttribute(k, attrs[k]);
      if (text) el.textContent = text;
      return el;
    }

    function getUserId() {
      let uid = localStorage.getItem("chat_user_id");
      if (!uid) {
        uid = crypto.randomUUID();
        localStorage.setItem("chat_user_id", uid);
      }
      return uid;
    }

    function escapeHtml(unsafe) {
      return unsafe
        ?.toString()
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;") || '';
    }

    // Rate limiting
    const MESSAGE_RATE_LIMIT = 1000; // 1 second between messages
    let lastMessageTime = 0;

    function isRateLimited() {
      const now = Date.now();
      if (now - lastMessageTime < MESSAGE_RATE_LIMIT) {
        return true;
      }
      lastMessageTime = now;
      return false;
    }

    // Message history
    const MAX_HISTORY = 50;
    function saveMessageToHistory(message, type) {
      try {
        const history = JSON.parse(localStorage.getItem('chatbot_history') || '[]');
        history.push({ message, type, timestamp: Date.now() });
        while (history.length > MAX_HISTORY) history.shift();
        localStorage.setItem('chatbot_history', JSON.stringify(history));
      } catch (err) {
        error('Failed to save message history:', err);
      }
    }

    function loadMessageHistory() {
      try {
        const history = JSON.parse(localStorage.getItem('chatbot_history') || '[]');
        history.forEach(item => {
          addMessage(item.message, `${item.type}-message`);
        });
      } catch (err) {
        error('Failed to load message history:', err);
      }
    }

    // Create UI Elements
    const style = createEl("style");
    style.textContent = `
      #chatbot-toggle {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 9999;
        background: #4CAF50;
        color: white;
        border: none;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        font-size: 30px;
        cursor: pointer;
        transition: transform 0.3s ease;
      }
      
      #chatbot-toggle:hover {
        transform: scale(1.1);
      }
      
      #chatbot-container {
        position: fixed;
        bottom: 90px;
        right: 20px;
        width: 90vw;
        max-width: 400px;
        height: 70vh;
        background: white;
        border: 1px solid #ccc;
        border-radius: 10px;
        display: flex;
        flex-direction: column;
        opacity: 0;
        transform: translateY(20px);
        pointer-events: none;
        transition: all 0.3s ease;
        z-index: 9998;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
      }
      
      #chatbot-container.visible {
        opacity: 1;
        transform: translateY(0);
        pointer-events: auto;
      }

      #chatbot-messages {
        flex: 1;
        overflow-y: auto;
        padding: 20px;
      }

      #chatbot-input-container {
        padding: 15px;
        border-top: 1px solid #eee;
        display: flex;
        gap: 10px;
        background: white;
      }

      #chatbot-input {
        flex: 1;
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 5px;
        font-size: 14px;
      }

      #chatbot-send {
        padding: 10px 20px;
        background: #4CAF50;
        color: white;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        transition: background 0.3s;
      }

      #chatbot-send:hover {
        background: #45a049;
      }

      .message-wrapper {
        display: flex;
        margin-bottom: 10px;
      }

      .message-wrapper.user {
        justify-content: flex-end;
      }

      .user-message, .bot-message {
        max-width: 80%;
        padding: 10px 15px;
        border-radius: 15px;
        font-size: 14px;
        line-height: 1.4;
        animation: fadeIn 0.3s ease;
      }

      .user-message {
        background: #4CAF50;
        color: white;
        border-bottom-right-radius: 5px;
      }

      .bot-message {
        background: #f0f0f0;
        color: #333;
        border-bottom-left-radius: 5px;
      }

      .typing-indicator {
        display: flex;
        gap: 5px;
        padding: 10px 15px;
        background: #f0f0f0;
        border-radius: 15px;
        width: fit-content;
      }

      .typing-indicator .dot {
        width: 8px;
        height: 8px;
        background: #888;
        border-radius: 50%;
        animation: bounce 1s infinite;
      }

      .typing-indicator .dot:nth-child(2) { animation-delay: 0.2s; }
      .typing-indicator .dot:nth-child(3) { animation-delay: 0.4s; }

      .bot-options {
        display: flex;
        flex-wrap: wrap;
        gap: 5px;
        margin-top: 10px;
      }

      .bot-option-button {
        background: white;
        border: 1px solid #4CAF50;
        color: #4CAF50;
        padding: 8px 15px;
        border-radius: 20px;
        cursor: pointer;
        transition: all 0.3s;
        animation: fadeIn 0.3s ease;
      }

      .bot-option-button:hover {
        background: #4CAF50;
        color: white;
      }

      @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
      }

      @keyframes bounce {
        0%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-8px); }
      }

      @media (max-width: 480px) {
        #chatbot-container {
          width: 100%;
          right: 0;
          bottom: 0;
          height: 100vh;
          max-width: none;
          border-radius: 0;
        }

        #chatbot-toggle {
          bottom: 10px;
          right: 10px;
        }
      }
      .bot-message h3 {
        margin-top: 0;
        margin-bottom: 0.5em;
      }
    `;
    document.head.appendChild(style);

    const container = createEl("div", { 
      id: "chatbot-container",
      role: "dialog",
      "aria-label": "Chat bot interface"
    });
    const messages = createEl("div", { 
      id: "chatbot-messages",
      role: "log",
      "aria-live": "polite"
    });
    const inputContainer = createEl("div", { id: "chatbot-input-container" });
    const input = createEl("input", {
      id: "chatbot-input",
      placeholder: "Hazme una pregunta...",
      "aria-label": "Chat input"
    });
    const sendBtn = createEl("button", { 
      id: "chatbot-send",
      "aria-label": "Send message"
    }, "Enviar");

    inputContainer.appendChild(input);
    inputContainer.appendChild(sendBtn);
    container.appendChild(messages);
    container.appendChild(inputContainer);
    document.body.appendChild(container);

    const toggle = createEl("button", { 
      id: "chatbot-toggle",
      "aria-label": "Toggle chat"
    }, "💬");
    document.body.appendChild(toggle);

    // Message Functions
    function addMessage(content, className) {
      const wrapper = createEl("div", {
        class: `message-wrapper ${className === "user-message" ? "user" : "bot"}`,
        role: "listitem"
      });

      const msg = createEl("div", { 
        class: className,
        role: className === "bot-message" ? "status" : "none"
      });
      msg.innerHTML = content;

      wrapper.appendChild(msg);
      messages.appendChild(wrapper);

      requestAnimationFrame(() => {
        messages.scrollTo({
          top: messages.scrollHeight,
          behavior: 'smooth'
        });
      });

      saveMessageToHistory(content, className.replace('-message', ''));
      analytics.track('message_added', { type: className });

      return msg;
    }

    function addOptions(options) {
      const wrapper = createEl("div", { 
        class: "bot-options",
        role: "group",
        "aria-label": "Message options"
      });

      options.forEach((option, index) => {
        const btn = createEl("button", {
          class: "bot-option-button",
          style: `animation-delay: ${index * 100}ms;`,
          role: "button"
        }, option);

        btn.onclick = () => {
          wrapper.querySelectorAll("button").forEach(b => b.disabled = true);
          wrapper.remove();
          sendBotMessage(option);
        };

        wrapper.appendChild(btn);
      });

      messages.appendChild(wrapper);
      messages.scrollTop = messages.scrollHeight;
    }

    function showTypingIndicator() {
      const wrapper = createEl("div", { 
        class: "message-wrapper bot",
        role: "status",
        "aria-label": "Bot is typing"
      });
      const indicator = createEl("div", { class: "typing-indicator" });
      indicator.innerHTML = `<span class="dot"></span><span class="dot"></span><span class="dot"></span>`;
      wrapper.appendChild(indicator);
      messages.appendChild(wrapper);
      messages.scrollTop = messages.scrollHeight;
      return wrapper;
    }

    function removeTypingIndicator(indicator) {
      if (indicator?.remove) indicator.remove();
    }

    // API Functions
    async function callApi(message, userId, retries = 3) {
      const API_URL = 'https://production-goshop-d116fe7863dc.herokuapp.com/chat';
      
      for (let i = 0; i < retries; i++) {
        try {
          const response = await fetch(API_URL, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "Accept": "application/json"
            },
            body: JSON.stringify({
              message,
              user_id: userId,
              client_timestamp: new Date().toISOString()
            })
          });

          if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
          }
          
          const data = await response.json();
          if (data.error) {
            throw new Error(data.error);
          }
          analytics.track('api_success', { message, attempt: i + 1 });
          return data;
        } catch (err) {
          error('API call failed:', err);
          analytics.track('api_error', { message, error: err.message, attempt: i + 1 });
          if (i === retries - 1) throw err;
          await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
        }
      }
    }

    function sendBotMessage(userMessage) {
      if (!userMessage?.trim()) {
        error('Empty message rejected');
        return;
      }

      if (isRateLimited()) {
        log('Message rate limited');
        return;
      }

      addMessage(userMessage, "user-message");
      const typingIndicator = showTypingIndicator();
      input.disabled = true;
      sendBtn.disabled = true;

      callApi(userMessage, getUserId())
        .then(data => {
          console.log("API response:", data); // Debug log for API response
          removeTypingIndicator(typingIndicator);

          const products = Array.isArray(data.products) ? data.products : [];
          const options = Array.isArray(data.options) ? data.options : [];
          const pharmacies = Array.isArray(data.pharmacies) ? data.pharmacies : [];

          // If backend returns an array of messages, show each as a separate bot message
          if (Array.isArray(data.messages)) {
            data.messages.forEach(msg => addMessage(msg, "bot-message"));
          } else {
            const botText = data.text?.trim() || "🤖 No entendí eso, ¿puedes intentarlo de otra forma?";
            // Remove any "(INIT)", "(REC)", "(CUS)", "(DONE)" prefixes from the text
            const cleanBotText = botText.replace(/^(\(INIT|REC|CUS|DONE)\)/, '').trim();
            addMessage(cleanBotText, "bot-message");
          }

          // Render pharmacies if present
          if (pharmacies.length > 0) {
            const formatted = pharmacies.map(pharmacy => `
              <div style="margin-bottom: 10px;">
                <a href="${escapeHtml(pharmacy.maps_link)}" target="_blank" rel="noopener noreferrer">
                  🏥 ${escapeHtml(pharmacy.name)}
                </a>
              </div>
            `).join("");
            addMessage(formatted, "bot-message");
          }

          if (products.length > 0) {
            const formatted = products.map(item => `
              <div style="margin-bottom: 12px; display: flex; align-items: flex-start; gap: 12px;">
                ${item.image ? `<img src="${escapeHtml(item.image)}" alt="Imagen de ${escapeHtml(item.name)}" style="width:60px; height:60px; object-fit:cover; border-radius:8px; flex-shrink:0;">` : ''}
                <div>
                  <b>🟢 ${escapeHtml(item.name)}</b> - 💲${escapeHtml(item.price)}<br>
                  <b>🏷️ Categoría:</b> ${escapeHtml(item.category)}<br>
                  <b>📝 Descripción:</b> ${escapeHtml(item.description)}<br>
                  <b>💊 Uso:</b> ${escapeHtml(item.usage)}<br>
                  ${item.recommended_for ? `<b>👍 Recomendado para:</b> ${escapeHtml(item.recommended_for)}<br>` : ''}
                  ${item.allergens ? `<b>⚠️ Alérgenos:</b> ${escapeHtml(item.allergens)}<br>` : ''}
                  <a href="${escapeHtml(item.link)}" target="_blank" rel="noopener noreferrer">🔗 Ver producto</a>
                </div>
              </div>
            `).join("");
            addMessage(formatted, "bot-message");
          }

          // Show followup_text if present (now after results)
          if (data.followup_text) {
            addMessage(data.followup_text, "bot-message");
          }

          if (options && options.length > 0) {
            addOptions(options);
          }
        })
        .catch(err => {
          removeTypingIndicator(typingIndicator);
          addMessage("⚠️ Lo siento, ocurrió un error en el servidor. Inténtalo de nuevo.", "bot-message");
        })
        .finally(() => {
          input.disabled = false;
          sendBtn.disabled = false;
        });
    }

    function sendMessage() {
      const userMessage = input.value.trim();
      if (!userMessage) return;
      sendBotMessage(userMessage);
      input.value = "";
    }

    // Event Listeners
    sendBtn.addEventListener("click", sendMessage);
    input.addEventListener("keypress", e => {
      if (e.key === "Enter") sendMessage();
    });

    toggle.addEventListener("click", () => {
      container.classList.toggle("visible");
      if (!window.__chatbotInitialized) {
        addMessage("Conectando con el asistente...", "bot-message");
        callApi("__init__", getUserId())
          .then(data => {
            // Remove the connecting message
            messages.lastElementChild?.remove();
            if (Array.isArray(data.messages)) {
              data.messages.forEach(msg => addMessage(msg, "bot-message"));
            } else if (data.text) {
              // Remove any "(INIT)" prefix from the text
              const cleanBotText = data.text.replace(/^\(INIT\)/, '').trim();
              addMessage(cleanBotText, "bot-message");
            }
            if (data.options?.length) {
              addOptions(data.options);
            }
          })
          .catch(err => {
            error("Initial chat trigger failed:", err);
            // Remove the connecting message
            messages.lastElementChild?.remove();
            addMessage("👋 Hola! Pero no pude conectarme al servidor. Por favor, intenta de nuevo más tarde.", "bot-message");
          });
        window.__chatbotInitialized = true;
      }
    });

    window.addEventListener('online', () => {
      log('Connection restored');
      addMessage("✅ Conexión restaurada", "bot-message");
    });

    window.addEventListener('offline', () => {
      error('Connection lost');
      addMessage("⚠️ Sin conexión - Los mensajes se enviarán cuando vuelva la conexión", "bot-message");
    });

    // Error boundary
    window.addEventListener('error', event => {
      error('Global error:', event.error);
      addMessage("⚠️ Lo siento, ocurrió un error inesperado.", "bot-message");
    });
  })();
}); 
