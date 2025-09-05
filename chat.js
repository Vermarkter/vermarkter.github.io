const CHAT_PROMPTS = {
  de: [
    "Vielen Dank für Ihre Nachricht! 😊 Unsere Experten sind für Sie da. Welches Marketing-Thema beschäftigt Sie?",
    "Das ist eine sehr gute Frage! 🤔 Lassen Sie mich Sie mit einem unserer Spezialisten verbinden.",
    "Perfekt! 🎯 Wir haben bereits vielen Unternehmen in ähnlichen Situationen geholfen. Möchten Sie mehr erfahren?",
    "Interessant! 💡 Wir können Ihnen dabei definitiv helfen. Sollen wir einen kostenlosen Beratungstermin vereinbaren?",
    "Ausgezeichnet! ⭐ Das ist genau unser Spezialgebiet. Lassen Sie uns besprechen, wie wir Ihnen helfen können."
  ],
  en: [
    "Thank you for your message! 😊 Our experts are here for you. Which marketing topic is on your mind?",
    "Great question! 🤔 Let me connect you with one of our specialists.",
    "Perfect! 🎯 We've helped many businesses in similar situations. Want to learn more?",
    "Interesting! 💡 We can definitely assist with that. Shall we schedule a free consultation?",
    "Excellent! ⭐ That's exactly our area of expertise. Let's discuss how we can help you."
  ],
  ua: [
    "Дякуємо за ваше повідомлення! 😊 Наші експерти готові допомогти. Яка тема маркетингу вас цікавить?",
    "Чудове запитання! 🤔 Дозвольте з'єднати вас з одним із наших спеціалістів.",
    "Відмінно! 🎯 Ми вже допомогли багатьом компаніям у схожих ситуаціях. Бажаєте дізнатися більше?",
    "Цікаво! 💡 Ми точно можемо вам допомогти. Чи призначимо безкоштовну консультацію?",
    "Чудово! ⭐ Це саме наша спеціалізація. Давайте обговоримо, як ми можемо вам допомогти."
  ],
  ru: [
    "Спасибо за ваше сообщение! 😊 Наши эксперты готовы помочь. Какая тема маркетинга вас интересует?",
    "Отличный вопрос! 🤔 Позвольте соединить вас с одним из наших специалистов.",
    "Прекрасно! 🎯 Мы уже помогли многим компаниям в подобных ситуациях. Хотите узнать больше?",
    "Интересно! 💡 Мы определенно можем вам помочь. Назначим бесплатную консультацию?",
    "Отлично! ⭐ Это как раз наша специализация. Давайте обсудим, как мы можем вам помочь."
  ],
  pl: [
    "Dziękujemy za wiadomość! 😊 Nasi eksperci są do Twojej dyspozycji. Jaki temat marketingowy Cię interesuje?",
    "Świetne pytanie! 🤔 Połączę Cię z jednym z naszych specjalistów.",
    "Doskonale! 🎯 Pomogliśmy już wielu firmom w podobnych sytuacjach. Chcesz dowiedzieć się więcej?",
    "Interesujące! 💡 Z pewnością możemy Ci pomóc. Czy umówimy darmową konsultację?",
    "Świetnie! ⭐ To dokładnie nasza specjalność. Porozmawiajmy, jak możemy Ci pomóc."
  ]
};

function getChatResponse(lang) {
  const responses = CHAT_PROMPTS[lang] || CHAT_PROMPTS.de;
  return responses[Math.floor(Math.random() * responses.length)];
}
