import { useMemo, useState } from 'react'
import mammoth from 'mammoth/mammoth.browser'
import { parseDocxWithBackend } from '../api/parserApi.js'

const PAGE_TYPES = ['university', 'course', 'specialization']

const TEMPLATE_DEFINITIONS = {
  university: {
    title: 'University Page',
    source: 'NMIMS University Page.html',
    signals: ['university', 'accreditation', 'ranking', 'faculty', 'alumni', 'recruiter', 'placement', 'programs', 'admission'],
    fields: [
      { name: 'university_name', type: 'text', required: true, aliases: ['university name', 'college name', 'institution name'] },
      { name: 'university_full_name', type: 'text', required: false, aliases: ['full name', 'about university'] },
      { name: 'hero_description', type: 'wysiwyg', required: true, aliases: ['overview', 'introduction', 'summary'] },
      { name: 'hero_stats', type: 'repeater', required: true, children: ['label', 'value'], aliases: ['stats', 'quick stats', 'numbers'] },
      { name: 'about_content', section: 'About NMIMS Online', type: 'wysiwyg', required: true, aliases: ['about university', 'about nmims online', 'about'] },
      { name: 'quick_facts', section: 'About NMIMS Online', type: 'repeater', required: false, children: ['label', 'value'], aliases: ['quick facts', 'facts'] },
      { name: 'why_choose_content', section: 'Why Choose NMIMS Online?', type: 'wysiwyg', required: true, aliases: ['why choose', 'why choose university'] },
      { name: 'university_facts', section: 'NMIMS Online Facts', type: 'repeater', required: false, children: ['title', 'description'], aliases: ['facts', 'highlights', 'key highlights'] },
      { name: 'accreditations', section: 'Accreditations & Rankings', type: 'repeater', required: true, children: ['name', 'description'], aliases: ['accreditations', 'rankings', 'approvals'] },
      { name: 'programs', section: 'Programs & Fee Structure', type: 'repeater', required: true, children: ['name', 'duration', 'fee', 'eligibility'], aliases: ['programs offered', 'courses', 'fee structure'] },
      { name: 'admission_steps', section: 'Admission Process', type: 'repeater', required: true, children: ['title', 'description'], aliases: ['admission process', 'how to apply'] },
      { name: 'emi_content', section: 'EMI & Financial Assistance', type: 'wysiwyg', required: false, aliases: ['emi', 'financial assistance', 'scholarship'] },
      { name: 'examination_content', section: 'Examination Process', type: 'wysiwyg', required: false, aliases: ['examination process', 'exam process'] },
      { name: 'faculty_members', section: 'Faculty Members', type: 'repeater', required: false, children: ['name', 'designation'], aliases: ['faculty', 'professors'] },
      { name: 'placement_content', section: 'Placement & Career Services', type: 'wysiwyg', required: false, aliases: ['placements', 'career services', 'recruiters'] },
      { name: 'reviews', section: 'Student Reviews', type: 'repeater', required: false, children: ['review', 'author'], aliases: ['student reviews', 'testimonials'] },
      { name: 'faqs', section: 'Frequently Asked Questions', type: 'repeater', required: true, children: ['question', 'answer'], aliases: ['faqs', 'frequently asked questions'] },
    ],
  },
  course: {
    title: 'Course Page',
    source: 'NMIMS Online MBA.html',
    signals: ['course', 'mba', 'program', 'duration', 'semester', 'syllabus', 'curriculum', 'eligibility', 'fee'],
    fields: [
      { name: 'course_name', type: 'text', required: true, aliases: ['course name', 'program name'] },
      { name: 'university_name', type: 'text', required: false, aliases: ['university name', 'offered by'] },
      { name: 'hero_description', type: 'wysiwyg', required: true, aliases: ['overview', 'course overview', 'summary'] },
      { name: 'hero_facts', type: 'repeater', required: true, children: ['label', 'value'], aliases: ['quick facts', 'duration', 'mode'] },
      { name: 'about_content', section: 'About the Program', type: 'wysiwyg', required: true, aliases: ['about program', 'about course'] },
      { name: 'program_highlights', section: 'NMIMS Online MBA — Program Highlights', type: 'repeater', required: true, children: ['title', 'description'], aliases: ['program highlights', 'key highlights'] },
      { name: 'accreditations', section: 'Accreditations & Rankings', type: 'repeater', required: false, children: ['name', 'description'], aliases: ['accreditations', 'rankings'] },
      { name: 'specializations', section: 'Specializations', type: 'repeater', required: false, children: ['name', 'fee'], aliases: ['specializations', 'electives'] },
      { name: 'fee_plans', section: 'Fee Structure & EMI', type: 'repeater', required: true, children: ['plan', 'amount', 'total'], aliases: ['fee structure', 'fees', 'emi'] },
      { name: 'eligibility', section: 'Eligibility Criteria', type: 'repeater', required: true, children: ['title', 'description'], aliases: ['eligibility criteria', 'eligibility'] },
      { name: 'admission_steps', section: 'Admission Process', type: 'repeater', required: true, children: ['title', 'description'], aliases: ['admission process', 'how to apply'] },
      { name: 'syllabus', section: 'Syllabus & Curriculum', type: 'repeater', required: true, children: ['semester', 'subjects'], aliases: ['syllabus', 'curriculum', 'semester'] },
      { name: 'placement_content', section: 'Placement & Career Services', type: 'wysiwyg', required: false, aliases: ['placement', 'career services'] },
      { name: 'job_profiles', section: 'Job Profiles & Average Salary', type: 'repeater', required: false, children: ['role', 'salary'], aliases: ['job profiles', 'average salary', 'career scope'] },
      { name: 'certificate_content', section: 'Sample Certificate', type: 'wysiwyg', required: false, aliases: ['sample certificate', 'certificate'] },
      { name: 'reviews', section: 'Student Reviews', type: 'repeater', required: false, children: ['review', 'author'], aliases: ['reviews', 'testimonials'] },
      { name: 'faqs', section: 'Frequently Asked Questions', type: 'repeater', required: true, children: ['question', 'answer'], aliases: ['faqs', 'frequently asked questions'] },
    ],
  },
  specialization: {
    title: 'Specialization Page',
    source: 'NMIMS MBA Marketing.html',
    signals: ['specialization', 'marketing', 'finance', 'hr', 'analytics', 'skills', 'salary', 'career scope', 'job opportunities'],
    fields: [
      { name: 'specialization_name', type: 'text', required: true, aliases: ['specialization name', 'domain', 'mba in'] },
      { name: 'course_name', type: 'text', required: false, aliases: ['course name', 'program'] },
      { name: 'hero_description', type: 'wysiwyg', required: true, aliases: ['overview', 'summary'] },
      { name: 'hero_facts', type: 'repeater', required: true, children: ['label', 'value'], aliases: ['quick facts', 'duration', 'salary'] },
      { name: 'about_content', section: 'About the Specialization', type: 'wysiwyg', required: true, aliases: ['about specialization', 'about marketing'] },
      { name: 'quick_facts', section: 'About the Specialization', type: 'repeater', required: false, children: ['label', 'value'], aliases: ['quick facts', 'facts'] },
      { name: 'program_highlights', section: 'MBA in Marketing — Program Highlights', type: 'repeater', required: true, children: ['title', 'description'], aliases: ['program highlights', 'specialization highlights', 'skills'] },
      { name: 'eligibility', section: 'Eligibility Criteria', type: 'repeater', required: true, children: ['title', 'description'], aliases: ['eligibility criteria', 'eligibility'] },
      { name: 'fee_plans', section: 'Fee Structure & EMI', type: 'repeater', required: true, children: ['plan', 'amount', 'total'], aliases: ['fee structure', 'fees', 'emi'] },
      { name: 'other_specializations', section: 'Other MBA Specializations', type: 'repeater', required: false, children: ['name', 'fee'], aliases: ['other specializations', 'specializations'] },
      { name: 'syllabus', section: 'Syllabus & Curriculum', type: 'repeater', required: true, children: ['semester', 'subjects'], aliases: ['syllabus', 'curriculum'] },
      { name: 'examination_content', section: 'Examination Process', type: 'wysiwyg', required: false, aliases: ['examination process', 'exam'] },
      { name: 'admission_steps', section: 'Admission Process', type: 'repeater', required: true, children: ['title', 'description'], aliases: ['admission process', 'how to apply'] },
      { name: 'placement_content', section: 'Placement & Career Services', type: 'wysiwyg', required: false, aliases: ['placement', 'career services'] },
      { name: 'job_opportunities', section: 'Job Opportunities & Salary', type: 'repeater', required: true, children: ['role', 'salary'], aliases: ['job opportunities', 'salary trends', 'career scope'] },
      { name: 'certificate_content', section: 'Sample Certificate', type: 'wysiwyg', required: false, aliases: ['sample certificate', 'certificate'] },
      { name: 'reviews', section: 'Student Reviews', type: 'repeater', required: false, children: ['review', 'author'], aliases: ['reviews', 'testimonials'] },
      { name: 'faqs', section: 'Frequently Asked Questions', type: 'repeater', required: true, children: ['question', 'answer'], aliases: ['faqs', 'frequently asked questions'] },
    ],
  },
}

const demoText = `Amity University Online

About the University
Amity University Online is a UGC-entitled online university offering MBA, BBA and other programs for working professionals. The university provides live classes, recorded sessions and placement assistance.

Key Highlights
- UGC Entitled
- NAAC A+
- Online learning with career support
- Multiple programs across management and commerce

Programs Offered
Program | Duration | Fee | Eligibility
Online MBA | 2 Years | INR 1,99,000 | Graduation
Online BBA | 3 Years | INR 1,65,000 | 10+2

Admission Process
1. Register on the university website
2. Fill the online application form
3. Upload documents
4. Pay the program fee
5. Receive admission confirmation

Frequently Asked Questions
Is Amity Online degree valid?
Yes. Amity Online degrees are UGC-entitled and valid for jobs and higher education.

Does Amity offer placement support?
Yes. Eligible students get career and placement assistance.`

function App() {
  const [activePage, setActivePage] = useState('upload')
  const [fileName, setFileName] = useState('')
  const [docHtml, setDocHtml] = useState('')
  const [plainText, setPlainText] = useState('')
  const [error, setError] = useState('')
  const [isParsing, setIsParsing] = useState(false)
  const [manualText, setManualText] = useState('')
  const [backendResult, setBackendResult] = useState(null)

  const localResult = useMemo(() => {
    if (!plainText.trim() && !docHtml.trim()) return null
    return runMappingEngine({ html: docHtml, text: plainText })
  }, [docHtml, plainText])
  const result = backendResult || localResult

  async function handleFile(event) {
    const file = event.target.files?.[0]
    setError('')
    setFileName('')
    setBackendResult(null)
    if (!file) return
    if (!file.name.toLowerCase().endsWith('.docx')) {
      setError('Only .docx files are supported. Please upload a Word document.')
      return
    }
    setIsParsing(true)
    try {
      const arrayBuffer = await file.arrayBuffer()
      const [htmlResult, rawResult] = await Promise.all([
        mammoth.convertToHtml({ arrayBuffer }),
        mammoth.extractRawText({ arrayBuffer }),
      ])
      setFileName(file.name)
      setDocHtml(htmlResult.value || '')
      setPlainText(rawResult.value || stripHtml(htmlResult.value || ''))
      try {
        const apiResult = await parseDocxWithBackend(file)
        setBackendResult(adaptBackendResult(apiResult, htmlResult.value || '', rawResult.value || ''))
      } catch (apiError) {
        setError(`Backend parser unavailable, using local fallback: ${apiError?.message || 'Unknown error'}`)
      }
      setActivePage('json')
    } catch (caught) {
      setError(`DOCX parsing failed: ${caught?.message || 'Unknown error'}`)
    } finally {
      setIsParsing(false)
    }
  }

  function useManualInput() {
    setError('')
    setBackendResult(null)
    setFileName('Pasted parsed content')
    setDocHtml(paragraphsToHtml(manualText))
    setPlainText(manualText)
    setActivePage('json')
  }

  const output = result ? JSON.stringify(buildPublishPayload(result.payload), null, 2) : ''

  return (
    <div className="min-h-screen bg-slate-50 text-slate-950">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl flex-col gap-5 px-5 py-5 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-orange-600">DegreeBaba Intern MVP</p>
            <h1 className="mt-1 text-2xl font-black tracking-tight text-slate-950 md:text-3xl">DOCX to ACF JSON Parser</h1>
          </div>
          <div className="flex flex-wrap gap-2">
            {[
              ['upload', 'Upload'],
              ['validation', 'Validation'],
              ['json', 'JSON'],
            ].map(([id, label]) => (
              <button key={id} className={`nav-pill ${activePage === id ? 'nav-pill-on' : ''}`} onClick={() => setActivePage(id)}>
                {label}
              </button>
            ))}
          </div>
        </div>
      </header>

      <main className="mx-auto grid max-w-7xl gap-5 px-5 py-6 lg:grid-cols-[280px_1fr]">
        <aside className="space-y-4">
          <StatusCard result={result} fileName={fileName} error={error} isParsing={isParsing} />
        </aside>

        <section className="min-w-0">
          {activePage === 'upload' && (
            <UploadPage
              handleFile={handleFile}
              isParsing={isParsing}
              error={error}
              manualText={manualText}
              setManualText={setManualText}
              useManualInput={useManualInput}
            />
          )}
          {activePage === 'validation' && <ValidationPage result={result} />}
          {activePage === 'json' && <JsonPage result={result} output={output} />}
        </section>
      </main>
    </div>
  )
}

function StatusCard({ result, fileName, error, isParsing }) {
  const confidence = result?.payload.classification_confidence ?? 0
  const aiReview = result?.payload.ai_review
  return (
    <div className="panel">
      <h2 className="panel-title">Run Status</h2>
      <div className="mt-4 space-y-3 text-sm">
        <StatusRow label="File" value={fileName || 'No document loaded'} />
        <StatusRow label="Parser" value={isParsing ? 'Reading DOCX...' : error ? 'Blocked' : result ? 'Parsed' : 'Waiting'} tone={error ? 'bad' : result ? 'good' : 'neutral'} />
        <StatusRow label="Source" value={result?.source === 'backend' ? 'Backend API' : result?.source === 'local' ? 'Local Fallback' : 'Pending'} tone={result?.source === 'backend' ? 'good' : result?.source === 'local' ? 'warn' : 'neutral'} />
        <StatusRow label="Type" value={result?.payload.page_type || 'Unknown'} />
        <StatusRow label="Confidence" value={result ? `${Math.round(confidence * 100)}%` : '0%'} tone={confidence >= 0.8 ? 'good' : result ? 'warn' : 'neutral'} />
        <StatusRow label="AI Review" value={aiReview ? (aiReview.configured ? aiReview.model : 'Unavailable') : 'Pending'} tone={aiReview ? (aiReview.configured ? 'good' : 'warn') : 'neutral'} />
        <StatusRow label="Review" value={result?.payload.needs_manual_review ? 'Required' : result ? 'Not required' : 'Pending'} tone={result?.payload.needs_manual_review ? 'warn' : result ? 'good' : 'neutral'} />
      </div>
    </div>
  )
}

function StatusRow({ label, value, tone = 'neutral' }) {
  return (
    <div className="flex items-center justify-between gap-3">
      <span className="text-slate-500">{label}</span>
      <span className={`status ${tone}`}>{value}</span>
    </div>
  )
}

function UploadPage({ handleFile, isParsing, error, manualText, setManualText, useManualInput }) {
  return (
    <div className="space-y-5">
      <div className="panel">
        <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
          <div>
            <p className="eyebrow">Upload</p>
            <h2 className="page-heading">Upload DOCX and generate final JSON</h2>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600">
              Upload a writer DOCX file to generate the final ACF JSON payload and validation report. WordPress publish/update can be connected in the next phase.
            </p>
            <label className="mt-6 flex min-h-44 cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-slate-300 bg-slate-50 px-6 text-center transition hover:border-orange-500 hover:bg-orange-50">
              <span className="text-base font-bold text-slate-900">{isParsing ? 'Parsing document...' : 'Choose .docx file'}</span>
              <span className="mt-2 text-sm text-slate-500">University, course, or specialization content</span>
              <input type="file" accept=".docx" className="hidden" onChange={handleFile} disabled={isParsing} />
            </label>
            {error && <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm font-semibold text-red-700">{error}</div>}
          </div>
          <div className="rounded-lg border border-slate-200 bg-white p-4">
            <h3 className="text-sm font-black uppercase tracking-[0.14em] text-slate-500">What You Get</h3>
            <ul className="mt-4 space-y-3 text-sm leading-6 text-slate-700">
              <li>Final JSON payload for WordPress ACF.</li>
              <li>Validation report with missing fields, unmapped fields, and warnings.</li>
              <li>Manual review flag when confidence or AI review is weak.</li>
              <li>WYSIWYG fields as HTML, not plain text.</li>
              <li>Repeaters as valid JSON arrays.</li>
              <li>Safe null output instead of fake data.</li>
            </ul>
          </div>
        </div>
      </div>

      <div className="panel">
        <h2 className="panel-title">Fallback Input</h2>
        <textarea
          className="mt-4 min-h-56 w-full resize-y rounded-lg border border-slate-300 bg-white p-4 font-mono text-sm outline-none focus:border-orange-500"
          value={manualText}
          onChange={(event) => setManualText(event.target.value)}
          placeholder={demoText}
        />
        <div className="mt-4 flex flex-wrap gap-3">
          <button className="primary-btn" onClick={useManualInput} disabled={!manualText.trim()}>
            Generate Output
          </button>
          <button className="secondary-btn" onClick={() => setManualText(demoText)}>
            Load Demo Text
          </button>
        </div>
      </div>
    </div>
  )
}

function ValidationPage({ result }) {
  if (!result) return <EmptyState title="No validation report yet" body="Run a document first." />
  const validation = result.payload.validation
  const summary = [
    { label: 'Missing', value: validation.missing_fields?.length || 0, tone: 'bad' },
    { label: 'Unmapped', value: validation.unmapped_fields?.length || 0, tone: 'warn' },
    { label: 'Thin', value: validation.thin_content?.length || 0, tone: 'warn' },
    { label: 'Warnings', value: validation.warnings?.length || 0, tone: 'neutral' },
  ]
  return (
    <div className="space-y-5">
      <div className="panel">
        <p className="eyebrow">Validation</p>
        <h2 className="page-heading">Validation Report</h2>
        <p className="mt-3 text-sm leading-6 text-slate-600">
          Review missing fields, thin content, warnings, and AI review status before sending this payload to WordPress later.
        </p>
        <div className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          {summary.map((item) => (
            <div key={item.label} className="validation-stat">
              <span className="validation-stat-label">{item.label}</span>
              <span className={`status ${item.tone}`}>{item.value}</span>
            </div>
          ))}
        </div>
      </div>
      <div className="grid gap-5 lg:grid-cols-2">
        <ValidationList title="Missing Fields" items={validation.missing_fields} tone="bad" />
        <ValidationList title="Unmapped Fields" items={validation.unmapped_fields || []} tone="warn" />
      </div>
      <div className="grid gap-5 lg:grid-cols-2">
        <ValidationList title="Thin Content" items={validation.thin_content} tone="warn" />
        <ValidationList title="Warnings" items={validation.warnings} tone="neutral" />
      </div>
    </div>
  )
}

function ValidationList({ title, items, tone }) {
  return (
    <div className="panel">
      <div className="flex items-center justify-between gap-3">
        <h2 className="panel-title">{title}</h2>
        <span className={`status ${items.length ? tone : 'good'}`}>{items.length}</span>
      </div>
      <div className="mt-4 max-h-[420px] space-y-2 overflow-auto pr-1">
        {items.length ? (
          items.map((item, index) => (
            <div key={`${title}-${index}-${item}`} className={`validation-item ${tone === 'bad' ? 'validation-item-bad' : tone === 'warn' ? 'validation-item-warn' : 'validation-item-neutral'}`}>
              <code className="validation-code">{item}</code>
            </div>
          ))
        ) : (
          <div className="rounded-lg bg-emerald-50 p-3 text-sm font-semibold text-emerald-800">No issues detected</div>
        )}
      </div>
    </div>
  )
}

function JsonPage({ result, output }) {
  if (!result) return <EmptyState title="No JSON payload yet" body="Upload and map a DOCX first." />
  return (
    <div className="panel">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="eyebrow">Final Output</p>
          <h2 className="page-heading">Final JSON payload</h2>
          <p className="mt-3 text-sm leading-6 text-slate-600">
            This is the clean publish payload for WordPress. Validation, confidence, schema inference, and mapping diagnostics are shown separately in the validation screen.
          </p>
        </div>
        <button className="secondary-btn" onClick={() => navigator.clipboard?.writeText(output)}>
          Copy JSON
        </button>
      </div>
      <pre className="mt-5 max-h-[680px] overflow-auto rounded-lg bg-slate-950 p-5 text-xs leading-5 text-slate-100">{output}</pre>
    </div>
  )
}

function EmptyState({ title, body }) {
  return (
    <div className="panel flex min-h-80 flex-col items-center justify-center text-center">
      <h2 className="text-xl font-black">{title}</h2>
      <p className="mt-2 max-w-md text-sm leading-6 text-slate-600">{body}</p>
    </div>
  )
}

function buildPublishPayload(payload) {
  return {
    page_type: payload.page_type,
    mapped_fields: normalizeMappedFields(payload.mapped_fields),
  }
}

function normalizeMappedFields(mappedFields) {
  if (!mappedFields || typeof mappedFields !== 'object' || Array.isArray(mappedFields)) {
    return mappedFields
  }

  const keys = Object.keys(mappedFields)
  if (keys.length === 1 && /_schema$/.test(keys[0]) && mappedFields[keys[0]] && typeof mappedFields[keys[0]] === 'object') {
    return mappedFields[keys[0]]
  }

  return mappedFields
}

function runMappingEngine({ html, text }) {
  const cleanText = normalize(text || stripHtml(html))
  const doc = parseDocument(html, cleanText)
  const classification = classifyDocument(cleanText, doc.sections)
  const pageType = classification.page_type
  const definition = TEMPLATE_DEFINITIONS[pageType]
  const mapped = {}
  const metadata = {}

  definition.fields.forEach((field) => {
    const value = mapField(field, doc, cleanText, pageType)
    mapped[field.name] = value
    metadata[field.name] = {
      type: field.type,
      source: findBestSection(field, doc.sections)?.heading || null,
      mapped: hasValue(value),
      required: Boolean(field.required),
    }
  })

  const validation = validatePayload(definition.fields, mapped, classification)
  return {
    source: 'local',
    classification,
    sections: doc.sections,
    payload: {
      page_type: pageType,
      classification_confidence: round2(classification.confidence),
      inferred_fields: Object.fromEntries(definition.fields.map((field) => [field.name, {
        type: field.type,
        required: Boolean(field.required),
        source_section: field.section || null,
        repeater_fields: field.children || null,
      }])),
      mapped_fields: mapped,
      mapping_metadata: metadata,
      validation,
      needs_manual_review:
        classification.confidence < 0.8 ||
        validation.missing_fields.length > 0 ||
        (validation.unmapped_fields?.length || 0) > 0 ||
        validation.warnings.some((warning) => warning.toLowerCase().includes('ambiguous')),
    },
  }
}

function adaptBackendResult(apiResult, html, text) {
  return {
    source: 'backend',
    classification: {
      page_type: apiResult.page_type,
      confidence: apiResult.classification_confidence,
      scores: apiResult.classification_scores || {
        university: apiResult.page_type === 'university' ? apiResult.classification_confidence : 0,
        course: apiResult.page_type === 'course' ? apiResult.classification_confidence : 0,
        specialization: apiResult.page_type === 'specialization' ? apiResult.classification_confidence : 0,
      },
    },
    sections: parseDocument(html || '', normalize(text || '')).sections,
    payload: apiResult,
  }
}

function parseDocument(html, text) {
  const sections = []
  if (html.trim()) {
    const parser = new DOMParser()
    const parsed = parser.parseFromString(html, 'text/html')
    if (parsed.body.querySelector('h1,h2,h3,h4')) {
      let current = { heading: 'Document Start', html: '', text: '', tables: [] }
      Array.from(parsed.body.children).forEach((node) => {
        if (/^H[1-4]$/.test(node.tagName)) {
          if (current.html || current.text || current.heading !== 'Document Start') sections.push(current)
          current = { heading: node.textContent.trim(), html: '', text: '', tables: [] }
        } else {
          current.html += node.outerHTML
          current.text += `\n${node.textContent.trim()}`
          if (node.tagName === 'TABLE') current.tables.push(extractTable(node))
        }
      })
      if (current.html || current.text || current.heading !== 'Document Start') sections.push(current)
    }
  }

  if (!sections.length) {
    const lines = text.split(/\n+/).map((line) => line.trim()).filter(Boolean)
    let current = { heading: 'Document Start', html: '', text: '', tables: [] }
    lines.forEach((line) => {
      if (looksLikeHeading(line)) {
        if (current.text || current.heading !== 'Document Start') sections.push(current)
        current = { heading: line, html: '', text: '', tables: [] }
      } else {
        current.text += `\n${line}`
        current.html += `<p>${escapeHtml(line)}</p>`
      }
    })
    if (current.text || current.heading !== 'Document Start') sections.push(current)
  }

  return { sections, text }
}

function classifyDocument(text, sections) {
  const joinedHeadings = sections.map((section) => section.heading).join(' ')
  const haystack = `${text} ${joinedHeadings}`.toLowerCase()
  const rawScores = Object.fromEntries(PAGE_TYPES.map((type) => {
    const def = TEMPLATE_DEFINITIONS[type]
    const keywordHits = def.signals.reduce((score, signal) => score + countOccurrences(haystack, signal), 0)
    const headingHits = def.fields.reduce((score, field) => {
      const best = findBestSection(field, sections)
      return score + (best ? best.score : 0)
    }, 0)
    const intentBoost =
      type === 'specialization' && /(marketing|finance|human resource|hr|analytics|operations|salary|job opportunities)/i.test(text) ? 4 : 0
    const courseBoost = type === 'course' && /(syllabus|semester|curriculum|eligibility|duration)/i.test(text) ? 3 : 0
    const universityBoost = type === 'university' && /(faculty|alumni|rankings?|accreditations?|programs offered)/i.test(text) ? 3 : 0
    return [type, keywordHits + headingHits + intentBoost + courseBoost + universityBoost]
  }))
  const total = Object.values(rawScores).reduce((sum, score) => sum + score, 0) || 1
  const scores = Object.fromEntries(PAGE_TYPES.map((type) => [type, rawScores[type] / total]))
  const page_type = PAGE_TYPES.reduce((best, type) => (scores[type] > scores[best] ? type : best), 'university')
  return { page_type, confidence: scores[page_type], scores }
}

function mapField(field, doc, fullText, pageType) {
  if (field.name.endsWith('_name')) return extractName(field.name, fullText, pageType)
  if (field.name === 'hero_description') return firstContentHtml(doc.sections)
  if (field.name === 'hero_stats' || field.name === 'hero_facts') return extractStats(fullText)

  const section = findBestSection(field, doc.sections)?.section
  if (!section) return field.type === 'repeater' ? [] : null

  if (field.type === 'wysiwyg') return sanitizeWysiwyg(section.html || paragraphsToHtml(section.text))
  if (field.type === 'repeater') return extractRepeater(field, section)
  return normalize(section.text) || null
}

function extractName(fieldName, text, pageType) {
  const firstLine = text.split(/\n+/).map((line) => line.trim()).find(Boolean)
  if (!firstLine) return null
  if (fieldName === 'specialization_name') {
    const match = firstLine.match(/MBA\s+in\s+(.+)/i) || text.match(/speciali[sz]ation\s*[:-]\s*(.+)/i)
    return match ? match[1].trim().slice(0, 90) : firstLine.slice(0, 90)
  }
  if (fieldName === 'course_name') {
    const match = firstLine.match(/(online\s+)?(MBA|BBA|B\.?Com|MCA|BCA|MA|M\.?Com).*/i)
    return match ? match[0].trim().slice(0, 90) : pageType === 'course' ? firstLine.slice(0, 90) : null
  }
  if (fieldName === 'university_name' || fieldName === 'university_full_name') {
    const match = firstLine.match(/(.+?(University|Institute|College|NMIMS|Amity).*)/i)
    return match ? match[1].trim().slice(0, 100) : firstLine.slice(0, 100)
  }
  return firstLine.slice(0, 100)
}

function extractRepeater(field, section) {
  const tables = section.tables || []
  if (tables.length) return tableToRepeater(field, tables[0])

  const text = normalize(section.text)
  if (!text) return []

  if (field.name === 'faqs') return extractFaqs(text)
  if (field.name.includes('steps') || /admission/i.test(field.name)) return extractSteps(text)
  if (field.name.includes('syllabus')) return extractSyllabus(text)
  if (field.name.includes('stats') || field.name.includes('facts')) return extractStats(text)

  const listItems = extractListItems(section.html, text)
  if (field.children?.includes('title') && field.children?.includes('description')) {
    return listItems.map((item) => splitTitleDescription(item))
  }
  if (field.children?.includes('name') && field.children?.includes('description')) {
    return listItems.map((item) => {
      const split = splitTitleDescription(item)
      return { name: split.title, description: split.description }
    })
  }
  if (field.children?.includes('review')) {
    return listItems.map((item) => ({ review: item, author: null }))
  }
  return listItems.map((item) => ({ value: item }))
}

function tableToRepeater(field, table) {
  const headers = table[0]?.map((cell) => slug(cell)) || []
  const rows = table.slice(1).filter((row) => row.some(Boolean))
  return rows.map((row) => {
    const object = {}
    field.children?.forEach((child, index) => {
      const childSlug = slug(child)
      const headerIndex = headers.findIndex((head) => head.includes(childSlug) || childSlug.includes(head))
      object[child] = row[headerIndex >= 0 ? headerIndex : index] || null
    })
    return object
  })
}

function extractTable(tableNode) {
  return Array.from(tableNode.querySelectorAll('tr')).map((row) =>
    Array.from(row.querySelectorAll('th,td')).map((cell) => normalize(cell.textContent)),
  )
}

function extractFaqs(text) {
  const lines = text.split(/\n+/).map((line) => line.trim()).filter(Boolean)
  const faqs = []
  for (let index = 0; index < lines.length; index += 1) {
    if (/\?$/.test(lines[index]) || /^q[:.)]/i.test(lines[index])) {
      const question = lines[index].replace(/^q[:.)]\s*/i, '')
      const answerLines = []
      index += 1
      while (index < lines.length && !(/\?$/.test(lines[index]) || /^q[:.)]/i.test(lines[index]))) {
        answerLines.push(lines[index].replace(/^a[:.)]\s*/i, ''))
        index += 1
      }
      index -= 1
      faqs.push({ question, answer: answerLines.join(' ') || null })
    }
  }
  return faqs
}

function extractSteps(text) {
  return text
    .split(/\n+/)
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => line.replace(/^(\d+[).]|-|\*)\s*/, ''))
    .map((line, index) => ({ title: line.length < 55 ? line : `Step ${index + 1}`, description: line }))
}

function extractSyllabus(text) {
  const lines = text.split(/\n+/).map((line) => line.trim()).filter(Boolean)
  const groups = []
  let current = null
  lines.forEach((line) => {
    if (/semester|year|term/i.test(line) && line.length < 80) {
      current = { semester: line, subjects: [] }
      groups.push(current)
    } else if (current) {
      current.subjects.push(...line.split(/[,;|]/).map((item) => item.trim()).filter(Boolean))
    }
  })
  return groups.length ? groups : [{ semester: null, subjects: lines }]
}

function extractStats(text) {
  const matches = [...text.matchAll(/(\d+(?:\.\d+)?\s*(?:K|L|Cr|%|\+)?)(?:\s+(?:students|alumni|faculty|partners|recruiters|years|months|programs|specializations|lpa))?/gi)]
  const seen = new Set()
  return matches
    .map((match) => {
      const value = statValue(match[1])
      const around = text.slice(Math.max(0, match.index - 45), match.index + 75)
      const label = inferStatLabel(around)
      return { label, value }
    })
    .filter((item) => {
      const key = `${item.label}:${item.value}`
      if (!item.value || seen.has(key)) return false
      seen.add(key)
      return true
    })
    .slice(0, 6)
}

function validatePayload(fields, mapped, classification) {
  const missing_fields = []
  const unmapped_fields = []
  const thin_content = []
  const warnings = []
  fields.forEach((field) => {
    const value = mapped[field.name]
    if (field.required && !hasValue(value)) missing_fields.push(field.name)
    if (!hasValue(value)) unmapped_fields.push(field.name)
    if (field.type === 'wysiwyg' && typeof value === 'string' && stripHtml(value).split(/\s+/).length < 20) thin_content.push(field.name)
    if (field.type === 'repeater' && value != null && !Array.isArray(value)) warnings.push(`${field.name} must be an array`)
  })

  const statValues = [
    ...(mapped.hero_stats || []),
    ...(mapped.hero_facts || []),
    ...(mapped.quick_facts || []),
  ].map((item) => item.value).filter(Boolean)
  const duplicates = statValues.filter((value, index) => statValues.indexOf(value) !== index)
  if (duplicates.length) warnings.push(`Duplicate stat values detected: ${[...new Set(duplicates)].join(', ')}`)
  statValues.forEach((value) => {
    if (String(value).length > 6) warnings.push(`Stat value "${value}" exceeds 6 characters`)
  })
  if (classification.confidence < 0.8) warnings.push('Ambiguous page type classification below 0.80')
  return { missing_fields, unmapped_fields, thin_content, warnings }
}

function findBestSection(field, sections) {
  const candidates = [field.section, field.name.replace(/_/g, ' '), ...(field.aliases || [])].filter(Boolean)
  let best = null
  sections.forEach((section) => {
    candidates.forEach((candidate) => {
      const score = similarity(candidate, section.heading)
      if (!best || score > best.score) best = { score, section, heading: section.heading }
    })
  })
  return best && best.score >= 0.42 ? best : null
}

function firstContentHtml(sections) {
  const first = sections.find((section) => stripHtml(section.html).split(/\s+/).length > 18)
  return first ? sanitizeWysiwyg(first.html || paragraphsToHtml(first.text)) : null
}

function extractListItems(html, text) {
  if (html) {
    const parsed = new DOMParser().parseFromString(html, 'text/html')
    const items = Array.from(parsed.querySelectorAll('li')).map((node) => normalize(node.textContent)).filter(Boolean)
    if (items.length) return items
  }
  return text
    .split(/\n+/)
    .map((line) => line.trim().replace(/^(\d+[).]|-|\*)\s*/, ''))
    .filter((line) => line.length > 2)
}

function splitTitleDescription(item) {
  const [title, ...rest] = item.split(/[:-]/)
  return { title: normalize(title), description: normalize(rest.join(':')) || normalize(item) }
}

function inferStatLabel(context) {
  const lower = context.toLowerCase()
  if (lower.includes('student')) return 'Students'
  if (lower.includes('alumni')) return 'Alumni'
  if (lower.includes('faculty')) return 'Faculty'
  if (lower.includes('partner') || lower.includes('recruiter')) return 'Hiring Partners'
  if (lower.includes('program')) return 'Programs'
  if (lower.includes('year')) return 'Years'
  if (lower.includes('salary') || lower.includes('lpa')) return 'Average Salary'
  return 'Stat'
}

function statValue(value) {
  return value.replace(/\s+/g, '').slice(0, 6)
}

function looksLikeHeading(line) {
  if (line.length > 90) return false
  if (/[:.]$/.test(line)) return false
  return /^[A-Z0-9]/.test(line) && line.split(/\s+/).length <= 9
}

function similarity(a, b) {
  const left = new Set(slug(a).split('-').filter(Boolean))
  const right = new Set(slug(b).split('-').filter(Boolean))
  if (!left.size || !right.size) return 0
  const intersection = [...left].filter((word) => right.has(word)).length
  const union = new Set([...left, ...right]).size
  const jaccard = intersection / union
  const contains = slug(a).includes(slug(b)) || slug(b).includes(slug(a)) ? 0.28 : 0
  return Math.min(1, jaccard + contains)
}

function countOccurrences(text, needle) {
  return (text.match(new RegExp(escapeRegExp(needle), 'gi')) || []).length
}

function hasValue(value) {
  if (Array.isArray(value)) return value.length > 0
  return value !== null && value !== undefined && String(value).trim() !== ''
}

function sanitizeWysiwyg(html) {
  const trimmed = html.trim()
  return trimmed ? trimmed : null
}

function paragraphsToHtml(text) {
  return text
    .split(/\n{2,}/)
    .map((paragraph) => normalize(paragraph))
    .filter(Boolean)
    .map((paragraph) => `<p>${escapeHtml(paragraph)}</p>`)
    .join('')
}

function stripHtml(html) {
  return html.replace(/<[^>]*>/g, ' ')
}

function normalize(value) {
  return String(value || '').replace(/\s+/g, ' ').trim()
}

function slug(value) {
  return normalize(value).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;')
}

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

function round2(value) {
  return Math.round(value * 100) / 100
}

export default App
