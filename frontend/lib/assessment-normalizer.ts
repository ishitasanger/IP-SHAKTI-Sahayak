import {
  AssessmentResult,
  LegalReport,
  IPAssessment,
  RegulatoryAssessment,
  TKDLAssessment,
  ABSAssessment,
  Roadmap,
  SearchQueryPlan,
  SourceCitation,
  CheckItem,
} from './types'

function normalizeEvidence(evidence: unknown): SourceCitation[] {
  if (!Array.isArray(evidence)) return []
  return evidence.map((item) => {
    if (!item || typeof item !== 'object') {
      const textVal = String(item ?? '')
      return {
        document: textVal ? 'Legal Evidence' : 'Reference',
        text: textVal,
      }
    }
    const ev = item as Record<string, unknown>
    const doc = (ev.document || ev.source || ev.source_file || 'Legal Evidence') as string
    return {
      ...ev,
      document: doc,
      source: (ev.source || doc) as string,
      source_file: (ev.source_file || '') as string,
      source_url: (ev.source_url || null) as string | null,
      section: ev.section as string | undefined,
      page: ev.page as string | number | undefined,
      score: typeof ev.score === 'number' ? ev.score : undefined,
      text: typeof ev.text === 'string' ? ev.text : String(ev.text ?? ''),
    }
  })
}

function normalizeSearchQueries(queries: unknown): SearchQueryPlan[] {
  if (!Array.isArray(queries)) return []
  return queries.map((item) => {
    if (!item || typeof item !== 'object') {
      const textVal = String(item ?? '')
      return {
        domain: 'IP',
        query: textVal,
        query_text: textVal,
      }
    }
    const q = item as Record<string, unknown>
    const queryText = String(q.query_text ?? q.query ?? '')
    const queryType = String(q.query_type ?? '')
    const ragDomain = String(q.rag_domain ?? '')
    const domain = String(q.domain ?? (ragDomain ? ragDomain : '') ?? (queryType ? queryType.replace(/_/g, ' ') : '') ?? 'IP')
    const description = String(q.description ?? (queryType ? queryType.replace(/_/g, ' ') : ''))

    return {
      ...q,
      query_type: queryType || undefined,
      query_text: queryText,
      rag_domain: ragDomain || undefined,
      domain: domain || 'IP',
      query: queryText,
      description: description || undefined,
    }
  })
}

function normalizeIpAssessment(ip: unknown): IPAssessment | undefined {
  if (!ip || typeof ip !== 'object') return undefined
  const raw = ip as Record<string, unknown>
  return {
    ...raw,
    product_name: typeof raw.product_name === 'string' ? raw.product_name : undefined,
    relevant_ip_domains: Array.isArray(raw.relevant_ip_domains)
      ? raw.relevant_ip_domains.filter((d): d is string => typeof d === 'string')
      : [],
    search_queries: normalizeSearchQueries(raw.search_queries),
    legal_evidence: normalizeEvidence(raw.legal_evidence),
    evidence_count: typeof raw.evidence_count === 'number' ? raw.evidence_count : (Array.isArray(raw.legal_evidence) ? raw.legal_evidence.length : 0),
    legal_considerations: Array.isArray(raw.legal_considerations)
      ? raw.legal_considerations.filter((c): c is string => typeof c === 'string')
      : [],
    screening_status: typeof raw.screening_status === 'string' ? raw.screening_status : undefined,
    summary: typeof raw.summary === 'string' ? raw.summary : undefined,
    disclaimer: typeof raw.disclaimer === 'string' ? raw.disclaimer : undefined,
  }
}

function normalizeChecks(checks: unknown): Record<string, CheckItem> | undefined {
  if (!checks || typeof checks !== 'object') return undefined
  const result: Record<string, CheckItem> = {}
  for (const [key, val] of Object.entries(checks as Record<string, unknown>)) {
    if (val && typeof val === 'object') {
      const item = val as Record<string, unknown>
      const citations = normalizeEvidence(item.sources || item.evidence)
      result[key] = {
        status: String(item.status || 'Review'),
        evidence: citations,
        sources: citations,
      }
    }
  }
  return result
}

function normalizeRegulatoryAssessment(reg: unknown): RegulatoryAssessment | undefined {
  if (!reg || typeof reg !== 'object') return undefined
  const raw = reg as Record<string, unknown>
  const citations = normalizeEvidence(raw.sources || raw.general_evidence)
  return {
    ...raw,
    overall_status: typeof raw.overall_status === 'string' ? raw.overall_status : undefined,
    checks: normalizeChecks(raw.checks),
    general_evidence: citations,
    sources: citations,
    llm_answer: typeof raw.llm_answer === 'string' ? raw.llm_answer : undefined,
    disclaimer: typeof raw.disclaimer === 'string' ? raw.disclaimer : undefined,
  }
}

function normalizeTkdlAssessment(tkdl: unknown): TKDLAssessment | undefined {
  if (!tkdl || typeof tkdl !== 'object') return undefined
  const raw = tkdl as Record<string, unknown>
  const citations = normalizeEvidence(raw.sources || raw.general_evidence)
  return {
    ...raw,
    overall_status: typeof raw.overall_status === 'string' ? raw.overall_status : undefined,
    checks: normalizeChecks(raw.checks),
    general_evidence: citations,
    sources: citations,
    llm_answer: typeof raw.llm_answer === 'string' ? raw.llm_answer : undefined,
    disclaimer: typeof raw.disclaimer === 'string' ? raw.disclaimer : undefined,
  }
}

function normalizeAbsAssessment(abs: unknown): ABSAssessment | undefined {
  if (!abs || typeof abs !== 'object') return undefined
  const raw = abs as Record<string, unknown>
  const citations = normalizeEvidence(raw.sources || raw.general_evidence)
  return {
    ...raw,
    overall_status: typeof raw.overall_status === 'string' ? raw.overall_status : undefined,
    checks: normalizeChecks(raw.checks),
    general_evidence: citations,
    sources: citations,
    llm_answer: typeof raw.llm_answer === 'string' ? raw.llm_answer : undefined,
    disclaimer: typeof raw.disclaimer === 'string' ? raw.disclaimer : undefined,
  }
}

export function normalizeAssessment(payload: Record<string, unknown>): AssessmentResult {
  if (!payload || typeof payload !== 'object') {
    return {}
  }

  const report = payload.legal_report as Record<string, unknown> | undefined
  const source = report && typeof report === 'object' ? report : payload

  const ip_assessment = normalizeIpAssessment(source.ip_assessment)
  const regulatory_assessment = normalizeRegulatoryAssessment(source.regulatory_assessment)
  const tkdl_assessment = normalizeTkdlAssessment(source.tkdl_assessment)
  const abs_assessment = normalizeAbsAssessment(source.abs_assessment)
  const roadmap = (payload.roadmap || source.roadmap) as Roadmap | undefined

  const legal_report: LegalReport = {
    product_context: (source.product_context as Record<string, unknown>) || undefined,
    ip_assessment,
    regulatory_assessment,
    tkdl_assessment,
    abs_assessment,
  }

  return {
    legal_report,
    product_context: source.product_context as Record<string, unknown> | undefined,
    ip_assessment,
    regulatory_assessment,
    tkdl_assessment,
    abs_assessment,
    roadmap,
  }
}

export function hasAssessment(result?: AssessmentResult | null): boolean {
  if (!result) return false
  return Boolean(
    result.ip_assessment ||
    result.regulatory_assessment ||
    result.tkdl_assessment ||
    result.abs_assessment ||
    result.legal_report
  )
}

export function getAssessmentSection<K extends keyof AssessmentResult>(
  result: AssessmentResult | null | undefined,
  key: K
): AssessmentResult[K] | null {
  const section = result?.[key]
  return section && typeof section === 'object' ? section : null
}
