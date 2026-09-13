import {
  AssessmentResult,
  LegalReport,
  IPAssessment,
  RegulatoryAssessment,
  TKDLAssessment,
  ABSAssessment,
  Roadmap,
  RoadmapAction,
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

export function extractNextStep(text?: string): {
  findings: string
  next_step_content?: string
  next_steps?: string[]
} {
  if (!text || typeof text !== 'string') {
    return { findings: '' }
  }

  // Matches any heading or bold 'Next step' / 'Next steps' up to the next heading or end of string
  const nextStepRegex = /(?:^|\n)(?:#{1,4}\s*(?:Recommended\s+|Practical\s+)?Next\s*steps?:?|(?:\*{2}|_{2})(?:Recommended\s+|Practical\s+)?Next\s*steps?:?(?:\*{2}|_{2}):?)\s*\n*([\s\S]*?)(?=(?:\n#{1,4}\s+|\n(?:\*{2}|_{2})[A-Z]|$))/i

  const match = text.match(nextStepRegex)
  if (!match) {
    return { findings: text.trim() }
  }

  const fullMatchedBlock = match[0]
  const nextStepRaw = match[1].trim()
  const findings = text.replace(fullMatchedBlock, '\n\n').trim()

  const items: string[] = []
  const lines = nextStepRaw.split('\n')
  let currentItem = ''

  for (const line of lines) {
    const trimmed = line.trim()
    if (!trimmed) {
      if (currentItem) {
        items.push(currentItem)
        currentItem = ''
      }
      continue
    }
    const bulletMatch = trimmed.match(/^(?:[-*•]|\d+[.)])\s+(.*)$/)
    if (bulletMatch) {
      if (currentItem) items.push(currentItem)
      currentItem = bulletMatch[1]
    } else {
      if (currentItem) {
        currentItem += ' ' + trimmed
      } else {
        currentItem = trimmed
      }
    }
  }
  if (currentItem) items.push(currentItem)

  return {
    findings,
    next_step_content: nextStepRaw || undefined,
    next_steps: items.length > 0 ? items : (nextStepRaw ? [nextStepRaw] : undefined),
  }
}

function normalizeRegulatoryAssessment(reg: unknown): RegulatoryAssessment | undefined {
  if (!reg || typeof reg !== 'object') return undefined
  const raw = reg as Record<string, unknown>
  const citations = normalizeEvidence(raw.sources || raw.general_evidence)
  const rawLlm = typeof raw.llm_answer === 'string' ? raw.llm_answer : ''
  const { findings, next_step_content, next_steps } = extractNextStep(rawLlm)

  return {
    ...raw,
    overall_status: typeof raw.overall_status === 'string' ? raw.overall_status : undefined,
    checks: normalizeChecks(raw.checks),
    general_evidence: citations,
    sources: citations,
    // llm_answer contains ONLY assessment findings without any next-step block
    llm_answer: findings || undefined,
    findings: findings || undefined,
    next_step_content: next_step_content || undefined,
    next_steps: next_steps || undefined,
    disclaimer: typeof raw.disclaimer === 'string' ? raw.disclaimer : undefined,
  }
}

function normalizeTkdlAssessment(tkdl: unknown): TKDLAssessment | undefined {
  if (!tkdl || typeof tkdl !== 'object') return undefined
  const raw = tkdl as Record<string, unknown>
  const citations = normalizeEvidence(raw.sources || raw.general_evidence)
  const rawLlm = typeof raw.llm_answer === 'string' ? raw.llm_answer : ''
  const { findings, next_step_content, next_steps } = extractNextStep(rawLlm)

  return {
    ...raw,
    overall_status: typeof raw.overall_status === 'string' ? raw.overall_status : undefined,
    checks: normalizeChecks(raw.checks),
    general_evidence: citations,
    sources: citations,
    llm_answer: findings || undefined,
    findings: findings || undefined,
    next_step_content: next_step_content || undefined,
    next_steps: next_steps || undefined,
    disclaimer: typeof raw.disclaimer === 'string' ? raw.disclaimer : undefined,
  }
}

function normalizeAbsAssessment(abs: unknown): ABSAssessment | undefined {
  if (!abs || typeof abs !== 'object') return undefined
  const raw = abs as Record<string, unknown>
  const citations = normalizeEvidence(raw.sources || raw.general_evidence)
  const rawLlm = typeof raw.llm_answer === 'string' ? raw.llm_answer : ''
  const { findings, next_step_content, next_steps } = extractNextStep(rawLlm)

  return {
    ...raw,
    overall_status: typeof raw.overall_status === 'string' ? raw.overall_status : undefined,
    checks: normalizeChecks(raw.checks),
    general_evidence: citations,
    sources: citations,
    // llm_answer contains ONLY assessment findings without any next-step block
    llm_answer: findings || undefined,
    findings: findings || undefined,
    next_step_content: next_step_content || undefined,
    next_steps: next_steps || undefined,
    disclaimer: typeof raw.disclaimer === 'string' ? raw.disclaimer : undefined,
  }
}

function normalizeRoadmap(
  rawRoadmap: unknown,
  regulatory?: RegulatoryAssessment,
  abs?: ABSAssessment,
  ip?: IPAssessment,
  tkdl?: TKDLAssessment
): Roadmap | undefined {
  const raw = rawRoadmap && typeof rawRoadmap === 'object' ? (rawRoadmap as Record<string, unknown>) : {}
  const rawActions = Array.isArray(raw.actions) ? (raw.actions as Record<string, unknown>[]) : []

  const actions: RoadmapAction[] = []
  let foundRegulatory = false
  let foundAbs = false

  for (const item of rawActions) {
    if (!item || typeof item !== 'object') continue
    const domain = String(item.domain || '').toLowerCase()
    const actionType = String(item.action_type || '').toLowerCase()
    const citations = normalizeEvidence(item.sources || item.evidence)
    const priority = typeof item.priority === 'number' ? item.priority : actions.length + 1

    if (domain === 'regulatory' || actionType.includes('regulatory') || actionType.includes('licensing')) {
      foundRegulatory = true
      const regSteps = regulatory?.next_steps || []
      actions.push({
        priority,
        domain: 'regulatory',
        action: typeof item.action === 'string' ? item.action : 'Regulatory licensing and compliance',
        action_type: typeof item.action_type === 'string' ? item.action_type : 'regulatory_licensing',
        answer: typeof item.answer === 'string' ? item.answer : regulatory?.next_step_content,
        next_steps: regSteps.length > 0 ? regSteps : (regulatory?.next_step_content ? [regulatory.next_step_content] : undefined),
        evidence: citations.length > 0 ? citations : (regulatory?.sources || regulatory?.general_evidence),
        sources: citations.length > 0 ? citations : regulatory?.sources,
        human_escalation: Boolean(item.human_escalation ?? true),
        origin: 'Regulatory FitCheck Model',
      })
    } else if (domain === 'abs' || actionType.includes('abs') || actionType.includes('benefit')) {
      foundAbs = true
      const absSteps = abs?.next_steps || []
      actions.push({
        priority,
        domain: 'abs',
        action: typeof item.action === 'string' ? item.action : 'Access & Benefit Sharing (ABS) compliance',
        action_type: typeof item.action_type === 'string' ? item.action_type : 'abs_compliance',
        answer: typeof item.answer === 'string' ? item.answer : abs?.next_step_content,
        next_steps: absSteps.length > 0 ? absSteps : (abs?.next_step_content ? [abs.next_step_content] : undefined),
        evidence: citations.length > 0 ? citations : (abs?.sources || abs?.general_evidence),
        sources: citations.length > 0 ? citations : abs?.sources,
        human_escalation: Boolean(item.human_escalation ?? true),
        origin: 'Biological Diversity Act Model',
      })
    } else {
      // IP actions (e.g. patent, trademark, design)
      const ipActionType = actionType
      let ipSteps: string[] | undefined = undefined
      if (ip?.search_queries && ip.search_queries.length > 0) {
        if (ipActionType.includes('patent')) {
          const patentQueries = ip.search_queries.filter(
            (q) => (q.domain || '').toLowerCase().includes('patent') || (q.rag_domain || '').toLowerCase().includes('patent')
          )
          if (patentQueries.length > 0) {
            ipSteps = patentQueries.map(
              (q) => `Execute prior-art patent search: "${q.query_text || q.query}" (${q.description || 'IPO database'})`
            )
          }
        } else if (ipActionType.includes('trademark')) {
          const tmQueries = ip.search_queries.filter(
            (q) => (q.domain || '').toLowerCase().includes('trademark') || (q.rag_domain || '').toLowerCase().includes('trademark')
          )
          if (tmQueries.length > 0) {
            ipSteps = tmQueries.map(
              (q) => `Conduct trademark registry search: "${q.query_text || q.query}" (${q.description || 'Class 5 classification'})`
            )
          }
        }
      }

      actions.push({
        priority,
        domain: domain || 'ip',
        action: typeof item.action === 'string' ? item.action : 'IP Protection Pathway',
        action_type: typeof item.action_type === 'string' ? item.action_type : 'ip_action',
        answer: typeof item.answer === 'string' ? item.answer : undefined,
        next_steps: ipSteps,
        evidence: citations,
        sources: citations,
        human_escalation: Boolean(item.human_escalation),
        origin: domain === 'ip' ? 'IP Screening Model' : 'Assessment Engine',
      })
    }
  }

  // If Regulatory had extracted next steps but was not already included in actions, append it
  if (!foundRegulatory && regulatory?.next_step_content) {
    actions.push({
      priority: 3,
      domain: 'regulatory',
      action: 'Regulatory licensing and compliance',
      action_type: 'regulatory_licensing',
      answer: regulatory.next_step_content,
      next_steps: regulatory.next_steps,
      evidence: regulatory.sources || regulatory.general_evidence,
      sources: regulatory.sources,
      human_escalation: true,
      origin: 'Regulatory FitCheck Model',
    })
  }

  // If ABS had extracted next steps but was not already included in actions, append it
  if (!foundAbs && abs?.next_step_content) {
    actions.push({
      priority: 4,
      domain: 'abs',
      action: 'Access & Benefit Sharing (ABS) compliance',
      action_type: 'abs_compliance',
      answer: abs.next_step_content,
      next_steps: abs.next_steps,
      evidence: abs.sources || abs.general_evidence,
      sources: abs.sources,
      human_escalation: true,
      origin: 'Biological Diversity Act Model',
    })
  }

  // Sort by priority and ensure 1, 2, 3...
  actions.sort((a, b) => a.priority - b.priority)
  actions.forEach((act, idx) => {
    act.priority = idx + 1
  })

  return {
    status: actions.length > 0 ? (typeof raw.status === 'string' ? raw.status : 'Action plan generated') : 'No immediate action identified',
    actions,
    disclaimer:
      typeof raw.disclaimer === 'string'
        ? raw.disclaimer
        : 'This roadmap consolidates next steps and statutory guidance derived from the assessment models.',
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
  const roadmap = normalizeRoadmap(
    payload.roadmap || source.roadmap,
    regulatory_assessment,
    abs_assessment,
    ip_assessment,
    tkdl_assessment
  )

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
