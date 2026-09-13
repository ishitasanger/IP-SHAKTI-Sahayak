export type WizardInput = {
  product_name: string
  product_description?: string
  jurisdiction: string
  product_type:
    | 'ayurvedic medicine'
    | 'herbal medicine'
    | 'nutraceutical'
    | 'food product'
    | 'dietary supplement'
    | 'cosmetic'
    | 'personal care product'
    | 'other'
  classification:
    | 'classical / traditional formulation'
    | 'proprietary formulation'
    | 'single ingredient product'
    | 'multi-ingredient formulation'
    | 'not sure'
  form?: string
  ingredients: string[]
  intended_use: string
  claims: string[]
  innovation_description?: string
  traditional_knowledge: 'yes' | 'no' | 'not sure'
  traditional_knowledge_source?: string
  uses_biological_resources: 'yes' | 'no' | 'not sure'
  biological_resources: string[]
  manufacturing_location?: string
  commercial_use: boolean
}

export type SourceCitation = {
  document?: string
  source?: string
  section?: string
  page?: string | number
  source_file?: string
  source_url?: string | null
  text?: string
  score?: number
  query_type?: string
  domain?: string
  [key: string]: unknown
}

export type SearchQueryPlan = {
  domain?: string
  query?: string
  description?: string
  query_type?: string
  query_text?: string
  rag_domain?: string
  [key: string]: unknown
}

export type IPAssessment = {
  product_name?: string
  relevant_ip_domains?: string[]
  search_queries?: SearchQueryPlan[]
  legal_evidence?: SourceCitation[]
  evidence_count?: number
  legal_considerations?: string[]
  screening_status?: string
  summary?: string
  disclaimer?: string
  [key: string]: unknown
}

export type CheckItem = {
  status: string
  evidence: SourceCitation[]
  sources?: SourceCitation[]
  [key: string]: unknown
}

export type RegulatoryAssessment = {
  overall_status?: string
  checks?: Record<string, CheckItem>
  general_evidence?: SourceCitation[]
  sources?: SourceCitation[]
  llm_answer?: string
  disclaimer?: string
  [key: string]: unknown
}

export type TKDLAssessment = {
  overall_status?: string
  checks?: Record<string, CheckItem>
  general_evidence?: SourceCitation[]
  sources?: SourceCitation[]
  llm_answer?: string
  disclaimer?: string
  [key: string]: unknown
}

export type ABSAssessment = {
  overall_status?: string
  checks?: Record<string, CheckItem>
  general_evidence?: SourceCitation[]
  sources?: SourceCitation[]
  llm_answer?: string
  disclaimer?: string
  [key: string]: unknown
}

export type RoadmapAction = {
  priority: number
  domain: string
  action: string
  action_type: string
  evidence?: SourceCitation[]
  human_escalation?: boolean
  query?: string
}

export type Roadmap = {
  status?: string
  actions?: RoadmapAction[]
  disclaimer?: string
  [key: string]: unknown
}

export type LegalReport = {
  product_context?: Record<string, unknown>
  ip_assessment?: IPAssessment
  regulatory_assessment?: RegulatoryAssessment
  tkdl_assessment?: TKDLAssessment
  abs_assessment?: ABSAssessment
  [key: string]: unknown
}

export type AssessmentResult = {
  legal_report?: LegalReport
  product_context?: Record<string, unknown>
  ip_assessment?: IPAssessment
  regulatory_assessment?: RegulatoryAssessment
  tkdl_assessment?: TKDLAssessment
  abs_assessment?: ABSAssessment
  roadmap?: Roadmap
  [key: string]: unknown
}

export type ChatRequest = {
  question: string
  product_context?: Record<string, unknown>
  legal_report?: Record<string, unknown>
  roadmap?: Record<string, unknown>
  chat_history?: Array<{
    role: 'user' | 'assistant'
    content: string
  }>
}

export type ChatResponse = {
  answer: string
  sources?: SourceCitation[]
}

export type Jurisdiction = {
  id: string
  name: string
  code: string
  region: string
}
