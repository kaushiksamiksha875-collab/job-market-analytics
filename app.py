from flask import Flask, request, render_template_string
import psycopg2
import os

from datetime import datetime

app = Flask(__name__)


# -----------------------------
# DATABASE CONNECTION
# -----------------------------
def get_connection():
    database_url = os.environ.get("DATABASE_URL")

    if database_url:
        return psycopg2.connect(database_url)

    return psycopg2.connect(
        host="localhost",
        port="5432",
        database="job_market_db",
        user="postgres",
        password=os.environ.get("POSTGRES_PASSWORD")
    )



# -----------------------------
# WEBSITE
# -----------------------------

@app.route("/")
def home():

    search = request.args.get("search", "").strip()
    employment = request.args.get("employment", "").strip()

    connection = get_connection()
    cursor = connection.cursor()

    # Total live jobs
    cursor.execute("SELECT COUNT(*) FROM live_jobs;")
    total_jobs = cursor.fetchone()[0]

    # AI-related live jobs
    cursor.execute("""
        SELECT COUNT(DISTINCT job_id)
        FROM live_job_skills
        WHERE LOWER(skill) IN (
            'artificial intelligence',
            'machine learning',
            'generative ai',
            'llm',
            'nlp'
        );
    """)
    ai_jobs = cursor.fetchone()[0]

    # Last update time
    cursor.execute("""
        SELECT MAX(fetched_at)
        FROM live_jobs;
    """)
    last_updated = cursor.fetchone()[0]

    # Employment types
    cursor.execute("""
        SELECT DISTINCT employment_type
        FROM live_jobs
        WHERE employment_type IS NOT NULL
        ORDER BY employment_type;
    """)
    employment_types = [row[0] for row in cursor.fetchall()]

    # Jobs
    query = """
        SELECT
            lj.job_id,
            lj.company,
            lj.title,
            lj.employment_type,
            lj.date_posted,
            lj.job_url,
            lj.fetched_at,
            COALESCE(
                STRING_AGG(
                    DISTINCT ljs.skill,
                    ', '
                    ORDER BY ljs.skill
                ),
                ''
            ) AS skills

        FROM live_jobs lj

        LEFT JOIN live_job_skills ljs
            ON lj.job_id = ljs.job_id

        WHERE 1=1
    """

    parameters = []

    if search:
        query += """
            AND (
                LOWER(lj.title) LIKE LOWER(%s)
                OR LOWER(lj.company) LIKE LOWER(%s)
            )
        """

        search_value = f"%{search}%"
        parameters.extend([search_value, search_value])

    if employment:
        query += """
            AND lj.employment_type = %s
        """
        parameters.append(employment)

    query += """
        GROUP BY
            lj.job_id,
            lj.company,
            lj.title,
            lj.employment_type,
            lj.date_posted,
            lj.job_url,
            lj.fetched_at

        ORDER BY
            lj.date_posted DESC NULLS LAST,
            lj.fetched_at DESC
        LIMIT 100;
    """

    cursor.execute(query, parameters)
    jobs = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template_string(
        PAGE,
        total_jobs=total_jobs,
        ai_jobs=ai_jobs,
        last_updated=last_updated,
        jobs=jobs,
        employment_types=employment_types,
        search=search,
        employment=employment
    )


# -----------------------------
# HTML + CSS
# -----------------------------

PAGE = """
<!DOCTYPE html>

<html>

<head>

    <meta charset="UTF-8">

    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">

    <title>Job Market & AI Skills Analytics</title>

    <link rel="preconnect"
          href="https://fonts.googleapis.com">

    <link rel="preconnect"
          href="https://fonts.gstatic.com"
          crossorigin>

    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap"
          rel="stylesheet">


    <style>

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            background: #f5f3ee;
            color: #202522;
            font-family: "DM Sans", sans-serif;
        }

        .container {
            max-width: 1180px;
            margin: auto;
            padding: 34px 24px 60px;
        }

        /* HEADER */

        header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 30px;
            margin-bottom: 42px;
        }

        .brand {
            max-width: 700px;
        }

        .eyebrow {
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: #b35c3d;
            margin-bottom: 12px;
        }

        h1 {
            font-family: "Space Grotesk", sans-serif;
            font-size: 42px;
            line-height: 1.05;
            margin: 0 0 14px;
            letter-spacing: -1.5px;
        }

        .subtitle {
            color: #666c68;
            font-size: 16px;
            line-height: 1.6;
            max-width: 620px;
        }

        .live-status {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 9px 13px;
            border: 1px solid #d7d4cd;
            border-radius: 30px;
            background: #fffefa;
            font-size: 13px;
            white-space: nowrap;
        }

        .dot {
            width: 8px;
            height: 8px;
            background: #3f8f65;
            border-radius: 50%;
        }

        /* STATS */

        .stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 14px;
            margin-bottom: 34px;
        }

        .stat {
            background: #fffefa;
            border: 1px solid #dedbd3;
            padding: 23px;
            border-radius: 12px;
        }

        .stat-label {
            font-size: 12px;
            color: #777b77;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
        }

        .stat-number {
            font-family: "Space Grotesk", sans-serif;
            font-size: 34px;
            margin-top: 8px;
            font-weight: 700;
        }

        .stat-note {
            color: #858983;
            font-size: 12px;
            margin-top: 4px;
        }

        /* SEARCH */

        .toolbar {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
        }

        .search {
            flex: 1;
            padding: 13px 16px;
            border: 1px solid #d5d2ca;
            border-radius: 8px;
            background: #fffefa;
            font-family: inherit;
            font-size: 14px;
            outline: none;
        }

        .search:focus {
            border-color: #b35c3d;
        }

        select {
            padding: 13px 15px;
            border: 1px solid #d5d2ca;
            border-radius: 8px;
            background: #fffefa;
            font-family: inherit;
            color: #333;
        }

        button {
            padding: 13px 20px;
            border: none;
            border-radius: 8px;
            background: #263b35;
            color: white;
            font-family: inherit;
            font-weight: 600;
            cursor: pointer;
        }

        button:hover {
            background: #172923;
        }

        /* SECTION */

        .section-heading {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            margin-bottom: 16px;
        }

        .section-heading h2 {
            font-family: "Space Grotesk", sans-serif;
            font-size: 23px;
            margin: 0;
        }

        .section-heading span {
            color: #7c817d;
            font-size: 13px;
        }

        /* JOB */

        .job {
            background: #fffefa;
            border: 1px solid #dedbd3;
            border-radius: 12px;
            padding: 22px;
            margin-bottom: 12px;
            transition: transform 0.15s ease,
                        box-shadow 0.15s ease;
        }

        .job:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 22px rgba(35, 38, 35, 0.08);
        }

        .job-top {
            display: flex;
            justify-content: space-between;
            gap: 20px;
        }

        .job h3 {
            font-family: "Space Grotesk", sans-serif;
            font-size: 20px;
            margin: 0 0 6px;
        }

        .company {
            color: #5e6560;
            font-weight: 600;
            font-size: 14px;
        }

        .employment {
            font-size: 12px;
            color: #6b716d;
            border: 1px solid #d8d5ce;
            padding: 6px 9px;
            border-radius: 20px;
            height: fit-content;
        }

        .details {
            margin-top: 14px;
            color: #737873;
            font-size: 13px;
        }

        .skills {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-top: 15px;
        }

        .skill {
            background: #eee9df;
            color: #4e554f;
            padding: 5px 9px;
            border-radius: 5px;
            font-size: 11px;
        }

        .job-footer {
            margin-top: 18px;
        }

        .view-job {
            color: #b35c3d;
            font-weight: 700;
            font-size: 13px;
            text-decoration: none;
        }

        .view-job:hover {
            text-decoration: underline;
        }

        .empty {
            padding: 50px;
            text-align: center;
            color: #777;
            background: #fffefa;
            border: 1px solid #dedbd3;
            border-radius: 12px;
        }

        footer {
            margin-top: 45px;
            padding-top: 20px;
            border-top: 1px solid #ddd9d0;
            color: #888d88;
            font-size: 12px;
        }

        @media (max-width: 700px) {

            header {
                flex-direction: column;
            }

            h1 {
                font-size: 34px;
            }

            .stats {
                grid-template-columns: 1fr;
            }

            .toolbar {
                flex-direction: column;
            }

            .job-top {
                flex-direction: column;
            }

        }

    </style>

</head>


<body>

<div class="container">


    <header>

        <div class="brand">

            <div class="eyebrow">
                Job Market Intelligence
            </div>

            <h1>
                Job Market & AI Skills Analytics
            </h1>

          <div class="subtitle">
    A live view of entry-level hiring activity, in-demand skills,
    and how AI is appearing across today's job market.
</div>
        </div>


        <div class="live-status">

            <span class="dot"></span>

           AUTOMATICALLY UPDATED
        </div>

    </header>



    <section class="stats">

        <div class="stat">

            <div class="stat-label">
                Live Jobs
            </div>

            <div class="stat-number">
                {{ total_jobs }}
            </div>

            <div class="stat-note">
                Currently tracked
            </div>

        </div>


        <div class="stat">

            <div class="stat-label">
                AI-related Jobs
            </div>

            <div class="stat-number">
                {{ ai_jobs }}
            </div>

            <div class="stat-note">
                Based on detected AI skills
            </div>

        </div>


        <div class="stat">

            <div class="stat-label">
                Last Data Refresh
            </div>

          <div class="stat-number"
     style="font-size:24px; margin-top:12px;">

    {% if last_updated %}
        {{ last_updated.strftime("%d %b") }}
    {% else %}
        —
    {% endif %}

</div>
           <div class="stat-note">
    Last successful data update
</div>

        </div>

    </section>



    <form class="toolbar" method="GET">

        <input
            class="search"
            type="text"
            name="search"
            placeholder="Search job title or company..."
            value="{{ search }}"
        >

        <select name="employment">

            <option value="">
                All employment types
            </option>

            {% for type in employment_types %}

                <option
                    value="{{ type }}"
                    {% if employment == type %}selected{% endif %}
                >
                    {{ type }}
                </option>

            {% endfor %}

        </select>

       <button type="submit">
    Find jobs
</button>

    </form>



    <div class="section-heading">

        <h2>
            Latest opportunities
        </h2>

      <span>
    {{ jobs|length }} opportunities found
</span>

    </div>



    {% if jobs %}

        {% for job in jobs %}

            <article class="job">

                <div class="job-top">

                    <div>

                        <h3>
                            {{ job[2] }}
                        </h3>

                        <div class="company">
                            {{ job[1] }}
                        </div>

                    </div>


                    {% if job[3] %}

                        <div class="employment">
                            {{ job[3] }}
                        </div>

                    {% endif %}

                </div>


                <div class="details">

                    {% if job[4] %}
                        Posted {{ job[4].strftime("%d %b %Y") }}
                    {% endif %}

                </div>


                {% if job[7] %}

                    <div class="skills">

                        {% for skill in job[7].split(", ") %}

                            <span class="skill">
                                {{ skill }}
                            </span>

                        {% endfor %}

                    </div>

                {% endif %}


                {% if job[5] %}

                    <div class="job-footer">

                      <a
    class="view-job"
    href="{{ job[5] }}"
    target="_blank"
>
    View job →
</a>

                    </div>

                {% endif %}

            </article>

        {% endfor %}

    {% else %}

        <div class="empty">
            No jobs matched your search.
        </div>

    {% endif %}



    <footer>

       Data is updated automatically from public job listings.

    </footer>


</div>

</body>

</html>
"""


if __name__ == "__main__":
    app.run(debug=True)