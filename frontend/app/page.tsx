'use client'

import { useMemo, useState } from 'react'
import {
  AlertTriangle,
  ArrowRight,
  BookOpen,
  Check,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  ExternalLink,
  FileText,
  Globe2,
  HelpCircle,
  Leaf,
  MessageCircle,
  Plus,
  RefreshCw,
  Search,
  ShieldCheck,
  Sparkles,
  Trash2,
  X,
} from 'lucide-react'
import { ComposableMap, Geographies, Geography, ZoomableGroup } from 'react-simple-maps'
import { askAssessmentQuestion, submitAssessment } from '@/lib/ip-shakti-api'
import type {
  AssessmentResult,
  ChatRequest,
  Jurisdiction,
  RoadmapAction,
  SourceCitation,
  WizardInput,
} from '@/lib/types'
import { hasAssessment, normalizeAssessment } from '@/lib/assessment-normalizer'

import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

const logoUrl =
  'https://hebbkx1anhila5yf.public.blob.vercel-storage.com/image-dhzBUh0TYQLc7qqvRBtpq4moRo1TUQ.png'
const geoUrl = 'https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json'

const jurisdictions: Jurisdiction[] = [
  { id: 'india', name: 'India', code: 'IN', region: 'South Asia' },
  { id: 'us', name: 'United States', code: 'US', region: 'North America' },
  { id: 'uk', name: 'United Kingdom', code: 'UK', region: 'Europe' },
  { id: 'eu', name: 'European Union', code: 'EU', region: 'Europe' },
  { id: 'japan', name: 'Japan', code: 'JP', region: 'East Asia' },
  { id: 'australia', name: 'Australia', code: 'AU', region: 'Oceania' },
  { id: 'asean', name: 'ASEAN', code: 'AS', region: 'Southeast Asia' },
]

const initialInput: WizardInput = {
  product_name: '',
  product_description: '',
  jurisdiction: 'India',
  product_type: 'ayurvedic medicine',
  classification: 'proprietary formulation',
  form: 'capsule',
  ingredients: ['Ashwagandha', 'Brahmi'],
  intended_use: 'Stress relief and mental wellness',
  claims: ['Supports stress resilience', 'Promotes calmness'],
  innovation_description: 'Synergistic herbal blend with standardized extract concentration',
  traditional_knowledge: 'yes',
  traditional_knowledge_source: 'Charaka Samhita',
  uses_biological_resources: 'yes',
  biological_resources: ['Ashwagandha', 'Brahmi'],
  manufacturing_location: 'Kerala, India',
  commercial_use: true,
}

const stages = [
  'Formulation Input',
  'Jurisdiction',
  'Classification',
  'IP Screening',
  'Regulatory Assessment',
  'TKDL Screening',
  'ABS Screening',
  'Action Roadmap',
  'Executive Summary',
]

function Brand() {
  return (
    <div className="brand">
      <img src={logoUrl} alt="IP Shakti logo" />
      <div>
        <strong>IP Shakti</strong>
        <span>Intelligent IP for India</span>
      </div>
    </div>
  )
}

function Sidebar({
  active,
  onChange,
}: {
  active: string
  onChange: (value: string) => void
}) {
  return (
    <aside className="sidebar">
      <Brand />
      <nav>
        {['Dashboard', 'New Assessment', 'My Analyses', 'Ask IP Shakti', 'Knowledge Base'].map(
          (item) => (
            <button
              key={item}
              className={active === item ? 'nav-item active' : 'nav-item'}
              onClick={() => onChange(item)}
            >
              <span className="nav-dot" />
              {item}
            </button>
          )
        )}
      </nav>
      <div className="sidebar-note">
        <Leaf size={16} />
        <span>
          Nature-led intelligence
          <br />
          for ambitious ideas.
        </span>
      </div>
      <div className="profile">
        <div className="avatar">AS</div>
        <div>
          <strong>Dr. A. Sharma</strong>
          <span>Innovator workspace</span>
        </div>
      </div>
    </aside>
  )
}

function Header() {
  return (
    <header className="topbar">
      <div className="mobile-brand">
        <Brand />
      </div>
      <div className="topbar-right">
        <span className="status-dot" /> Live backend connected{' '}
        <div className="top-avatar">AS</div>
      </div>
    </header>
  )
}

function Disclaimer() {
  return (
    <div className="disclaimer">
      <ShieldCheck size={15} />
      <span>
        This assistant provides source-grounded informational guidance and does not constitute
        legal or medical advice.
      </span>
    </div>
  )
}

function Progress({ current }: { current: number }) {
  return (
    <div className="workflow">
      <span className="workflow-label">YOUR ASSESSMENT JOURNEY</span>
      <div className="stepper">
        {stages.map((stage, index) => (
          <div
            className={
              index === current ? 'step active' : index < current ? 'step done' : 'step'
            }
            key={stage}
          >
            <span className="step-marker">
              {index < current ? <Check size={12} /> : index + 1}
            </span>
            <span>{stage}</span>
            {index < stages.length - 1 && <i className="step-line" />}
          </div>
        ))}
      </div>
    </div>
  )
}

function SectionIntro({
  eyebrow,
  title,
  text,
}: {
  eyebrow: string
  title: React.ReactNode
  text: string
}) {
  return (
    <div className="screen-intro">
      <span className="eyebrow small">{eyebrow}</span>
      <h1>{title}</h1>
      <p>{text}</p>
    </div>
  )
}

function TagList({
  items,
  setItems,
  placeholder,
}: {
  items: string[]
  setItems: (items: string[]) => void
  placeholder: string
}) {
  const [value, setValue] = useState('')
  const add = () => {
    if (value.trim()) {
      setItems([...items, value.trim()])
      setValue('')
    }
  }
  return (
    <div className="tag-editor">
      <div className="tag-list">
        {items.map((item, i) => (
          <span className="tag" key={`${item}-${i}`}>
            {item}
            <button
              onClick={() => setItems(items.filter((_, index) => index !== i))}
              aria-label={`Remove ${item}`}
            >
              <X size={12} />
            </button>
          </span>
        ))}
      </div>
      <div className="tag-input">
        <input
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              e.preventDefault()
              add()
            }
          }}
          placeholder={placeholder}
        />
        <button type="button" onClick={add} aria-label="Add item">
          <Plus size={15} />
        </button>
      </div>
    </div>
  )
}

function Question({
  title,
  value,
  options,
  onChange,
}: {
  title: string
  value: string
  options: string[]
  onChange: (value: string) => void
}) {
  return (
    <fieldset className="question">
      <legend>{title}</legend>
      <div className="option-grid">
        {options.map((option) => (
          <button
            type="button"
            key={option}
            className={value === option ? 'option selected' : 'option'}
            onClick={() => onChange(option)}
          >
            <span className="radio" />
            {option}
          </button>
        ))}
      </div>
    </fieldset>
  )
}

function StateCard({
  title,
  text,
  action,
  onAction,
  loading,
  error,
}: {
  title: string
  text: string
  action?: string
  onAction?: () => void
  loading?: boolean
  error?: boolean
}) {
  return (
    <div className={`state-card ${error ? 'error' : ''}`}>
      <div className={loading ? 'loader' : 'state-icon'}>
        {loading ? '' : error ? '!' : <Globe2 size={20} />}
      </div>
      <h2>{title}</h2>
      <p>{text}</p>
      {action && (
        <button className="continue-button" onClick={onAction}>
          {action} <ArrowRight size={16} />
        </button>
      )}
    </div>
  )
}

/* =========================================================================
   STAGE 1: Formulation Input
   ========================================================================= */
function DetailsStep({
  input,
  setInput,
  next,
  back,
}: {
  input: WizardInput
  setInput: React.Dispatch<React.SetStateAction<WizardInput>>
  next: () => void
  back: () => void
}) {
  const [productStage, setProductStage] = useState('newly developed')
  const update = (patch: Partial<WizardInput>) =>
    setInput((current) => ({ ...current, ...patch }))
  const addIngredient = () => update({ ingredients: [...input.ingredients, ''] })
  const setIngredient = (i: number, value: string) =>
    update({
      ingredients: input.ingredients.map((item, index) =>
        index === i ? value : item
      ),
    })

  return (
    <div className="analysis-screen page-enter">
      <SectionIntro
        eyebrow="STEP 01 / FORMULATION INPUT"
        title={
          <>
            Describe your <em>formulation.</em>
          </>
        }
        text="Provide factual information about your product composition, claims, and intended use to guide the multi-domain assessment."
      />
      <div className="form-card">
        <div className="field-grid">
          <label>
            Product name
            <input
              value={input.product_name}
              onChange={(e) => update({ product_name: e.target.value })}
              placeholder="e.g. Ashwagandha Wellness Blend"
              required
            />
          </label>
          <label>
            Development stage
            <select
              value={productStage}
              onChange={(e) => setProductStage(e.target.value)}
            >
              <option>newly developed</option>
              <option>existing in market</option>
              <option>prototype / formulation stage</option>
            </select>
          </label>
        </div>

        <label>
          Product description
          <textarea
            value={input.product_description || ''}
            onChange={(e) => update({ product_description: e.target.value })}
            placeholder="Describe the formulation, origin, and characteristics in plain language."
          />
        </label>

        <div className="field-grid">
          <label>
            Intended use
            <input
              value={input.intended_use}
              onChange={(e) => update({ intended_use: e.target.value })}
              placeholder="e.g. Stress relief, cognitive wellness, digestive support"
              required
            />
          </label>
          <label>
            Product type
            <select
              value={input.product_type}
              onChange={(e) =>
                update({
                  product_type: e.target.value as WizardInput['product_type'],
                })
              }
            >
              {[
                'ayurvedic medicine',
                'herbal medicine',
                'nutraceutical',
                'food product',
                'dietary supplement',
                'cosmetic',
                'personal care product',
                'other',
              ].map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </label>
        </div>

        <label>
          Product form
          <input
            value={input.form || ''}
            onChange={(e) => update({ form: e.target.value })}
            placeholder="Tablet, capsule, powder, oil, syrup, cream…"
          />
        </label>

        <div className="form-section">
          <div className="table-head">
            <div>
              <span className="eyebrow small">COMPOSITION</span>
              <h3>Ingredients</h3>
            </div>
            <button className="outline-button" onClick={addIngredient}>
              <Plus size={15} /> Add ingredient
            </button>
          </div>
          {input.ingredients.map((ingredient, i) => (
            <div className="ingredient-input" key={i}>
              <input
                value={ingredient}
                onChange={(e) => setIngredient(i, e.target.value)}
                placeholder={`Ingredient ${i + 1}`}
              />
              {input.ingredients.length > 1 && (
                <button
                  onClick={() =>
                    update({
                      ingredients: input.ingredients.filter(
                        (_, index) => index !== i
                      ),
                    })
                  }
                  aria-label="Remove ingredient"
                >
                  <Trash2 size={15} />
                </button>
              )}
            </div>
          ))}
        </div>

        <label>
          Claims or therapeutic indications
          <TagList
            items={input.claims}
            setItems={(claims) => update({ claims })}
            placeholder="Add claim (e.g. Relieves stress) and press Enter"
          />
        </label>

        <label>
          Innovation description
          <textarea
            value={input.innovation_description || ''}
            onChange={(e) => update({ innovation_description: e.target.value })}
            placeholder="What is novel, adapted, or distinctive about this formulation?"
          />
        </label>

        <div className="field-grid">
          <label>
            Manufacturing location
            <input
              value={input.manufacturing_location || ''}
              onChange={(e) =>
                update({ manufacturing_location: e.target.value })
              }
              placeholder="City, state, country (e.g. Kerala, India)"
            />
          </label>
          <label className="toggle-label">
            Commercial use intended
            <input
              type="checkbox"
              checked={input.commercial_use}
              onChange={(e) => update({ commercial_use: e.target.checked })}
            />
            <span className="toggle" />
          </label>
        </div>

        <p className="privacy-note">
          <ShieldCheck size={14} /> Factual information collected here is evaluated against official Indian IP and regulatory knowledge bases.
        </p>

        <div className="screen-footer">
          <button className="back-button" onClick={back}>
            <ChevronLeft size={16} /> Back to dashboard
          </button>
          <button
            className="continue-button"
            onClick={next}
            disabled={!input.product_name.trim() || !input.intended_use.trim()}
          >
            Continue to jurisdiction selection <ArrowRight size={17} />
          </button>
        </div>
      </div>
    </div>
  )
}

/* =========================================================================
   STAGE 3: Guided Classification Step
   ========================================================================= */
function ClassificationStep({
  jurisdiction,
  input,
  setInput,
  onSubmit,
  loading,
  error,
  back,
}: {
  jurisdiction: Jurisdiction
  input: WizardInput
  setInput: React.Dispatch<React.SetStateAction<WizardInput>>
  onSubmit: () => void
  loading: boolean
  error: string
  back: () => void
}) {
  const update = (patch: Partial<WizardInput>) =>
    setInput((current) => ({ ...current, ...patch }))

  const ingredientsCount = input.ingredients.filter((i) => i.trim()).length
  const singleIngredientError =
    input.classification === 'single ingredient product' && ingredientsCount !== 1
  const biologicalError =
    input.uses_biological_resources === 'yes' &&
    input.biological_resources.filter((b) => b.trim()).length === 0

  return (
    <div className="analysis-screen page-enter">
      <SectionIntro
        eyebrow="STEP 03 / GUIDED CLASSIFICATION"
        title={
          <>
            Identity, <em>heritage & origin.</em>
          </>
        }
        text="These questions help the backend map your product against TKDL, Biological Diversity Act (ABS), and Patents Act provisions."
      />

      <div style={{ marginBottom: '16px', display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '7px 14px', background: '#e6f3ef', borderRadius: '8px', fontSize: '12px', color: '#174c49', border: '1px solid #cbe5dc' }}>
        <Globe2 size={15} /> <strong>Active Jurisdiction:</strong> {jurisdiction.name} ({jurisdiction.region})
      </div>

      {loading ? (
        <StateCard
          title="Executing multi-domain assessment"
          text="Running IP screening, Regulatory fit check, TKDL prior-art review, ABS compliance analysis, and roadmap synthesis via FastAPI backend…"
          loading
        />
      ) : error ? (
        <StateCard
          title="Assessment request failed"
          text={error}
          error
          action="Retry assessment"
          onAction={onSubmit}
        />
      ) : (
        <div className="question-stack">
          <Question
            title="How is the formulation classified?"
            value={input.classification}
            options={[
              'classical / traditional formulation',
              'proprietary formulation',
              'single ingredient product',
              'multi-ingredient formulation',
              'not sure',
            ]}
            onChange={(value) =>
              update({ classification: value as WizardInput['classification'] })
            }
          />
          {singleIngredientError && (
            <div className="conditional-field" style={{ background: '#ffd5d5', color: '#851d1d' }}>
              <AlertTriangle size={15} /> A single ingredient product must contain exactly one ingredient. Please adjust your ingredients list.
            </div>
          )}

          <Question
            title="Is this formulation referenced in classical Ayurvedic texts?"
            value={input.traditional_knowledge}
            options={['yes', 'no', 'not sure']}
            onChange={(value) =>
              update({
                traditional_knowledge: value as WizardInput['traditional_knowledge'],
                traditional_knowledge_source:
                  value === 'no' ? '' : input.traditional_knowledge_source,
              })
            }
          />

          {input.traditional_knowledge === 'yes' && (
            <label className="conditional-field">
              Classical text or compendium reference
              <input
                value={input.traditional_knowledge_source || ''}
                onChange={(e) =>
                  update({ traditional_knowledge_source: e.target.value })
                }
                placeholder="e.g. Charaka Samhita, Sushruta Samhita, Ashtanga Hridaya"
              />
            </label>
          )}

          <Question
            title="Does the product use biological resources (herbs, plants, microbes, animal derivatives) sourced from India?"
            value={input.uses_biological_resources}
            options={['yes', 'no', 'not sure']}
            onChange={(value) =>
              update({
                uses_biological_resources:
                  value as WizardInput['uses_biological_resources'],
                biological_resources:
                  value === 'no' ? [] : input.biological_resources,
              })
            }
          />

          {input.uses_biological_resources === 'yes' && (
            <label className="conditional-field">
              List biological resources / botanical species
              <TagList
                items={input.biological_resources}
                setItems={(biological_resources) =>
                  update({ biological_resources })
                }
                placeholder="Add botanical or resource name and press Enter"
              />
            </label>
          )}

          {biologicalError && (
            <div className="conditional-field" style={{ background: '#ffd5d5', color: '#851d1d' }}>
              <AlertTriangle size={15} /> Biological resources are marked &quot;yes&quot;, so at least one biological resource must be listed.
            </div>
          )}

          <div className="screen-footer">
            <button className="back-button" onClick={back}>
              <ChevronLeft size={16} /> Back to jurisdiction selection
            </button>
            <button
              className="continue-button"
              onClick={onSubmit}
              disabled={Boolean(singleIngredientError || biologicalError)}
            >
              Run full assessment <Sparkles size={17} />
            </button>
          </div>
        </div>
      )}
      <Disclaimer />
    </div>
  )
}

/* =========================================================================
   STAGE 4: IP Screening Step
   ========================================================================= */
function IPScreeningStep({
  result,
  next,
  back,
}: {
  result: AssessmentResult | null
  next: () => void
  back: () => void
}) {
  const ip = result?.ip_assessment
  const domains = ip?.relevant_ip_domains || []
  const queries = ip?.search_queries || []
  const considerations = ip?.legal_considerations || []
  const evidence = ip?.legal_evidence || []

  return (
    <div className="analysis-screen page-enter">
      <SectionIntro
        eyebrow="STEP 04 / IP SCREENING"
        title={
          <>
            Intellectual property <em>screening.</em>
          </>
        }
        text="Preliminary identification of relevant IP protection domains, patent novelty barriers, and search strategies grounded in Indian IP law."
      />

      <div className="assessment-layout">
        {/* Status and Domains */}
        <div className="domain-card">
          <div className="domain-header">
            <h3>Screening Status</h3>
            <span className="badge badge-mint">
              {ip?.screening_status || 'Screening complete'}
            </span>
          </div>
          <p style={{ margin: 0, color: 'var(--muted-foreground)', fontSize: '13px' }}>
            {ip?.summary ||
              'IP relevance evaluated across Indian Patent Act 1970 (including Section 3(p) Traditional Knowledge exclusion) and Trade Marks Act 1999.'}
          </p>

          <div style={{ marginTop: '8px' }}>
            <span className="evidence-title">Identified Relevant IP Domains</span>
            <div className="pill-row" style={{ marginTop: '6px' }}>
              {domains.length > 0 ? (
                domains.map((dom, i) => (
                  <span key={dom || i} className="badge badge-teal">
                    {(dom || '').toUpperCase()}
                  </span>
                ))
              ) : (
                <span className="badge badge-neutral">Standard IP assessment</span>
              )}
            </div>
          </div>
        </div>

        {/* Legal Considerations */}
        {considerations.length > 0 && (
          <div className="domain-card">
            <div className="domain-header">
              <h3>Key Legal Considerations</h3>
              <span className="badge badge-amber">STATUTORY SAFEGUARDS</span>
            </div>
            <ul style={{ margin: 0, paddingLeft: '18px', display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '12px', color: 'var(--foreground)' }}>
              {considerations.map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Search Queries Plan */}
        {queries.length > 0 && (
          <div className="domain-card">
            <div className="domain-header">
              <h3>Recommended Search Strategies</h3>
              <span className="badge badge-neutral">{queries.length} QUERIES</span>
            </div>
            <div className="cards-grid">
              {queries.map((q, idx) => {
                const domainLabel = (q.domain || q.rag_domain || q.query_type || 'IP').toUpperCase()
                const queryContent = q.query || q.query_text || ''
                const badgeLabel = q.query_type ? q.query_type.replace(/_/g, ' ') : 'Registry Search'
                const descriptionText = q.description || (q.query_type && q.query_type !== q.domain ? q.query_type.replace(/_/g, ' ') : '')

                return (
                  <div key={idx} className="evidence-card">
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                      <strong>{domainLabel}</strong>
                      <span className="badge badge-mint" style={{ textTransform: 'capitalize' }}>
                        {badgeLabel}
                      </span>
                    </div>
                    {queryContent ? (
                      <code style={{ display: 'block', padding: '6px 8px', background: '#fffdf3', borderRadius: '6px', fontSize: '11px', marginBottom: '6px' }}>
                        {queryContent}
                      </code>
                    ) : null}
                    {descriptionText ? (
                      <span style={{ fontSize: '10px', color: 'var(--muted-foreground)', textTransform: 'capitalize' }}>
                        {descriptionText}
                      </span>
                    ) : null}
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* Legal Evidence & Citations */}
        {evidence.length > 0 && (
          <div className="domain-card">
            <div className="domain-header">
              <h3>Retrieved Legal Evidence</h3>
              <span className="badge badge-mint">{evidence.length} CITATIONS</span>
            </div>
            <div className="evidence-section">
              {evidence.map((ev, idx) => (
                <div key={idx} className="evidence-card">
                  <strong>{ev.document || ev.source || ev.source_file || 'Legal Evidence'}</strong>
                  {ev.text && <p style={{ margin: '4px 0', fontSize: '11px' }}>{ev.text}</p>}
                  <div className="evidence-meta">
                    {ev.section && <span>Section: {ev.section}</span>}
                    {ev.page && <span>Page: {ev.page}</span>}
                    {typeof ev.score === 'number' && (
                      <span>Relevance: {(ev.score * 100).toFixed(0)}%</span>
                    )}
                    {ev.source_url && (
                      <a
                        href={ev.source_url}
                        target="_blank"
                        rel="noreferrer"
                        style={{ color: '#174c49', display: 'inline-flex', alignItems: 'center', gap: '3px' }}
                      >
                        Official Source <ExternalLink size={11} />
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {ip?.disclaimer && (
          <p style={{ fontSize: '11px', color: 'var(--muted-foreground)', fontStyle: 'italic' }}>
            {ip.disclaimer}
          </p>
        )}

        <div className="screen-footer">
          <button className="back-button" onClick={back}>
            <ChevronLeft size={16} /> Back to guided classification
          </button>
          <button className="continue-button" onClick={next}>
            Continue to regulatory assessment <ArrowRight size={17} />
          </button>
        </div>
      </div>
      <Disclaimer />
    </div>
  )
}

/* =========================================================================
   STAGE 2: Jurisdiction Selection Step
   ========================================================================= */
function JurisdictionStep({
  selected,
  setSelected,
  next,
  back,
}: {
  selected: Jurisdiction
  setSelected: (j: Jurisdiction) => void
  next: () => void
  back: () => void
}) {
  const [query, setQuery] = useState('')
  const [compare, setCompare] = useState(false)
  const filtered = jurisdictions.filter((j) =>
    j.name.toLowerCase().includes(query.toLowerCase())
  )

  return (
    <div className="analysis-screen page-enter">
      <SectionIntro
        eyebrow="STEP 02 / JURISDICTION CONTEXT"
        title={
          <>
            Select your <em>target jurisdiction.</em>
          </>
        }
        text="India is the primary regulatory and IP jurisdiction for this analysis. Setting your jurisdiction establishes statutory baseline rules before guided classification and screening."
      />
      <div className="jurisdiction-layout">
        <div className="map-card">
          <div className="map-tools">
            <label className="search-field">
              <Search size={15} />
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search country or region"
                aria-label="Search jurisdiction"
              />
            </label>
            <div className="zoom-controls">
              <button aria-label="Zoom out">−</button>
              <button aria-label="Zoom in">+</button>
            </div>
          </div>
          <div className="world-map">
            <ComposableMap
              projectionConfig={{ scale: 145 }}
              aria-label="Interactive world map"
            >
              <ZoomableGroup>
                <Geographies geography={geoUrl}>
                  {({ geographies }) =>
                    geographies.map((geo) => {
                      const isIndia = geo.properties?.name === 'India'
                      return (
                        <Geography
                          key={geo.rsmKey}
                          geography={geo}
                          tabIndex={0}
                          role="button"
                          aria-label={`Select ${geo.properties?.name || 'Country'}`}
                          onClick={() => isIndia && setSelected(jurisdictions[0])}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter' && isIndia) setSelected(jurisdictions[0])
                          }}
                          style={
                            {
                              default: {
                                fill: isIndia ? '#4a9181' : '#d9dfca',
                                outline: 'none',
                              },
                              hover: { fill: '#a8e16e', outline: 'none' },
                              pressed: { fill: '#174c49', outline: 'none' },
                            } as unknown as React.CSSProperties
                          }
                        />
                      )
                    })
                  }
                </Geographies>
              </ZoomableGroup>
            </ComposableMap>
          </div>
          <p className="map-caption">
            <Globe2 size={14} /> India is active. Applicable statutes: Patents Act 1970, Biological Diversity Act 2002, Drugs & Cosmetics Act.
          </p>
        </div>

        <div className="jurisdiction-side">
          <div className="selected-context">
            <div className="context-top">
              <span className="country-code">{selected.code}</span>
              <span className="status mint">Primary Jurisdiction</span>
            </div>
            <h2>{selected.name}</h2>
            <p>
              {selected.region} · Applied Indian statutory framework: Patents Act Section 3(p), National Biodiversity Authority (NBA) approval, and AYUSH licensing guidelines.
            </p>
            <button className="text-button" onClick={() => setQuery('')}>
              Change jurisdiction <ChevronRight size={15} />
            </button>
          </div>

          <span className="eyebrow small">QUICK SELECT</span>
          <div className="quick-grid">
            {filtered.map((j) => (
              <button
                key={j.id}
                className={
                  selected.id === j.id ? 'quick-card selected' : 'quick-card'
                }
                onClick={() => setSelected(j)}
              >
                <strong>{j.code}</strong>
                <span>{j.name}</span>
              </button>
            ))}
          </div>

          <button
            className="compare-toggle"
            onClick={() => setCompare(!compare)}
          >
            {compare ? <Check size={15} /> : <Plus size={15} />} Compare jurisdictions
          </button>
          {compare && (
            <div className="compare-panel">
              <div>
                <strong>{selected.name} (Active)</strong>
                <span>Full Ayurveda, TKDL & ABS pipeline enabled</span>
              </div>
              <div>
                <strong>US / EU (Export)</strong>
                <span>Dietary supplement / botanical drug classification rules apply</span>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="screen-footer">
        <button className="back-button" onClick={back}>
          <ChevronLeft size={16} /> Back to formulation details
        </button>
        <button className="continue-button" onClick={next}>
          Continue to guided classification <ArrowRight size={17} />
        </button>
      </div>
      <Disclaimer />
    </div>
  )
}

function renderChecks(
  checks?: Record<string, { status: string; evidence?: SourceCitation[]; sources?: SourceCitation[] }>
) {
  if (!checks || Object.keys(checks).length === 0) {
    return (
      <p style={{ color: 'var(--muted-foreground)', fontSize: '12px' }}>
        No specific category checks returned.
      </p>
    )
  }
  return (
    <div className="cards-grid">
      {Object.entries(checks).map(([catKey, val]) => {
        const citations = val.sources && val.sources.length > 0 ? val.sources : (val.evidence || [])
        const topCitation = citations[0]
        const isReview =
          val.status === 'Review' ||
          val.status?.toLowerCase().includes('required') ||
          val.status?.toLowerCase().includes('caution') ||
          val.status?.toLowerCase().includes('applicable')
        return (
          <div key={catKey} className="evidence-card">
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '6px',
              }}
            >
              <strong style={{ textTransform: 'capitalize' }}>
                {catKey.replace(/_/g, ' ')}
              </strong>
              <span className={`badge ${isReview ? 'badge-amber' : 'badge-mint'}`}>
                {val.status}
              </span>
            </div>
            {topCitation ? (
              <div style={{ fontSize: '10px', color: 'var(--muted-foreground)' }}>
                {topCitation.document}
                {topCitation.section ? ` — ${topCitation.section}` : ''}
              </div>
            ) : (
              <div style={{ fontSize: '10px', color: 'var(--muted-foreground)' }}>
                Standard statutory guidelines apply
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}

/* =========================================================================
   STAGE 5: Regulatory Assessment Step
   ========================================================================= */
function RegulatoryAssessmentStep({
  result,
  next,
  back,
}: {
  result: AssessmentResult | null
  next: () => void
  back: () => void
}) {
  const reg = result?.regulatory_assessment
  const evidenceList =
    reg?.sources && reg.sources.length > 0
      ? reg.sources
      : (reg?.general_evidence || [])

  return (
    <div className="analysis-screen page-enter">
      <SectionIntro
        eyebrow="STEP 05 / REGULATORY ASSESSMENT"
        title={
          <>
            Regulatory <em>compliance & fit check.</em>
          </>
        }
        text="Review AYUSH licensing obligations, formulation classification, labeling rules, and Good Manufacturing Practices (GMP) compliance requirements."
      />

      <div className="assessment-layout">
        <div className="domain-card">
          <div className="domain-header">
            <h3>Regulatory FitCheck Status</h3>
            <span
              className={`badge ${
                reg?.overall_status?.toLowerCase().includes('fit') ||
                reg?.overall_status?.toLowerCase().includes('compliant')
                  ? 'badge-mint'
                  : 'badge-amber'
              }`}
            >
              {reg?.overall_status || 'Review required'}
            </span>
          </div>

          {reg?.llm_answer && (
            <div className="llm-box" style={{ marginTop: '12px' }}>
              <strong>
                <Sparkles size={14} /> Regulatory Guidance Synthesis
              </strong>
              <div className="chat-markdown" style={{ marginTop: '8px' }}>
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {reg.llm_answer}
                </ReactMarkdown>
              </div>
            </div>
          )}

          <div style={{ marginTop: '16px' }}>
            <span className="evidence-title">Category Requirements Breakdown</span>
            <div style={{ marginTop: '8px' }}>{renderChecks(reg?.checks)}</div>
          </div>
        </div>

        {evidenceList.length > 0 && (
          <div className="domain-card">
            <div className="domain-header">
              <h3>Retrieved Regulatory Evidence</h3>
              <span className="badge badge-mint">{evidenceList.length} CITATIONS</span>
            </div>
            <div className="evidence-section">
              {evidenceList.map((ev, idx) => (
                <div key={idx} className="evidence-card">
                  <strong>{ev.document || 'Regulatory Statute'}</strong>
                  {ev.text && <p style={{ margin: '4px 0', fontSize: '11px' }}>{ev.text}</p>}
                  <div className="evidence-meta">
                    {ev.section && <span>Section: {ev.section}</span>}
                    {ev.page && <span>Page: {ev.page}</span>}
                    {ev.source_url && (
                      <a
                        href={ev.source_url}
                        target="_blank"
                        rel="noreferrer"
                        style={{
                          color: '#174c49',
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '3px',
                        }}
                      >
                        Official Source <ExternalLink size={11} />
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {reg?.disclaimer && (
          <p style={{ fontSize: '11px', color: 'var(--muted-foreground)', fontStyle: 'italic' }}>
            {reg.disclaimer}
          </p>
        )}

        <div className="screen-footer">
          <button className="back-button" onClick={back}>
            <ChevronLeft size={16} /> Back to IP screening
          </button>
          <button className="continue-button" onClick={next}>
            Continue to TKDL screening <ArrowRight size={17} />
          </button>
        </div>
      </div>
      <Disclaimer />
    </div>
  )
}

/* =========================================================================
   STAGE 6: TKDL Screening Step
   ========================================================================= */
function TKDLScreeningStep({
  result,
  next,
  back,
}: {
  result: AssessmentResult | null
  next: () => void
  back: () => void
}) {
  const tkdl = result?.tkdl_assessment
  const evidenceList =
    tkdl?.sources && tkdl.sources.length > 0
      ? tkdl.sources
      : (tkdl?.general_evidence || [])
  const hasChecks = tkdl?.checks && Object.keys(tkdl.checks).length > 0
  const hasEvidence = evidenceList.length > 0

  return (
    <div className="analysis-screen page-enter">
      <SectionIntro
        eyebrow="STEP 06 / TKDL SCREENING"
        title={
          <>
            Traditional Knowledge <em>Digital Library (TKDL).</em>
          </>
        }
        text="Evaluation of classical Ayurvedic formulations, prior-art disclosures, and statutory patentability exclusions under Section 3(p) of the Indian Patents Act 1970."
      />

      <div className="assessment-layout">
        <div className="domain-card">
          <div className="domain-header">
            <h3>TKDL Screening Status</h3>
            <span className="badge badge-teal">
              {tkdl?.overall_status || 'Insufficient TKDL evidence'}
            </span>
          </div>

          {tkdl?.llm_answer ? (
            <div className="llm-box" style={{ marginTop: '12px' }}>
              <strong>
                <Sparkles size={14} /> Traditional Knowledge Synthesis
              </strong>
              <div className="chat-markdown" style={{ marginTop: '8px' }}>
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {tkdl.llm_answer}
                </ReactMarkdown>
              </div>
            </div>
          ) : null}

          {/* If no evidence or insufficient evidence, display intentional professional empty state */}
          {!hasEvidence && !hasChecks ? (
            <div
              style={{
                background: '#faf9f5',
                border: '1px solid var(--border)',
                borderRadius: '12px',
                padding: '28px 20px',
                textAlign: 'center',
                marginTop: '16px',
              }}
            >
              <BookOpen size={30} style={{ color: '#4a9181', margin: '0 auto 10px' }} />
              <h4 style={{ fontSize: '16px', margin: '0 0 6px', color: 'var(--foreground)' }}>
                Insufficient TKDL Evidence Available
              </h4>
              <p
                style={{
                  color: 'var(--muted-foreground)',
                  fontSize: '12px',
                  maxWidth: '560px',
                  margin: '0 auto 14px',
                  lineHeight: 1.5,
                }}
              >
                No direct prior-art citations were matched from the Traditional Knowledge Digital Library corpus for this formulation.
              </p>
              <div
                style={{
                  background: '#fff',
                  border: '1px solid #e2ddd3',
                  borderRadius: '8px',
                  padding: '12px 16px',
                  maxWidth: '540px',
                  margin: '0 auto',
                  textAlign: 'left',
                  fontSize: '12px',
                  color: 'var(--foreground)',
                }}
              >
                <strong style={{ display: 'block', marginBottom: '4px' }}>
                  Section 3(p) Statutory Safeguard:
                </strong>
                <span style={{ color: 'var(--muted-foreground)', lineHeight: 1.4 }}>
                  Under Section 3(p) of the Indian Patents Act 1970, an invention which is traditional knowledge or an aggregation/duplication of known properties of traditionally known component(s) is not patentable. When classical evidence is not indexed in TKDL, independent prior art searches remain advisable for novelty substantiation.
                </span>
              </div>
            </div>
          ) : (
            <div style={{ marginTop: '16px' }}>
              <span className="evidence-title">Prior Art & Classical Checks</span>
              <div style={{ marginTop: '8px' }}>{renderChecks(tkdl?.checks)}</div>
            </div>
          )}
        </div>

        {hasEvidence && (
          <div className="domain-card">
            <div className="domain-header">
              <h3>TKDL Reference Citations</h3>
              <span className="badge badge-mint">{evidenceList.length} CITATIONS</span>
            </div>
            <div className="evidence-section">
              {evidenceList.map((ev, idx) => (
                <div key={idx} className="evidence-card">
                  <strong>{ev.document || 'TKDL Reference'}</strong>
                  {ev.text && <p style={{ margin: '4px 0', fontSize: '11px' }}>{ev.text}</p>}
                  <div className="evidence-meta">
                    {ev.section && <span>Section: {ev.section}</span>}
                    {ev.page && <span>Page: {ev.page}</span>}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {tkdl?.disclaimer && (
          <p style={{ fontSize: '11px', color: 'var(--muted-foreground)', fontStyle: 'italic' }}>
            {tkdl.disclaimer}
          </p>
        )}

        <div className="screen-footer">
          <button className="back-button" onClick={back}>
            <ChevronLeft size={16} /> Back to regulatory assessment
          </button>
          <button className="continue-button" onClick={next}>
            Continue to ABS screening <ArrowRight size={17} />
          </button>
        </div>
      </div>
      <Disclaimer />
    </div>
  )
}

/* =========================================================================
   STAGE 7: ABS Screening Step
   ========================================================================= */
function ABSScreeningStep({
  input,
  result,
  next,
  back,
}: {
  input: WizardInput
  result: AssessmentResult | null
  next: () => void
  back: () => void
}) {
  const abs = result?.abs_assessment
  const evidenceList =
    abs?.sources && abs.sources.length > 0
      ? abs.sources
      : (abs?.general_evidence || [])
  const hasChecks = abs?.checks && Object.keys(abs.checks).length > 0

  return (
    <div className="analysis-screen page-enter">
      <SectionIntro
        eyebrow="STEP 07 / ABS SCREENING"
        title={
          <>
            Access & Benefit Sharing <em>(ABS) compliance.</em>
          </>
        }
        text="Dedicated screening under the Biological Diversity Act 2002 for commercial utilization of Indian biological resources and prior approvals from the National Biodiversity Authority (NBA)."
      />

      <div className="assessment-layout">
        <div className="domain-card">
          <div className="domain-header">
            <h3>Access & Benefit Sharing Status</h3>
            <span
              className={`badge ${
                abs?.overall_status?.toLowerCase().includes('exempt')
                  ? 'badge-teal'
                  : 'badge-mint'
              }`}
            >
              {abs?.overall_status || 'ABS Review Required'}
            </span>
          </div>

          <div
            style={{
              marginTop: '6px',
              fontSize: '12px',
              color: 'var(--muted-foreground)',
              padding: '6px 12px',
              background: '#f6fbf9',
              borderRadius: '6px',
              display: 'inline-block',
            }}
          >
            <strong>Declared Biological Resources:</strong>{' '}
            {input.biological_resources && input.biological_resources.length > 0
              ? input.biological_resources.join(', ')
              : input.ingredients.join(', ')}
          </div>

          {abs?.llm_answer && (
            <div className="llm-box" style={{ marginTop: '12px' }}>
              <strong>
                <Sparkles size={14} /> Biological Diversity Act Synthesis
              </strong>
              <div className="chat-markdown" style={{ marginTop: '8px' }}>
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {abs.llm_answer}
                </ReactMarkdown>
              </div>
            </div>
          )}

          {hasChecks && (
            <div style={{ marginTop: '16px' }}>
              <span className="evidence-title">Biological Diversity Compliance Checks</span>
              <div style={{ marginTop: '8px' }}>{renderChecks(abs?.checks)}</div>
            </div>
          )}
        </div>

        {evidenceList.length > 0 && (
          <div className="domain-card">
            <div className="domain-header">
              <h3>National Biodiversity Authority Citations</h3>
              <span className="badge badge-mint">{evidenceList.length} CITATIONS</span>
            </div>
            <div className="evidence-section">
              {evidenceList.map((ev, idx) => (
                <div key={idx} className="evidence-card">
                  <strong>{ev.document || 'Biological Diversity Act Reference'}</strong>
                  {ev.text && <p style={{ margin: '4px 0', fontSize: '11px' }}>{ev.text}</p>}
                  <div className="evidence-meta">
                    {ev.section && <span>Section: {ev.section}</span>}
                    {ev.page && <span>Page: {ev.page}</span>}
                    {ev.source_url && (
                      <a
                        href={ev.source_url}
                        target="_blank"
                        rel="noreferrer"
                        style={{
                          color: '#174c49',
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '3px',
                        }}
                      >
                        Official Source <ExternalLink size={11} />
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {abs?.disclaimer && (
          <p style={{ fontSize: '11px', color: 'var(--muted-foreground)', fontStyle: 'italic' }}>
            {abs.disclaimer}
          </p>
        )}

        <div className="screen-footer">
          <button className="back-button" onClick={back}>
            <ChevronLeft size={16} /> Back to TKDL screening
          </button>
          <button className="continue-button" onClick={next}>
            Continue to action roadmap <ArrowRight size={17} />
          </button>
        </div>
      </div>
      <Disclaimer />
    </div>
  )
}

/* =========================================================================
   STAGE 8: Action Roadmap Step
   ========================================================================= */
function RoadmapStep({
  result,
  next,
  back,
}: {
  result: AssessmentResult | null
  next: () => void
  back: () => void
}) {
  const roadmap = result?.roadmap
  const actions: RoadmapAction[] = roadmap?.actions || []

  return (
    <div className="analysis-screen page-enter">
      <SectionIntro
        eyebrow="STEP 08 / ACTION ROADMAP"
        title={
          <>
            Actionable guidance & <em>filing pathways.</em>
          </>
        }
        text="Prioritized roadmap synthesized from your IP screening, regulatory fit check, TKDL review, and ABS obligations."
      />

      <div className="roadmap-actions">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span className="eyebrow small">SYNTHESIZED ACTION PLAN</span>
          <span className="badge badge-mint">
            {roadmap?.status || 'Action plan generated'}
          </span>
        </div>

        {actions.length === 0 ? (
          <div className="state-card roadmap-empty">
            <Leaf size={22} />
            <h2>No immediate action identified</h2>
            <p>Run an assessment from the classification step to generate a grounded roadmap.</p>
          </div>
        ) : (
          actions.map((act, idx) => (
            <div key={idx} className="action-item">
              <div className="action-item-top">
                <div className="action-item-title">
                  <div className="priority-circle">P{act.priority}</div>
                  <div>
                    <strong style={{ fontSize: '14px', display: 'block' }}>
                      {act.action}
                    </strong>
                    <span style={{ fontSize: '10px', color: 'var(--muted-foreground)', textTransform: 'uppercase' }}>
                      Domain: {act.domain} · Type: {act.action_type}
                    </span>
                  </div>
                </div>
                {act.human_escalation && (
                  <span className="badge badge-amber" title="Expert legal or patent agent review recommended">
                    <AlertTriangle size={11} /> Professional Review
                  </span>
                )}
              </div>

              {act.evidence && act.evidence.length > 0 && (
                <div className="evidence-section" style={{ marginTop: '6px' }}>
                  <span className="evidence-title">Official Procedure Citations</span>
                  {act.evidence.map((ev, evIdx) => (
                    <div key={evIdx} className="evidence-card">
                      <strong>{ev.document}</strong>
                      <p style={{ margin: '3px 0', fontSize: '11px' }}>{ev.text}</p>
                      <div className="evidence-meta">
                        {ev.section && <span>Section: {ev.section}</span>}
                        {ev.page && <span>Page: {ev.page}</span>}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))
        )}

        {roadmap?.disclaimer && (
          <p style={{ fontSize: '11px', color: 'var(--muted-foreground)', fontStyle: 'italic', marginTop: '12px' }}>
            {roadmap.disclaimer}
          </p>
        )}

        <div className="screen-footer">
          <button className="back-button" onClick={back}>
            <ChevronLeft size={16} /> Back to ABS screening
          </button>
          <button className="continue-button" onClick={next}>
            View final executive summary <ArrowRight size={17} />
          </button>
        </div>
      </div>
      <Disclaimer />
    </div>
  )
}

/* =========================================================================
   STAGE 9: Final Executive Summary Step
   ========================================================================= */
function FinalSummaryStep({
  input,
  jurisdiction,
  result,
  onOpenChat,
  onRestart,
  back,
}: {
  input: WizardInput
  jurisdiction: Jurisdiction
  result: AssessmentResult | null
  onOpenChat: () => void
  onRestart: () => void
  back: () => void
}) {
  const ip = result?.ip_assessment
  const reg = result?.regulatory_assessment
  const tkdl = result?.tkdl_assessment
  const abs = result?.abs_assessment
  const roadmap = result?.roadmap

  return (
    <div className="analysis-screen page-enter">
      <SectionIntro
        eyebrow="STEP 09 / EXECUTIVE SUMMARY"
        title={
          <>
            Assessment <em>synthesis.</em>
          </>
        }
        text="A holistic summary of your Ayurvedic product analysis across IP, Regulatory, TKDL, and Biological Diversity compliance."
      />

      {/* Hero Overview */}
      <div className="summary-hero">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <span className="eyebrow small">ANALYSIS COMPLETED</span>
            <h2 style={{ fontFamily: 'DM Serif Display, serif', fontSize: '28px', margin: '6px 0 4px', color: 'var(--foreground)' }}>
              {input.product_name || 'Ayurvedic Formulation'}
            </h2>
            <p style={{ fontSize: '12px', color: 'var(--muted-foreground)', margin: 0 }}>
              {input.classification} · {input.product_type} · Jurisdiction: {jurisdiction.name}
            </p>
          </div>
          <button className="primary-cta" onClick={onOpenChat} style={{ marginTop: 0 }}>
            Ask IP Shakti About This <MessageCircle size={16} />
          </button>
        </div>

        <div className="summary-stats">
          <div className="summary-stat-box">
            <span>IP Domains</span>
            <strong>{ip?.relevant_ip_domains?.join(', ') || 'Patent, Trademark'}</strong>
          </div>
          <div className="summary-stat-box">
            <span>Regulatory Fit</span>
            <strong>{reg?.overall_status || 'Review required'}</strong>
          </div>
          <div className="summary-stat-box">
            <span>TKDL Status</span>
            <strong>{tkdl?.overall_status || 'Review required'}</strong>
          </div>
          <div className="summary-stat-box">
            <span>ABS Status</span>
            <strong>{abs?.overall_status || 'Review required'}</strong>
          </div>
        </div>
      </div>

      {/* Detailed Pillars */}
      <div className="assessment-layout" style={{ marginTop: '24px' }}>
        <div className="cards-grid">
          <div className="domain-card">
            <div className="domain-header">
              <h3>1. Formulation & IP</h3>
              <span className="badge badge-teal">IP Screening</span>
            </div>
            <p style={{ fontSize: '12px', margin: 0 }}>
              {ip?.summary || 'Formulation evaluated against Indian Patent Act Section 3(p) and trademark considerations.'}
            </p>
            <div style={{ fontSize: '11px', color: 'var(--muted-foreground)' }}>
              <strong>Ingredients:</strong> {input.ingredients.filter(Boolean).join(', ')}
            </div>
          </div>

          <div className="domain-card">
            <div className="domain-header">
              <h3>2. Regulatory Compliance</h3>
              <span className="badge badge-amber">{reg?.overall_status || 'Review'}</span>
            </div>
            <p style={{ fontSize: '12px', margin: 0 }}>
              AYUSH manufacturing license, labeling rules, and Good Manufacturing Practices (GMP) compliance required prior to commercial distribution.
            </p>
          </div>

          <div className="domain-card">
            <div className="domain-header">
              <h3>3. TKDL & Heritage</h3>
              <span className="badge badge-mint">{tkdl?.overall_status || 'Review'}</span>
            </div>
            <p style={{ fontSize: '12px', margin: 0 }}>
              Classical references identified ({input.traditional_knowledge_source || 'Charaka Samhita'}). Prior-art barrier prevents standard patent on known traditional formulation.
            </p>
          </div>

          <div className="domain-card">
            <div className="domain-header">
              <h3>4. Biological Resources (ABS)</h3>
              <span className="badge badge-amber">{abs?.overall_status || 'Review'}</span>
            </div>
            <p style={{ fontSize: '12px', margin: 0 }}>
              Sourcing of Indian biological resources ({input.biological_resources.join(', ') || 'botanicals'}) invokes Biological Diversity Act NBA/SBB filing mandates.
            </p>
          </div>
        </div>

        {/* Roadmap Actions Preview */}
        {roadmap?.actions && roadmap.actions.length > 0 && (
          <div className="domain-card">
            <div className="domain-header">
              <h3>Immediate Strategic Priorities</h3>
              <span className="badge badge-mint">{roadmap.actions.length} ACTIONS</span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {roadmap.actions.slice(0, 3).map((act, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '12px' }}>
                  <span className="priority-circle" style={{ width: '22px', height: '22px', fontSize: '10px' }}>
                    {act.priority}
                  </span>
                  <strong>{act.action}</strong>
                  <span style={{ color: 'var(--muted-foreground)', fontSize: '11px' }}>({(act.domain || '').toUpperCase()})</span>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="screen-footer">
          <button className="back-button" onClick={back}>
            <ChevronLeft size={16} /> Back to roadmap
          </button>
          <div style={{ display: 'flex', gap: '12px' }}>
            <button className="outline-button" onClick={onRestart}>
              <RefreshCw size={14} /> Start new analysis
            </button>
            <button className="continue-button" onClick={onOpenChat}>
              Open interactive assistant <MessageCircle size={16} />
            </button>
          </div>
        </div>
      </div>
      <Disclaimer />
    </div>
  )
}

/* =========================================================================
   CHATBOT: Ask IP Shakti
   ========================================================================= */
function ChatStep({
  jurisdiction,
  input,
  result,
}: {
  jurisdiction: Jurisdiction
  input: WizardInput
  result: AssessmentResult | null
}) {
  const [messages, setMessages] = useState<
    Array<{ role: 'user' | 'assistant'; content: string; sources?: SourceCitation[] }>
  >([])
  const [question, setQuestion] = useState('')
  const [busy, setBusy] = useState(false)

  const hasActiveAssessment = Boolean(result && hasAssessment(result))

  const send = async (value = question) => {
    const text = value.trim()
    if (!text || busy) return

    const history = messages.map((m) => ({ role: m.role, content: m.content }))
    setQuestion('')
    setMessages((prev) => [...prev, { role: 'user', content: text }])
    setBusy(true)

    // Construct ChatRequest matching backend schema exactly
    const request: ChatRequest = {
      question: text,
      product_context: hasActiveAssessment
        ? result?.product_context || { ...input, jurisdiction: jurisdiction.name || 'India' }
        : {},
      legal_report: hasActiveAssessment ? result?.legal_report || {} : {},
      roadmap: hasActiveAssessment ? result?.roadmap || {} : {},
      chat_history: history,
    }

    try {
      const response = await askAssessmentQuestion(request)
      setMessages((current) => [
        ...current,
        {
          role: 'assistant',
          content: response.answer,
          sources: response.sources,
        },
      ])
    } catch (error) {
      setMessages((current) => [
        ...current,
        {
          role: 'assistant',
          content:
            error instanceof Error
              ? `Could not complete chat query: ${error.message}`
              : 'I could not reach the chat service. Please verify that the backend is running at http://127.0.0.1:8000.',
        },
      ])
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="analysis-screen page-enter">
      <SectionIntro
        eyebrow="AI ASSISTANT / ASK IP SHAKTI"
        title={
          <>
            Source-grounded <em>guidance.</em>
          </>
        }
        text="Ask follow-up questions about patentability, regulatory licensing, TKDL prior art, and ABS compliance. All answers are grounded in official Indian legal sources."
      />

      <div className="chat-context">
        <span className="country-code">{jurisdiction.code}</span>
        <div>
          <strong>Active Jurisdiction: {jurisdiction.name}</strong>
          <span>
            {hasActiveAssessment
              ? `Assessment context attached for "${input.product_name || 'Current Product'}"`
              : 'General inquiry mode · No product assessment attached'}
          </span>
        </div>
        {hasActiveAssessment && <span className="badge badge-mint">CONTEXT ACTIVE</span>}
      </div>

      <div className="chat-card assessment-chat">
        <div className="chat-messages">
          {messages.length === 0 && (
            <div className="chat-empty">
              <MessageCircle size={24} />
              <p>
                {hasActiveAssessment
                  ? 'Ask anything about your assessment: patent novelty, Section 3(p), AYUSH licensing requirements, or NBA approval steps.'
                  : 'Ask any question regarding Ayurvedic IP, Patents Act 1970, TKDL, or Biological Diversity Act compliance.'}
              </p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', justifyContent: 'center', marginTop: '8px' }}>
                <button
                  type="button"
                  className="outline-button"
                  onClick={() => send('Why is ABS compliance relevant to my product?')}
                >
                  Why is ABS compliance relevant?
                </button>
                <button
                  type="button"
                  className="outline-button"
                  onClick={() => send('Can I patent this traditional formulation in India?')}
                >
                  Can I patent this in India?
                </button>
                <button
                  type="button"
                  className="outline-button"
                  onClick={() => send('What are the AYUSH licensing requirements?')}
                >
                  AYUSH licensing requirements?
                </button>
              </div>
            </div>
          )}

          {messages.map((message, index) => (
            <div className={`chat-message ${message.role}`} key={index}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', width: '100%' }}>
                {message.role === 'assistant' ? (
                  <div className="chat-markdown">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {message.content}
                    </ReactMarkdown>
                  </div>
                ) : (
                  <span style={{ whiteSpace: 'pre-wrap' }}>{message.content}</span>
                )}
                {message.sources && message.sources.length > 0 && (
                  <div className="chat-sources">
                    <span className="chat-sources-title">RETRIEVED LEGAL SOURCES:</span>
                    {message.sources.map((src, sIdx) => (
                      <div key={sIdx} className="chat-source-item">
                        <strong>{src.document}</strong> {src.section ? `· ${src.section}` : ''}{' '}
                        {src.page ? `(Page ${src.page})` : ''}
                        {src.source_url && (
                          <a
                            href={src.source_url}
                            target="_blank"
                            rel="noreferrer"
                            style={{ marginLeft: '6px', color: '#174c49' }}
                          >
                            Source Link ↗
                          </a>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}

          {busy && (
            <div className="chat-message assistant">
              <span className="typing">Consulting RAG engine & legal knowledge base…</span>
            </div>
          )}
        </div>

        <form
          className="chat-compose"
          onSubmit={(e) => {
            e.preventDefault()
            send()
          }}
        >
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question about IP, TKDL, ABS, or regulatory compliance…"
            aria-label="Ask IP Shakti"
          />
          <button type="submit" disabled={busy || !question.trim()} aria-label="Send question">
            <ArrowRight size={17} />
          </button>
        </form>
      </div>
      <Disclaimer />
    </div>
  )
}

/* =========================================================================
   WORKSPACE HISTORY & KNOWLEDGE BASE
   ========================================================================= */
function WorkspaceHistory({ onResume }: { onResume: () => void }) {
  const [records, setRecords] = useState<{ name: string; status: string; date: string }[]>([])
  const [query, setQuery] = useState('')

  useMemo(() => {
    try {
      setRecords(JSON.parse(localStorage.getItem('ip-shakti-analyses') || '[]'))
    } catch {
      setRecords([])
    }
  }, [])

  const filtered = records.filter((record) =>
    record.name.toLowerCase().includes(query.toLowerCase())
  )

  return (
    <div className="analysis-screen page-enter">
      <SectionIntro
        eyebrow="WORKSPACE / MY ANALYSES"
        title={
          <>
            Your analysis <em>history.</em>
          </>
        }
        text="Resume saved work or review assessments completed in this workspace."
      />
      <div className="history-toolbar">
        <span>{records.length} saved analyses</span>
        <label className="search-field">
          <Search size={15} />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search analyses"
          />
        </label>
      </div>
      {filtered.length === 0 ? (
        <div className="state-card">
          <Leaf size={22} />
          <h2>No saved analyses yet</h2>
          <p>Completed and in-progress assessments will appear here after you run an intake.</p>
          <button className="continue-button" onClick={onResume}>
            Start an assessment <ArrowRight size={16} />
          </button>
        </div>
      ) : (
        <div className="history-list">
          {filtered.map((record) => (
            <div className="history-card" key={`${record.name}-${record.date}`}>
              <div className="analysis-mark mint">
                <Leaf size={17} />
              </div>
              <div className="history-main">
                <strong>{record.name}</strong>
                <span>{record.date}</span>
              </div>
              <span className={`status ${record.status === 'Completed' ? 'yellow' : 'mint'}`}>
                {record.status}
              </span>
              <button className="history-action" onClick={onResume}>
                Resume <ArrowRight size={15} />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function KnowledgeBase() {
  const [query, setQuery] = useState('')
  const sources = [
    { title: 'Indian Patents Act 1970 — Section 3(p)', type: 'Statutory Act', topic: 'Traditional Knowledge' },
    { title: 'TKDL — Traditional Knowledge Digital Library', type: 'Prior Art Database', topic: 'Ayurveda Prior Art' },
    { title: 'Biological Diversity Act 2002 — Section 3 & 4', type: 'Official Statute', topic: 'Access & Benefit Sharing (ABS)' },
    { title: 'AYUSH Guidelines — Drugs and Cosmetics Rules', type: 'Regulatory Framework', topic: 'Formulation Licensing & GMP' },
    { title: 'Trade Marks Act 1999 — Ayurvedic Naming & Deceptiveness', type: 'Official Statute', topic: 'Trademarks' },
  ]
  const filtered = sources.filter((source) =>
    `${source.title} ${source.topic}`.toLowerCase().includes(query.toLowerCase())
  )

  return (
    <div className="analysis-screen page-enter">
      <SectionIntro
        eyebrow="REFERENCE / KNOWLEDGE BASE"
        title={
          <>
            Ground your work in <em>trusted sources.</em>
          </>
        }
        text="Browse authoritative legal and regulatory references utilized by the IP Shakti backend."
      />
      <label className="search-field knowledge-search">
        <Search size={15} />
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search the knowledge base"
        />
      </label>
      <div className="knowledge-grid">
        {filtered.map((source) => (
          <article className="knowledge-card" key={source.title}>
            <span className="eyebrow small">{source.topic}</span>
            <h2>{source.title}</h2>
            <p>{source.type} · Grounded in IP Shakti backend RAG corpus.</p>
            <button className="outline-button" disabled>
              Indexed in RAG <CheckCircle2 size={14} />
            </button>
          </article>
        ))}
      </div>
      <Disclaimer />
    </div>
  )
}

/* =========================================================================
   HOME: Dashboard
   ========================================================================= */
function Dashboard({ start }: { start: () => void }) {
  return (
    <div className="dashboard page-enter">
      <div className="eyebrow">
        <span className="eyebrow-line" />
        AYURVEDA IP & REGULATORY CO-PILOT
      </div>
      <h1>
        Welcome to <em>IP Shakti.</em>
      </h1>
      <p className="lede">
        A grounded decision support system for Ayurvedic innovators, navigating patents, Section 3(p) exclusions, TKDL prior art, Biological Diversity Act (ABS), and AYUSH regulatory compliance.
      </p>

      <button className="primary-cta" onClick={start}>
        Start New Assessment <ArrowRight size={18} />
      </button>

      <div className="stats">
        <div>
          <span>Active jurisdiction</span>
          <strong>India</strong>
        </div>
        <div>
          <span>Integrated Engines</span>
          <strong>IP · Reg · TKDL · ABS</strong>
        </div>
        <div>
          <span>Backend status</span>
          <strong>Connected (8000)</strong>
        </div>
      </div>

      <section className="recent">
        <div className="section-head">
          <div>
            <span className="eyebrow small">WORKSPACE</span>
            <h2>Integrated analysis workflow</h2>
          </div>
        </div>
        <div className="empty-history">
          <Leaf size={18} />
          <p>
            The analysis follows the 9-step guided journey: Formulation Input → Jurisdiction → Classification → IP Screening → Regulatory Assessment → TKDL Screening → ABS Screening → Action Roadmap → Final Summary.
          </p>
        </div>
      </section>

      <div className="dashboard-note">
        <Sparkles size={18} />
        <div>
          <strong>How IP Shakti works</strong>
          <span>
            1. Enter formulation details · 2. Select target jurisdiction · 3. Classify heritage & bio-resources · 4. IP screening · 5. Regulatory FitCheck · 6. TKDL prior art · 7. ABS screening · 8. Action roadmap · 9. Executive summary & chatbot
          </span>
        </div>
      </div>

      <Disclaimer />
    </div>
  )
}

/* =========================================================================
   MAIN APPLICATION ROUTER & STATE CONTAINER
   ========================================================================= */
export default function Page() {
  const [activeNav, setActiveNav] = useState('Dashboard')
  // stage 0: Dashboard
  // stage 1: Formulation Input
  // stage 2: Jurisdiction Selection
  // stage 3: Guided Classification
  // stage 4: IP Screening
  // stage 5: Regulatory Assessment
  // stage 6: TKDL Screening
  // stage 7: ABS Screening
  // stage 8: Action Roadmap
  // stage 9: Final Executive Summary
  // stage 10: ChatStep (Ask IP Shakti)
  // stage 11: Workspace History
  // stage 12: Knowledge Base
  const [stage, setStage] = useState(0)

  const [jurisdiction, setJurisdiction] = useState(jurisdictions[0])
  const [input, setInput] = useState<WizardInput>(initialInput)
  const [result, setResult] = useState<AssessmentResult | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const start = () => {
    setActiveNav('New Assessment')
    setStage(1)
  }

  const submit = async () => {
    setLoading(true)
    setError('')

    const cleanIngredients = input.ingredients.map((i) => i.trim()).filter(Boolean)
    const cleanBio = input.biological_resources.map((b) => b.trim()).filter(Boolean)

    const payload: WizardInput = {
      ...input,
      product_name: input.product_name.trim(),
      product_description: input.product_description?.trim() || undefined,
      jurisdiction: jurisdiction.name || 'India',
      product_type: input.product_type,
      classification: input.classification,
      form: input.form?.trim() || undefined,
      ingredients:
        input.classification === 'single ingredient product'
          ? cleanIngredients.slice(0, 1)
          : cleanIngredients,
      intended_use: input.intended_use.trim(),
      claims: input.claims.map((c) => c.trim()).filter(Boolean),
      innovation_description: input.innovation_description?.trim() || undefined,
      traditional_knowledge: input.traditional_knowledge,
      traditional_knowledge_source:
        input.traditional_knowledge === 'no'
          ? undefined
          : input.traditional_knowledge_source?.trim() || undefined,
      uses_biological_resources: input.uses_biological_resources,
      biological_resources:
        input.uses_biological_resources === 'no' ? [] : cleanBio,
      manufacturing_location: input.manufacturing_location?.trim() || undefined,
      commercial_use: Boolean(input.commercial_use),
    }

    try {
      const response = await submitAssessment(payload)
      const normalized = normalizeAssessment(response as Record<string, unknown>)
      setResult(normalized)

      try {
        const saved = JSON.parse(localStorage.getItem('ip-shakti-analyses') || '[]')
        localStorage.setItem(
          'ip-shakti-analyses',
          JSON.stringify([
            {
              name: input.product_name || 'Ayurvedic Formulation',
              status: 'Completed',
              date: new Date().toLocaleDateString(),
            },
            ...saved.filter(
              (item: { name: string }) => item.name !== input.product_name
            ),
          ])
        )
      } catch {
        /* storage may be restricted */
      }

      // Automatically transition to Stage 4: IP Screening
      setStage(4)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unable to submit assessment')
    } finally {
      setLoading(false)
    }
  }

  const nav = (value: string) => {
    setActiveNav(value)
    if (value === 'Dashboard') setStage(0)
    else if (value === 'New Assessment') setStage(1)
    else if (value === 'Ask IP Shakti') setStage(10)
    else if (value === 'My Analyses') setStage(11)
    else if (value === 'Knowledge Base') setStage(12)
    else setStage(0)
  }

  let screen = null
  if (stage === 0) {
    screen = <Dashboard start={start} />
  } else if (stage === 1) {
    screen = (
      <DetailsStep
        input={input}
        setInput={setInput}
        next={() => setStage(2)}
        back={() => setStage(0)}
      />
    )
  } else if (stage === 2) {
    screen = (
      <JurisdictionStep
        selected={jurisdiction}
        setSelected={(j) => {
          setJurisdiction(j)
          setInput((prev) => ({ ...prev, jurisdiction: j.name }))
        }}
        next={() => setStage(3)}
        back={() => setStage(1)}
      />
    )
  } else if (stage === 3) {
    screen = (
      <ClassificationStep
        jurisdiction={jurisdiction}
        input={input}
        setInput={setInput}
        onSubmit={submit}
        loading={loading}
        error={error}
        back={() => setStage(2)}
      />
    )
  } else if (stage === 4) {
    screen = (
      <IPScreeningStep
        result={result}
        next={() => setStage(5)}
        back={() => setStage(3)}
      />
    )
  } else if (stage === 5) {
    screen = (
      <RegulatoryAssessmentStep
        result={result}
        next={() => setStage(6)}
        back={() => setStage(4)}
      />
    )
  } else if (stage === 6) {
    screen = (
      <TKDLScreeningStep
        result={result}
        next={() => setStage(7)}
        back={() => setStage(5)}
      />
    )
  } else if (stage === 7) {
    screen = (
      <ABSScreeningStep
        input={input}
        result={result}
        next={() => setStage(8)}
        back={() => setStage(6)}
      />
    )
  } else if (stage === 8) {
    screen = (
      <RoadmapStep
        result={result}
        next={() => setStage(9)}
        back={() => setStage(7)}
      />
    )
  } else if (stage === 9) {
    screen = (
      <FinalSummaryStep
        input={input}
        jurisdiction={jurisdiction}
        result={result}
        onOpenChat={() => {
          setActiveNav('Ask IP Shakti')
          setStage(10)
        }}
        onRestart={() => {
          setInput(initialInput)
          setResult(null)
          setStage(1)
        }}
        back={() => setStage(8)}
      />
    )
  } else if (stage === 10) {
    screen = (
      <ChatStep
        jurisdiction={jurisdiction}
        input={input}
        result={result}
      />
    )
  } else if (stage === 11) {
    screen = <WorkspaceHistory onResume={start} />
  } else if (stage === 12) {
    screen = <KnowledgeBase />
  }

  // Active stepper calculation (for stages 1 to 9)
  const currentStepIndex = stage >= 1 && stage <= 9 ? stage - 1 : -1

  return (
    <main className="app-shell">
      <Sidebar active={activeNav} onChange={nav} />
      <section className="main-area">
        <Header />
        {currentStepIndex >= 0 && <Progress current={currentStepIndex} />}
        {screen}
      </section>
    </main>
  )
}
