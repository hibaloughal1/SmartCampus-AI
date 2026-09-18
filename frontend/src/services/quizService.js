import api from './api'

export async function generateQuiz(documentId, topic, numQuestions) {
  const { data } = await api.post('/quiz/generate', {
    document_id: documentId,
    topic,
    num_questions: numQuestions,
  })
  return data
}

export async function listQuizzes() {
  const { data } = await api.get('/quiz')
  return data
}

export async function generateFlashcards(documentId, topic, numCards) {
  const { data } = await api.post('/flashcards/generate', {
    document_id: documentId,
    topic,
    num_cards: numCards,
  })
  return data
}

export async function listFlashcardSets() {
  const { data } = await api.get('/flashcards')
  return data
}
