"""Shared CSS for the Streamlit dashboard."""

CUSTOM_CSS = """
<style>
    .block-container { padding-top: 2rem; padding-bottom: 3rem; }

    .recon-badge {
        display: inline-block;
        padding: 0.45rem 1.2rem;
        border-radius: 999px;
        font-weight: 700;
        font-size: 1.1rem;
        letter-spacing: 0.03em;
        margin-bottom: 0.5rem;
    }
    .recon-badge-match { background-color: #C6EFCE; color: #0B6B0B; border: 1px solid #6FC46F; }
    .recon-badge-xmatch { background-color: #FFC7CE; color: #9C0006; border: 1px solid #E68A8F; }

    .recon-card {
        background: var(--background-color, #ffffff);
        border: 1px solid rgba(49, 51, 63, 0.15);
        border-radius: 10px;
        padding: 1rem 1.1rem;
        text-align: left;
    }
    .recon-card-label { font-size: 0.8rem; opacity: 0.7; margin-bottom: 0.25rem; }
    .recon-card-value { font-size: 1.6rem; font-weight: 700; }

    .field-chip {
        display: inline-block;
        padding: 0.15rem 0.6rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
        margin: 0.1rem 0.25rem 0.1rem 0;
    }
    .field-chip-exact { background-color: #D9EAD3; color: #274E13; }
    .field-chip-fuzzy { background-color: #FFF2CC; color: #7F6000; }
    .field-chip-manual { background-color: #CFE2F3; color: #1155CC; }
    .field-chip-unmapped { background-color: #F4CCCC; color: #990000; }
</style>
"""
