import { generateText } from 'ai'
import { gateway } from '@ai-sdk/gateway'

export async function POST(request: Request) {
  try {
    const body = await request.json()
    const message = typeof body?.message === 'string' ? body.message.trim() : ''
    if (!message || message.length > 1200) return Response.json({ error: 'Please provide a question under 1,200 characters.' }, { status: 400 })

    const result = await generateText({
      model: gateway('openai/gpt-5-mini'),
      system: 'You are Shakti AI, a warm, concise general innovation guide inside IP Shakti. Answer questions outside the guided IP workflow in plain language. You may explain concepts, terminology, product development, science communication, and general business topics. Do not present yourself as a lawyer, do not give definitive legal or medical advice, and suggest a qualified professional for decisions. Keep responses under 180 words.',
      prompt: message,
      maxOutputTokens: 280,
    })

    return Response.json({ text: result.text })
  } catch {
    return Response.json({ error: 'The assistant is temporarily unavailable.' }, { status: 500 })
  }
}
