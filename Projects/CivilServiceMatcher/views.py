from flask import Blueprint, render_template, request, redirect, url_for
import asyncio
from .scraper_tool import scrape_jobs
from .job_match_agent import run_async_langgraph_pipeline

matcher_bp = Blueprint(
    'civil_service_matcher',
    __name__,
    template_folder='templates'
)

# In app.py, register this with:
# app.register_blueprint(matcher_bp, url_prefix='/projects/civil-service-matcher-app')

@matcher_bp.route('/match', methods=['GET', 'POST'])
def match():
    if request.method == 'POST':
        cv_text = request.form['cv']

        # 🔍 Run the job scraper for developer roles
        jobs = scrape_jobs("developer")

        # ⛓️ Run async LangGraph pipeline (match + STAR + gap)
        results = asyncio.run(run_async_langgraph_pipeline(cv_text, jobs))

        return render_template('results.html', jobs=results, cv=cv_text)

    return render_template('match.html')
