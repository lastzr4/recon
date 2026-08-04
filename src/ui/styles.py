"""Shared CSS for the Streamlit dashboard - a clean, professional design system."""

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --recon-primary: #4338CA;
        --recon-primary-dark: #3730A3;
        --recon-primary-soft: #EEF2FF;
        --recon-success: #059669;
        --recon-success-soft: #ECFDF5;
        --recon-success-border: #A7F3D0;
        --recon-danger: #DC2626;
        --recon-danger-soft: #FEF2F2;
        --recon-danger-border: #FECACA;
        --recon-warning: #D97706;
        --recon-warning-soft: #FFFBEB;
        --recon-warning-border: #FDE68A;
        --recon-text: #0F172A;
        --recon-text-muted: #64748B;
        --recon-border: #E2E8F0;
        --recon-surface: #FFFFFF;
        --recon-surface-alt: #F8FAFC;
    }

    html, body, [class*="css"] { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }

    /* ---- Hide default Streamlit chrome for a cleaner shell ---- */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header[data-testid="stHeader"] { background: transparent; }
    div[data-testid="stDecoration"] { display: none; }
    div[data-testid="stStatusWidget"] { display: none; }
    a[data-testid="stHeaderActionElements"] { display: none; }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 4rem;
        max-width: 1180px;
    }

    /* ---- App header ---- */
    .recon-app-header {
        display: flex;
        align-items: center;
        gap: 0.85rem;
        padding-bottom: 1.1rem;
        margin-bottom: 1.6rem;
        border-bottom: 1px solid var(--recon-border);
    }
    .recon-app-mark {
        width: 42px;
        height: 42px;
        min-width: 42px;
        border-radius: 11px;
        background: linear-gradient(135deg, var(--recon-primary) 0%, #6366F1 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: #fff;
        font-weight: 800;
        font-size: 1.05rem;
        letter-spacing: -0.02em;
        box-shadow: 0 4px 10px rgba(67, 56, 202, 0.25);
    }
    .recon-app-title { font-size: 1.35rem; font-weight: 800; color: var(--recon-text); letter-spacing: -0.01em; line-height: 1.2; }
    .recon-app-subtitle { font-size: 0.87rem; color: var(--recon-text-muted); margin-top: 0.1rem; }

    /* ---- Step header (numbered section titles) ---- */
    .recon-step {
        display: flex;
        align-items: center;
        gap: 0.65rem;
        margin: 1.9rem 0 0.35rem 0;
    }
    .recon-step-number {
        width: 26px;
        height: 26px;
        min-width: 26px;
        border-radius: 50%;
        background: var(--recon-primary-soft);
        color: var(--recon-primary);
        font-weight: 700;
        font-size: 0.82rem;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 1px solid #C7D2FE;
    }
    .recon-step-title { font-size: 1.05rem; font-weight: 700; color: var(--recon-text); letter-spacing: -0.01em; }
    .recon-step-desc { font-size: 0.85rem; color: var(--recon-text-muted); margin: 0.15rem 0 0.9rem 2.35rem; }

    /* ---- Bordered containers (used as cards throughout) ---- */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 12px !important;
        border-color: var(--recon-border) !important;
        background: var(--recon-surface);
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
    }

    /* ---- Overall status badge ---- */
    .recon-badge-wrap { display: flex; justify-content: center; margin: 0.4rem 0 1.3rem 0; }
    .recon-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.55rem 1.4rem;
        border-radius: 999px;
        font-weight: 700;
        font-size: 1rem;
        letter-spacing: 0.02em;
    }
    .recon-badge-icon { font-size: 1.05rem; line-height: 1; }
    .recon-badge-match { background-color: var(--recon-success-soft); color: var(--recon-success); border: 1px solid var(--recon-success-border); }
    .recon-badge-xmatch { background-color: var(--recon-danger-soft); color: var(--recon-danger); border: 1px solid var(--recon-danger-border); }

    /* ---- Metric cards ---- */
    .recon-card {
        background: var(--recon-surface);
        border: 1px solid var(--recon-border);
        border-left: 3px solid var(--recon-accent, var(--recon-primary));
        border-radius: 9px;
        padding: 0.85rem 1rem;
        text-align: left;
        height: 100%;
    }
    .recon-card-label {
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: var(--recon-text-muted);
        margin-bottom: 0.3rem;
    }
    .recon-card-value { font-size: 1.55rem; font-weight: 800; color: var(--recon-text); letter-spacing: -0.02em; }

    /* ---- Field mapping chips ---- */
    .field-chip {
        display: inline-block;
        padding: 0.2rem 0.65rem;
        border-radius: 999px;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    .field-chip-exact { background-color: var(--recon-success-soft); color: var(--recon-success); }
    .field-chip-fuzzy { background-color: var(--recon-warning-soft); color: var(--recon-warning); }
    .field-chip-manual { background-color: var(--recon-primary-soft); color: var(--recon-primary); }
    .field-chip-unmapped { background-color: #F1F5F9; color: var(--recon-text-muted); }

    /* ---- Mapping row ---- */
    .recon-map-row {
        display: flex;
        align-items: center;
        padding: 0.35rem 0;
        border-bottom: 1px solid var(--recon-surface-alt);
    }
    .recon-map-field { font-weight: 600; font-size: 0.9rem; color: var(--recon-text); }
    .recon-map-arrow { color: var(--recon-text-muted); font-size: 0.85rem; padding: 0 0.4rem; }

    /* ---- Buttons ---- */
    div.stButton > button, div.stDownloadButton > button {
        border-radius: 8px;
        font-weight: 600;
        padding: 0.55rem 1.1rem;
        border: 1px solid var(--recon-border);
    }
    div.stButton > button[kind="primary"] {
        background: var(--recon-primary);
        border-color: var(--recon-primary);
    }
    div.stButton > button[kind="primary"]:hover {
        background: var(--recon-primary-dark);
        border-color: var(--recon-primary-dark);
    }
    div.stDownloadButton > button {
        background: var(--recon-success);
        color: #fff;
        border-color: var(--recon-success);
    }
    div.stDownloadButton > button:hover {
        background: #047857;
        border-color: #047857;
    }

    /* ---- Segmented filter control (radio, horizontal) ---- */
    div[role="radiogroup"] {
        gap: 0.3rem;
        background: var(--recon-surface-alt);
        padding: 0.28rem;
        border-radius: 9px;
        border: 1px solid var(--recon-border);
        display: inline-flex;
    }
    div[role="radiogroup"] label {
        border-radius: 6px;
        padding: 0.15rem 0.55rem;
        margin: 0 !important;
    }

    /* ---- File uploader ---- */
    div[data-testid="stFileUploaderDropzone"] {
        background: var(--recon-surface-alt);
        border-radius: 10px;
        border: 1.5px dashed var(--recon-border);
    }

    /* ---- Section captions ---- */
    .recon-section-desc { font-size: 0.85rem; color: var(--recon-text-muted); margin-bottom: 0.75rem; }

    /* ---- Alerts spacing tighten ---- */
    div[data-testid="stAlert"] { border-radius: 9px; }

    /* ---- Divider replacement spacing ---- */
    hr { margin: 0.4rem 0; border-color: var(--recon-border); }
</style>
"""
