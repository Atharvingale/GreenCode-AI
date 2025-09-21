import streamlit as st

st.set_page_config(page_title="HTML Test", layout="wide")

# Test basic HTML rendering
st.markdown("""
<div style="background: #1E1E1E; color: white; padding: 2rem; border-radius: 12px; margin: 1rem 0;">
    <h3>Test HTML Rendering</h3>
    <p>If you can see this properly styled, HTML rendering is working.</p>
</div>
""", unsafe_allow_html=True)

# Test if it's a specific section causing issues
st.markdown("## Regular Markdown Works")
st.write("This should display normally.")

# Test a simple modern card
st.markdown("""
<div style="background: #1E1E1E; border: 1px solid #333333; border-radius: 16px; padding: 2rem; margin: 1rem 0;">
    <h4 style="color: #00D4AA;">Modern Card Test</h4>
    <p style="color: #B0B0B0;">This is a test of the modern card styling.</p>
</div>
""", unsafe_allow_html=True)