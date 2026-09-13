// app/server/api/syne/chat.ts
import { SYNE_SYSTEM_PROMPT } from '~~/config/syne-persona'

export default defineEventHandler(async (event) => {
  const body = await readBody(event)

  // Ajouter le message système au début de la conversation
  const messagesWithSystem = [
    { role: 'system', content: SYNE_SYSTEM_PROMPT },
    ...(body.messages || [])
  ]

  // Transmettre au gateway Nginx (qui lui-même renvoie vers llama.cpp)
  const response = await fetch('http://nginx-gateway/api/syne/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(event.headers.get('authorization') && {
        authorization: event.headers.get('authorization')!
      })
    },
    body: JSON.stringify({ messages: messagesWithSystem })
  })

  const data = await response.json()
  return data
})