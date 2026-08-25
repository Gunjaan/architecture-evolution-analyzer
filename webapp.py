import os
import shutil
import tempfile
import html

from dotenv import load_dotenv

load_dotenv()

import gradio as gr
from git import Repo

from app.analyzer import analyze_repository


# ============================================================
# POLISHED UI
# ============================================================

CSS = """
:root {
    --bg: #faf9f7 !important;
    --card: #ffffff !important;
    --text: #18161b !important;
    --text-soft: #48434d !important;
    --muted: #6d6772 !important;
    --border: #e8e2db !important;

    --lavender: #9783c3 !important;
    --lavender-dark: #7d68aa !important;
    --lavender-pale: #f0ebf8 !important;

    --warning-bg: #fff8e8 !important;
    --warning-border: #f1dfb2 !important;

    --critical-bg: #fff3f3 !important;
    --critical-border: #edcccc !important;
}

html,
body {
    margin: 0 !important;
    padding: 0 !important;
    background: var(--bg) !important;
}

body {
    color: var(--text) !important;
}

.gradio-container {
    max-width: 1080px !important;
    margin: 0 auto !important;
    padding: 0 28px 50px !important;
    background: var(--bg) !important;
    color: var(--text) !important;
}

/* Prevent Gradio's default theme from leaking into the UI */

.gradio-container *,
.gradio-container input,
.gradio-container textarea,
.gradio-container button {
    --body-text-color: #18161b !important;
    --body-text-color-subdued: #48434d !important;
    --block-background-fill: #ffffff !important;
    --input-background-fill: #ffffff !important;
    --input-border-color: #e8e2db !important;
}

footer {
    display: none !important;
}


/* ============================================================
   HERO
   ============================================================ */

.hero {
    text-align: center;
    padding: 48px 20px 34px;
}

.hero-icon {
    width: 68px;
    height: 68px;
    margin: 0 auto 18px;

    display: flex;
    align-items: center;
    justify-content: center;

    border-radius: 20px;

    background: linear-gradient(
        145deg,
        #f3eefb 0%,
        #ece5f8 100%
    ) !important;

    box-shadow:
        0 10px 28px rgba(118, 96, 165, 0.12),
        inset 0 0 0 1px rgba(142, 119, 184, 0.08);
}

.hero-logo {
    width: 56px;
    height: 56px;
    display: block;
}

.hero h1 {
    margin: 0 0 11px !important;

    color: var(--text) !important;

    font-size: 38px !important;
    line-height: 1.12 !important;

    font-weight: 700 !important;
    letter-spacing: -1.4px !important;
}

.hero p {
    max-width: 690px;
    margin: 0 auto !important;

    color: var(--text-soft) !important;

    font-size: 15px !important;
    line-height: 1.65 !important;
}


/* ============================================================
   INPUT CARD
   ============================================================ */

.input-card {
    width: 100% !important;

    background: #ffffff !important;

    border: 1px solid var(--border) !important;
    border-radius: 22px !important;

    padding: 30px 34px 24px !important;

    box-shadow:
        0 12px 38px rgba(52, 45, 39, 0.055) !important;
}

.input-card > div,
.input-card > div > div,
.input-card .block,
.input-card .wrap,
.input-card .form {
    background: #ffffff !important;
    border-color: var(--border) !important;
}


/* Labels */

.input-card label,
.input-card label span {
    color: #211e25 !important;

    font-size: 14px !important;
    font-weight: 650 !important;
}


/* URL input */

.input-card input[type="text"],
.input-card textarea {
    background: #ffffff !important;

    color: #18161b !important;

    border: 1px solid #ded8d1 !important;
    border-radius: 12px !important;

    min-height: 50px !important;

    font-size: 15px !important;

    box-shadow: none !important;
}

.input-card input[type="text"]::placeholder,
.input-card textarea::placeholder {
    color: #6d6772 !important;
    opacity: 1 !important;
}

.input-card input[type="text"]:focus,
.input-card textarea:focus {
    border-color: #a893ce !important;

    box-shadow:
        0 0 0 3px rgba(154, 134, 197, 0.12) !important;
}


/* Slider info */

.input-card small,
.input-card .info {
    color: #5f5965 !important;
    font-size: 12px !important;
}


/* Slider */

.input-card input[type="range"] {
    accent-color: var(--lavender) !important;
}

.input-card [role="slider"] {
    background: var(--lavender) !important;
    border-color: var(--lavender) !important;
}


/* Analyze */

.analyze-btn {
    width: 100% !important;

    min-height: 50px !important;

    margin-top: 12px !important;

    border: none !important;
    border-radius: 12px !important;

    background: var(--lavender) !important;

    color: #ffffff !important;

    font-size: 15px !important;
    font-weight: 650 !important;

    box-shadow:
        0 8px 20px rgba(154, 134, 197, 0.20) !important;

    transition: 0.15s ease !important;
}

.analyze-btn:hover {
    background: var(--lavender-dark) !important;
    transform: translateY(-1px);
}

.analyze-btn,
.analyze-btn * {
    color: #ffffff !important;
}


/* Feature row */

.feature-row {
    display: flex;
    align-items: center;
    justify-content: center;

    gap: 22px;
    flex-wrap: wrap;

    margin-top: 23px;

    color: #5f5965 !important;
    font-size: 12px;
}

.feature {
    display: inline-flex;
    align-items: center;
    gap: 7px;

    white-space: nowrap;
}

.feature-icon {
    color: #7660a5 !important;
    font-size: 14px;
}

.feature-separator {
    color: #c5bfca !important;
}


/* ============================================================
   RESULTS
   ============================================================ */

.results {
    margin-top: 30px !important;
}

.results-title {
    margin: 0 0 4px !important;

    color: var(--text) !important;

    font-size: 27px !important;
    font-weight: 700 !important;

    letter-spacing: -0.6px !important;
}

.results-repo {
    margin: 0 0 22px !important;

    color: var(--muted) !important;

    font-size: 13px !important;
}

.results-repo code {
    background: var(--lavender-pale) !important;
    color: #5d477f !important;

    border-radius: 6px !important;

    padding: 4px 7px !important;
}


/* ============================================================
   METRIC CARDS
   ============================================================ */

.metric-row {
    gap: 12px !important;
}

.metric-card {
    min-height: 105px;

    padding: 18px 18px 16px;

    background: #ffffff !important;

    border: 1px solid var(--border) !important;
    border-radius: 16px !important;

    box-shadow:
        0 7px 22px rgba(52, 45, 39, 0.035) !important;
}

.metric-value {
    color: var(--text) !important;

    font-size: 28px !important;
    font-weight: 700 !important;

    letter-spacing: -0.8px !important;
}

.metric-label {
    margin-top: 5px;

    color: var(--muted) !important;

    font-size: 12px !important;
}

.metric-card.drift .metric-value {
    color: #8d5b62 !important;
}


/* ============================================================
   SECTION CARDS
   ============================================================ */

.section-card {
    margin-top: 16px !important;

    padding: 25px 27px !important;

    background: #ffffff !important;

    border: 1px solid var(--border) !important;
    border-radius: 18px !important;

    box-shadow:
        0 8px 25px rgba(52, 45, 39, 0.035) !important;
}

.section-heading {
    margin: 0 0 4px !important;

    color: var(--text) !important;

    font-size: 19px !important;
    font-weight: 700 !important;

    letter-spacing: -0.25px !important;
}

.section-description {
    margin: 0 0 18px !important;

    color: var(--muted) !important;

    font-size: 12px !important;
}


/* ============================================================
   LANGUAGES
   ============================================================ */

.language-list {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

.language-pill {
    display: inline-flex;
    align-items: center;
    gap: 7px;

    padding: 8px 11px;

    background: #f6f3f8 !important;

    border: 1px solid #e8e1ef !important;
    border-radius: 9px !important;

    color: #433b4d !important;

    font-size: 12px !important;
}

.language-count {
    color: #6f5a91 !important;
    font-weight: 700 !important;
}


/* ============================================================
   DRIFT EVENTS
   ============================================================ */

.drift-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.drift-event {
    padding: 15px 16px;

    border-radius: 12px;

    border: 1px solid var(--border);

    background: #ffffff;
}

.drift-event.critical {
    background: var(--critical-bg) !important;
    border-color: var(--critical-border) !important;
}

.drift-event.warning {
    background: var(--warning-bg) !important;
    border-color: var(--warning-border) !important;
}

.drift-top {
    display: flex;
    align-items: center;
    justify-content: space-between;

    gap: 10px;

    margin-bottom: 7px;
}

.severity {
    display: inline-flex;

    padding: 4px 8px;

    border-radius: 6px;

    font-size: 10px !important;
    font-weight: 750 !important;

    letter-spacing: 0.5px;
}

.severity.critical {
    color: #9a525b !important;
    background: #f9dfe1 !important;
}

.severity.warning {
    color: #936d27 !important;
    background: #f9edc9 !important;
}

.drift-type {
    color: #39333e !important;

    font-size: 13px !important;
    font-weight: 650 !important;
}

.drift-message {
    color: #5f5965 !important;

    font-size: 12px !important;
    line-height: 1.55 !important;
}

.commit {
    color: #725b91 !important;

    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;

    font-size: 11px !important;
}


/* ============================================================
   HOTSPOTS
   ============================================================ */

.hotspot-table {
    width: 100%;

    border-collapse: separate;
    border-spacing: 0;

    overflow: hidden;

    border: 1px solid var(--border);
    border-radius: 11px;
}

.hotspot-table th {
    padding: 11px 12px;

    background: #f5f1f8;

    color: #4a4351;

    text-align: left;

    font-size: 11px;
    font-weight: 700;
}

.hotspot-table td {
    padding: 12px;

    border-top: 1px solid #eee9e3;

    color: #45404a;

    font-size: 12px;

    vertical-align: middle;
}

.hotspot-table tr:first-child td {
    border-top: none;
}

.hotspot-file {
    max-width: 430px;

    color: #43384e;

    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;

    font-size: 11px;

    word-break: break-word;
}

.hotspot-growth {
    color: #7d62a1;

    font-weight: 700;

    white-space: nowrap;
}

.hotspot-score {
    color: #302933;

    font-weight: 700;
}


/* ============================================================
   AI ANALYSIS
   ============================================================ */

.ai-card {
    margin-top: 16px !important;

    padding: 26px 28px !important;

    background:
        linear-gradient(
            135deg,
            #ffffff 0%,
            #fbf9fd 100%
        ) !important;

    border: 1px solid #ded5eb !important;
    border-radius: 18px !important;

    box-shadow:
        0 10px 30px rgba(112, 86, 145, 0.06) !important;
}

.ai-badge {
    display: inline-flex;

    align-items: center;

    gap: 7px;

    padding: 6px 9px;

    margin-bottom: 10px;

    border-radius: 7px;

    background: var(--lavender-pale) !important;

    color: #6d5593 !important;

    font-size: 10px !important;
    font-weight: 750 !important;

    letter-spacing: 0.5px;
}

.ai-card h2 {
    margin: 0 0 15px !important;

    color: #27212d !important;

    font-size: 20px !important;
}

.ai-card h3 {
    color: #40364b !important;

    font-size: 14px !important;
}

.ai-card p,
.ai-card li {
    color: #4c4651 !important;

    font-size: 13px !important;
    line-height: 1.7 !important;
}

.ai-card strong {
    color: #30263a !important;
}

.ai-card code {
    background: #f0ebf6 !important;

    color: #624b80 !important;

    border-radius: 5px !important;

    padding: 2px 5px !important;
}


/* ============================================================
   UNSUPPORTED FILES
   ============================================================ */

.unsupported {
    color: #69636e !important;

    font-size: 11px !important;
    line-height: 1.7 !important;
}

.unsupported strong {
    color: #4c4651 !important;
}


/* ============================================================
   AUTHOR
   ============================================================ */

.footer {
    text-align: center;

    padding: 28px 0 8px;

    color: #4d4854 !important;

    font-size: 12px !important;
}

.footer strong {
    color: #5d477f !important;

    font-weight: 700 !important;
}


/* ============================================================
   MOBILE
   ============================================================ */

@media (max-width: 750px) {

    .gradio-container {
        padding: 0 15px 35px !important;
    }

    .hero {
        padding: 36px 10px 28px;
    }

    .hero h1 {
        font-size: 30px !important;
    }

    .hero p {
        font-size: 14px !important;
    }

    .input-card {
        padding: 22px 20px 20px !important;
    }

    .metric-row {
        flex-direction: column !important;
    }

    .metric-card {
        min-height: auto;
    }

    .feature-row {
        gap: 12px;
    }

    .feature-separator {
        display: none;
    }

    .section-card,
    .ai-card {
        padding: 21px !important;
    }

    .hotspot-table {
        font-size: 11px;
    }

    .hotspot-file {
        max-width: 220px;
    }
}
"""


def _metric(value, label, extra_class=""):
    return f"""
    <div class="metric-card {extra_class}">
        <div class="metric-value">{html.escape(str(value))}</div>
        <div class="metric-label">{html.escape(label)}</div>
    </div>
    """


def _languages_html(languages):
    if not languages:
        return '<span class="language-pill">No supported source files</span>'

    pills = []

    for language, count in sorted(languages.items()):
        pills.append(
            f"""
            <span class="language-pill">
                {html.escape(str(language))}
                <span class="language-count">{count}</span>
            </span>
            """
        )

    return f'<div class="language-list">{"".join(pills)}</div>'


def _drift_html(events):
    if not events:
        return """
        <div class="drift-event">
            <div class="drift-type">No configured drift thresholds were crossed.</div>
            <div class="drift-message">
                The sampled history did not trigger any configured architectural drift rules.
            </div>
        </div>
        """

    cards = []

    for event in events:
        severity = str(event.severity).lower()

        if severity not in {"critical", "warning"}:
            severity = "warning"

        event_type = str(event.type).replace("_", " ")

        cards.append(
            f"""
            <div class="drift-event {severity}">

                <div class="drift-top">

                    <div class="drift-type">
                        {html.escape(event_type)}
                    </div>

                    <span class="severity {severity}">
                        {html.escape(severity.upper())}
                    </span>

                </div>

                <div class="drift-message">
                    {html.escape(str(event.message))}
                </div>

                <div class="commit">
                    commit {html.escape(str(event.commit)[:8])}
                </div>

            </div>
            """
        )

    return f'<div class="drift-list">{"".join(cards)}</div>'


def _hotspots_html(hotspots):
    if not hotspots:
        return """
        <div class="drift-event">
            <div class="drift-type">No evolving hotspots detected.</div>
        </div>
        """

    rows = []

    for hotspot in hotspots[:15]:

        rows.append(
            f"""
            <tr>
                <td>
                    <div class="hotspot-file">
                        {html.escape(str(hotspot.path))}
                    </div>
                </td>

                <td>
                    {html.escape(str(hotspot.latest_lines))}
                </td>

                <td>
                    <span class="hotspot-growth">
                        {hotspot.line_change_percent:+.1f}%
                    </span>
                </td>

                <td>
                    {html.escape(str(hotspot.latest_functions))}
                </td>

                <td>
                    {html.escape(str(hotspot.latest_branches))}
                </td>

                <td>
                    <span class="hotspot-score">
                        {html.escape(str(hotspot.score))}
                    </span>
                </td>
            </tr>
            """
        )

    return f"""
    <table class="hotspot-table">

        <thead>
            <tr>
                <th>File</th>
                <th>Lines</th>
                <th>Growth</th>
                <th>Functions</th>
                <th>Branches</th>
                <th>Score</th>
            </tr>
        </thead>

        <tbody>
            {"".join(rows)}
        </tbody>

    </table>
    """


def _unsupported_html(extensions):
    if not extensions:
        return """
        <div class="unsupported">
            No unsupported extensions detected.
        </div>
        """

    items = ", ".join(
        f"{html.escape(str(extension))}: {count}"
        for extension, count in sorted(extensions.items())
    )

    return f"""
    <div class="unsupported">
        <strong>{len(extensions)} extension types:</strong>
        {items}
    </div>
    """


def _ai_html(text):
    if not text:
        text = "No AI explanation generated."

    # The analyzer already returns Markdown.
    # Keep it in a Markdown component so headings/lists render correctly.
    return text


def run_analysis(url, snapshot_count, progress=gr.Progress()):

    if not url or "github.com/" not in url:
        raise gr.Error(
            "Please enter a public GitHub repository URL."
        )

    name = (
        url.rstrip("/")
        .split("/")[-1]
        .removesuffix(".git")
    )

    clone_dir = tempfile.mkdtemp(
        prefix=f"cea-{name}-"
    )

    try:

        progress(
            0,
            "Cloning repository…"
        )

        Repo.clone_from(
            url,
            clone_dir,
            depth=None,
        )

        progress(
            0.25,
            "Reconstructing Git history…"
        )

        report = analyze_repository(
            clone_dir,
            snapshot_count=int(snapshot_count),
            use_llm=True,
            progress=progress,
        )

        overview = (
            f"""
            <div class="results">

                <div class="results-title">
                    Evolution Report
                </div>

                <div class="results-repo">
                    Repository
                    <code>{html.escape(url)}</code>
                </div>

            </div>
            """
        )

        metrics = f"""
        <div class="metric-row">

            <div class="metric-card">
                <div class="metric-value">
                    {report.total_commits}
                </div>
                <div class="metric-label">
                    Git commits
                </div>
            </div>

            <div class="metric-card">
                <div class="metric-value">
                    {report.snapshots_analyzed}
                </div>
                <div class="metric-label">
                    Historical snapshots
                </div>
            </div>

            <div class="metric-card">
                <div class="metric-value">
                    {report.supported_files}
                </div>
                <div class="metric-label">
                    Source files
                </div>
            </div>

            <div class="metric-card drift">
                <div class="metric-value">
                    {len(report.drift_events)}
                </div>
                <div class="metric-label">
                    Drift events
                </div>
            </div>

        </div>
        """

        languages = f"""
        <div class="section-card">

            <div class="section-heading">
                Source languages
            </div>

            <div class="section-description">
                Files included in AST and evolution analysis.
            </div>

            {_languages_html(report.languages)}

        </div>
        """

        drift = f"""
        <div class="section-card">

            <div class="section-heading">
                Architectural drift
            </div>

            <div class="section-description">
                Significant changes detected across sampled Git history.
            </div>

            {_drift_html(report.drift_events)}

        </div>
        """

        hotspots = f"""
        <div class="section-card">

            <div class="section-heading">
                Evolving hotspots
            </div>

            <div class="section-description">
                Files with the strongest combination of growth and structural change.
            </div>

            {_hotspots_html(report.hotspots)}

        </div>
        """

        unsupported = f"""
        <div class="section-card">

            <div class="section-heading">
                Other repository files
            </div>

            <div class="section-description">
                Non-source files were ignored during AST analysis.
            </div>

            {_unsupported_html(report.unsupported_extensions)}

        </div>
        """

        return (
            overview,
            metrics,
            languages,
            drift,
            hotspots,
            unsupported,
            _ai_html(report.ai_explanation),
        )

    except Exception as exc:

        raise gr.Error(
            f"Analysis failed: {type(exc).__name__}: {exc}"
        )

    finally:

        shutil.rmtree(
            clone_dir,
            ignore_errors=True
        )


# ============================================================
# UI
# ============================================================

with gr.Blocks(
    title="Architecture Evolution Analyzer"
) as demo:

    # HERO

    gr.HTML(
        """
        <div class="hero">

            <div class="hero-icon" aria-label="Architecture evolution logo">
    <svg class="hero-logo" viewBox="0 0 64 64" role="img">
        <defs>
            <linearGradient id="logoGradient" x1="8" y1="54" x2="56" y2="10">
                <stop offset="0%" stop-color="#8d73bd"/>
                <stop offset="100%" stop-color="#b39cdd"/>
            </linearGradient>
        </defs>

        <!-- code/document -->
        <rect x="14" y="10" width="31" height="38" rx="7"
              fill="url(#logoGradient)" opacity="0.95"/>

        <!-- code symbol -->
        <path d="M25 21l-6 6 6 6"
              fill="none"
              stroke="#ffffff"
              stroke-width="3.2"
              stroke-linecap="round"
              stroke-linejoin="round"/>

        <path d="M34 21l6 6-6 6"
              fill="none"
              stroke="#ffffff"
              stroke-width="3.2"
              stroke-linecap="round"
              stroke-linejoin="round"/>

        <!-- evolution path -->
        <path d="M10 49 C20 42, 25 52, 34 45 S48 40, 55 31"
              fill="none"
              stroke="#765ca8"
              stroke-width="3"
              stroke-linecap="round"/>

        <!-- commit nodes -->
        <circle cx="10" cy="49" r="4" fill="#ffffff" stroke="#765ca8" stroke-width="2.5"/>
        <circle cx="34" cy="45" r="4" fill="#ffffff" stroke="#765ca8" stroke-width="2.5"/>
        <circle cx="55" cy="31" r="4" fill="#ffffff" stroke="#765ca8" stroke-width="2.5"/>

        <!-- small architecture/evolution spark -->
        <path d="M48 12l1.8 4.2L54 18l-4.2 1.8L48 24l-1.8-4.2L42 18l4.2-1.8z"
              fill="#a38bce"/>
    </svg>
</div>

            <h1>
                Architecture Evolution Analyzer
            </h1>

            <p>
                Trace how your software architecture changes,
                grows, and drifts across Git history.
            </p>

        </div>
        """
    )

    # INPUT

    with gr.Column(
        elem_classes="input-card"
    ):

        url = gr.Textbox(
            label="GitHub repository",

            placeholder=(
                "https://github.com/owner/repository"
            ),
        )

        snapshot_count = gr.Slider(
            minimum=5,
            maximum=60,
            value=15,
            step=5,

            label="Historical snapshots",

            info=(
                "More snapshots provide finer-grained evolution analysis."
            ),
        )

        button = gr.Button(
            "Analyze repository  →",

            elem_classes="analyze-btn",
        )

        gr.HTML(
            """
            <div class="feature-row">

                <div class="feature">
                    <span class="feature-icon">◷</span>
                    <span>Git history</span>
                </div>

                <span class="feature-separator">·</span>

                <div class="feature">
                    <span class="feature-icon">&lt;/&gt;</span>
                    <span>AST metrics</span>
                </div>

                <span class="feature-separator">·</span>

                <div class="feature">
                    <span class="feature-icon">◇</span>
                    <span>Drift detection</span>
                </div>

                <span class="feature-separator">·</span>

                <div class="feature">
                    <span class="feature-icon">✦</span>
                    <span>AI analysis</span>
                </div>

            </div>
            """
        )

    # RESULTS

    results = gr.Column(
        elem_classes="results",
        visible=False,
    )

    with results:

        result_header = gr.HTML()

        metric_html = gr.HTML()

        language_html = gr.HTML()

        drift_html = gr.HTML()

        hotspot_html = gr.HTML()

        unsupported_html = gr.HTML()

        with gr.Column(
            elem_classes="ai-card"
        ):

            gr.HTML(
                """
                <div class="ai-badge">
                    <span>✦</span> AI-POWERED
                </div>

                <h2>
                    Architectural interpretation
                </h2>
                """
            )

            ai_markdown = gr.Markdown()

    # AUTHOR

    gr.HTML(
        """
        <div class="footer">
            Built by
            <strong>Gunjan Verma</strong>
            <span>·</span>
            Architecture Evolution Analyzer
        </div>
        """
    )

    # ANALYZE

    button.click(
        run_analysis,

        inputs=[
            url,
            snapshot_count,
        ],

        outputs=[
            result_header,
            metric_html,
            language_html,
            drift_html,
            hotspot_html,
            unsupported_html,
            ai_markdown,
        ],
    ).then(
        lambda: gr.update(visible=True),
        outputs=results,
    )


# ============================================================
# LAUNCH
# ============================================================

if __name__ == "__main__":

    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        css=CSS,
    )