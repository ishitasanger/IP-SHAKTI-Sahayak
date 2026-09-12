import { WizardInput, AssessmentResult, ChatRequest, ChatResponse } from './types'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000'

export async function submitAssessment(input: WizardInput): Promise<AssessmentResult> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/assessment`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(input),
    })

    if (!response.ok) {
      let errorDetail = response.statusText
      try {
        const errorData = await response.json()
        if (typeof errorData.detail === 'string') {
          errorDetail = errorData.detail
        } else if (Array.isArray(errorData.detail)) {
          errorDetail = errorData.detail.map((err: { msg?: string }) => err.msg || JSON.stringify(err)).join(', ')
        } else if (errorData.message) {
          errorDetail = errorData.message
        }
      } catch {
        // use fallback statusText
      }
      throw new Error(`Assessment failed (${response.status}): ${errorDetail}`)
    }

    return await response.json()
  } catch (error) {
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error(`Could not connect to backend server at ${API_BASE_URL}. Please ensure the backend is running.`)
    }
    throw error
  }
}

export async function askAssessmentQuestion(request: ChatRequest): Promise<ChatResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    })

    if (!response.ok) {
      let errorDetail = response.statusText
      try {
        const errorData = await response.json()
        if (typeof errorData.detail === 'string') {
          errorDetail = errorData.detail
        } else if (errorData.message) {
          errorDetail = errorData.message
        }
      } catch {
        // fallback
      }
      throw new Error(`Chat failed (${response.status}): ${errorDetail}`)
    }

    return await response.json()
  } catch (error) {
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error(`Could not reach chat server at ${API_BASE_URL}. Please ensure the backend is running.`)
    }
    throw error
  }
}
