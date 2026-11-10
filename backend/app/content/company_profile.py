"""Charles Schwab company knowledge for the interview: who they are, what they value,
how they hire, and where the SDET — Cyber Security QA role sits.

Everything here is drawn from public sources (aboutschwab.com / schwabjobs.com and
Wikipedia for scale figures) and is presented as company research, not insider
information. Counts and figures are marked with their as-of date.
"""
from __future__ import annotations

COMPANY_PROFILE: dict = {
    "name": "The Charles Schwab Corporation",
    "target_role": "SDET — Cyber Security QA",
    "mission": "Champion individuals' goals with passion and integrity.",
    "philosophy": "Through Clients' Eyes",
    "tagline": "Own Your Tomorrow",
    "nickname": "Schwabbies (what Schwab employees call themselves)",
    "business": (
        "American multinational financial services company: investing, banking, wealth "
        "management and related advisory services for retail and institutional clients. "
        "One of the largest banks in the United States by assets."
    ),
    "values": [
        {
            "name": "Trust",
            "meaning": "Earning our clients' trust by serving them in an ethical, empathetic, and proactive way.",
            "qa_link": "Security testing IS trust: every access-control defect you catch protects a client's money and data.",
        },
        {
            "name": "Innovation",
            "meaning": "Constantly improving the client experience through client-centric innovations.",
            "qa_link": "Your Selenium\u2192Playwright migration is exactly this: modernizing quality tooling to ship faster, safely.",
        },
        {
            "name": "Teamwork",
            "meaning": "Empowering the success of fellow Schwabbies and championing collaboration.",
            "qa_link": "SDETs unblock whole teams — frameworks, CI pipelines and reusable checks are teamwork, engineered.",
        },
        {
            "name": "Stewardship",
            "meaning": "Being good stewards of Schwab's brand by maintaining a human-centric approach to finance.",
            "qa_link": "IAM governance (who has access to what, and why) is stewardship of client trust at scale.",
        },
    ],
    "numbers": [
        {"label": "Client assets", "value": "$10.10 trillion", "as_of": "Dec 31, 2024"},
        {"label": "Active brokerage accounts", "value": "36.5 million", "as_of": "Dec 31, 2024"},
        {"label": "Workplace retirement plan participants", "value": "5.4 million", "as_of": "Dec 31, 2024"},
        {"label": "Banking accounts", "value": "2.0 million", "as_of": "Dec 31, 2024"},
        {"label": "Branches", "value": "380+ (U.S. and U.K.)", "as_of": "2025"},
        {"label": "Headquarters", "value": "Westlake, Texas", "as_of": "—"},
        {"label": "Founded", "value": "San Francisco, 1971", "as_of": "—"},
    ],
    "history": [
        {
            "year": "1971",
            "event": "Founded as First Commander Corporation in San Francisco.",
            "say_it": "Schwab started as a small San Francisco firm in 1971.",
        },
        {
            "year": "1973",
            "event": "Renamed Charles Schwab & Co.",
            "say_it": None,
        },
        {
            "year": "1975",
            "event": (
                "Leveraged 1970s brokerage deregulation to pioneer discount sales of equity "
                "securities — the original industry disrupter."
            ),
            "say_it": "Schwab is the original disrupter: discount brokerage after 1970s deregulation.",
        },
        {
            "year": "1970s–80s",
            "event": (
                "Flagship opening in Sacramento, expansion to Seattle, and heavy investment in "
                "technology, automation and digital record keeping."
            ),
            "say_it": "Technology has been the growth engine since the beginning — automation and digital record keeping in the 1980s.",
        },
        {
            "year": "—",
            "event": "First brokerage to offer round-the-clock order entry and quotation.",
            "say_it": "They were first to 24/7 order entry — always-on systems make quality engineering non-negotiable.",
        },
        {
            "year": "1983",
            "event": "Purchased by Bank of America for $55 million.",
            "say_it": None,
        },
        {
            "year": "1986",
            "event": "Founder bought the company back for $280 million.",
            "say_it": None,
        },
        {
            "year": "Today",
            "event": (
                "Headquartered in Westlake, Texas; 380+ branches, primarily in financial centers "
                "in the United States and the United Kingdom."
            ),
            "say_it": None,
        },
    ],
    "tech_org": {
        "sts": {
            "name": "Schwab Technology Services (STS)",
            "description": (
                "Powers every part of the business: secure, world-class digital experiences and "
                "resilient systems. Teams span software engineering, AI, architecture, cloud and "
                "cybersecurity, plus dedicated iOS and Android teams so clients can trade and "
                "manage investments anywhere. Agile development methodologies, modern tech stack."
            ),
        },
        "scs": {
            "name": "Schwab Cybersecurity Services (SCS)",
            "description": (
                "Mission: safeguard information and cultivate client trust so people feel secure "
                "in every interaction. Spans securing access and protecting data to safeguarding "
                "applications, endpoints and the cloud — reinforced by proactive threat detection, "
                "penetration testing, cyber threat intelligence, and strong risk management and governance."
            ),
        },
        "role_families": [
            "SDET",
            "Identity and Access Management (IAM)",
            "Quality Automation",
            "Data Loss Prevention (DLP)",
            "Product Support",
            "Site Reliability",
            "Application Security",
        ],
        "your_role_note": (
            "Schwab's own engineering careers page lists SDET, IAM, Quality Automation and DLP as "
            "named role families inside STS/SCS — your target role sits exactly there, between "
            "quality engineering and cyber security."
        ),
        "stack": ["Java", ".NET / C#", "Python", "Spark", "SQL", "full-stack", "iOS & Android", "agile"],
    },
    "hiring": {
        "methodology": "Behavioral-based interviewing (S.T.A.R. — Situation, Task, Action, Result)",
        "steps": [
            {
                "n": 1,
                "name": "Finding your fit",
                "detail": "Research career areas (Technology, Service, Risk, Retail Branch) and search openings.",
            },
            {
                "n": 2,
                "name": "Build a candidate profile",
                "detail": "Resume that reflects strengths and transferable skills; join the Talent Network.",
            },
            {
                "n": 3,
                "name": "Apply",
                "detail": "Resume and candidate profile go to the Talent Advisor team for review.",
            },
            {
                "n": 4,
                "name": "Interview",
                "detail": (
                    "Talent Advisor phone screen first, then the Hiring Manager; additional rounds "
                    "depend on the team. Behavioral (S.T.A.R.) methodology throughout."
                ),
            },
            {
                "n": 5,
                "name": "Offer",
                "detail": (
                    "Verbal or written offer, then background check and (where applicable) drug "
                    "screening before starting — usually about two weeks."
                ),
            },
        ],
        "background_check": (
            "2–4 weeks depending on personal and geographical history: criminal, educational, "
            "residential, credit history (if applicable), fingerprint processing, and FINRA "
            "license review (if applicable)."
        ),
        "transferable_skills": (
            "Schwab publicly encourages transferable skillsets: 'If you have 90% of what is "
            "required, we encourage you to apply.' A finance degree is not required unless the "
            "listing says so."
        ),
        "ai_policy": (
            "Schwab's careers FAQ asks candidates NOT to use AI tools during interviews or "
            "assessments — responses should reflect your own skills and thinking. Use this gym "
            "to prepare beforehand, then answer as yourself on the day."
        ),
    },
    "interview_angles": [
        {
            "question": "Why do you want to work at Schwab?",
            "talking_points": [
                "Mission fit: 'champion individuals' goals with passion and integrity' — security is how a brokerage keeps that promise at scale.",
                "Your IAM/CyberArk/Saviynt background maps directly onto Schwab's named SDET/IAM/DLP role families.",
                "Scale that matters: $10.1T in client assets and 36.5M brokerage accounts — every access-control bug is someone's retirement.",
                "Values you can cite from memory: Trust, Innovation, Teamwork, Stewardship — connect each to a real story from your work.",
                "Technology-first history: from 1980s automation to today's STS/SCS orgs — quality engineering has always been core to Schwab.",
            ],
            "model_answer": (
                "Schwab's mission is to champion individuals' goals with passion and integrity, and "
                "at a firm holding $10.1 trillion in client assets for 36.5 million accounts, that "
                "promise is kept or broken by security and reliability — which is exactly where I've "
                "spent my career. I've spent two years as an SDET specializing in identity and access "
                "management: Saviynt-based joiner-mover-leaver workflows, CyberArk privileged access, "
                "access certifications and provisioning, automated with Java, Selenium, Playwright and "
                "REST Assured across 300+ test cases. Schwab's own engineering organization lists SDET, "
                "IAM and Quality Automation as role families in Schwab Technology Services and Schwab "
                "Cybersecurity Services — this role sits at the intersection I already work in. And the "
                "values — Trust, Innovation, Teamwork, Stewardship — are the ones I already operate by: "
                "trust through honest test reporting, innovation through my Selenium-to-Playwright "
                "migration, teamwork through the frameworks and CI pipelines my teams build on. I want "
                "my work to protect something that matters: people's financial futures."
            ),
        },
        {
            "question": "What do you know about Schwab?",
            "talking_points": [
                "Founded 1971 in San Francisco as First Commander Corporation; renamed Charles Schwab & Co. in 1973.",
                "Pioneer of discount brokerage after 1970s deregulation — the industry 'disrupter' before that word existed.",
                "First to offer round-the-clock order entry and quotation.",
                "Bought by Bank of America in 1983 for $55M; founder bought it back in 1986 for $280M.",
                "Today: HQ in Westlake, Texas; 380+ branches in the U.S. and U.K.; one of the largest U.S. banks by assets.",
                "Employees call themselves Schwabbies; hiring is behavioral (S.T.A.R.) via Talent Advisors.",
            ],
            "model_answer": (
                "Schwab was founded in San Francisco in 1971, took the Charles Schwab name in 1973, and "
                "built its identity on deregulation-era discount brokerage — making investing accessible "
                "to everyone, which is still the 'Own Your Tomorrow' client promise today. It grew through "
                "technology: automation and digital record keeping in the 1980s, and it was the first "
                "brokerage with round-the-clock order entry. There's even a great ownership story — Bank "
                "of America bought it in 1983 for $55 million, and the founder bought it back in 1986 for "
                "$280 million. Today it's headquartered in Westlake, Texas, runs 380+ branches in the U.S. "
                "and U.K., and holds about $10.1 trillion in client assets across 36.5 million brokerage "
                "accounts — one of the largest U.S. banks by assets."
            ),
        },
        {
            "question": "Why cyber security QA at a financial services company?",
            "talking_points": [
                "Money is trust: a brokerage's product is confidence — security defects hit clients' life savings, not just UX.",
                "Regulated environment (SIPC membership; FINRA license reviews in hiring) — security and audit trails are first-class requirements.",
                "IAM is the control plane of trust: joiner-mover-leaver, least privilege, access certification.",
                "SCS's stated mission — 'safeguard information and cultivate client trust' — is the job description of your career so far.",
            ],
            "model_answer": (
                "Because at a brokerage, security isn't a feature — it's the product. Clients hand over "
                "their savings, so 'safeguard information and cultivate client trust,' which is literally "
                "Schwab Cybersecurity Services' mission, is what the business runs on. That trust is "
                "enforced through identity: who can access what, who approved it, what happens the day "
                "someone leaves or changes roles. I've tested exactly that plane — Saviynt IGA workflows, "
                "CyberArk privileged sessions, access certifications — and I've seen how one untested "
                "mover path becomes an orphaned privileged account. A financial firm also runs under "
                "real regulatory scrutiny, which means security testing has teeth: findings get fixed, "
                "audit trails matter, and quality engineering is treated as engineering, not overhead."
            ),
        },
        {
            "question": "Where does the SDET role sit inside Schwab?",
            "talking_points": [
                "Schwab Technology Services (STS) powers the whole business — engineering, AI, architecture, cloud, cybersecurity.",
                "Schwab Cybersecurity Services (SCS) covers access, data, app, endpoint and cloud security plus threat detection and pen testing.",
                "Schwab's careers site names SDET, IAM, Quality Automation and DLP among its engineering role families.",
                "Stack they cite: Java, .NET/C#, Python, Spark, SQL — your core stack.",
            ],
            "model_answer": (
                "Inside Schwab Technology Services, which powers every part of the business, with the "
                "security arm being Schwab Cybersecurity Services — their mission spans securing access, "
                "protecting data, and safeguarding applications, endpoints and cloud, backed by threat "
                "detection, penetration testing and risk governance. Schwab's engineering careers pages "
                "explicitly list SDET, IAM, Quality Automation and DLP as role families, with Java, .NET, "
                "Python and SQL named in the stack — so this role sits right between quality engineering "
                "and cyber security, which is precisely where my experience is."
            ),
        },
    ],
    "quick_facts_drill": [
        {"q": "Schwab's mission statement?", "a": "To champion individuals' goals with passion and integrity."},
        {"q": "Schwab's four values?", "a": "Trust, Innovation, Teamwork, Stewardship."},
        {"q": "Schwab's client-facing philosophy?", "a": "Through Clients' Eyes — see everything from the client's perspective."},
        {"q": "Schwab's tagline?", "a": "Own Your Tomorrow."},
        {"q": "What are Schwab employees called?", "a": "Schwabbies."},
        {"q": "When and where was Schwab founded?", "a": "1971, San Francisco (as First Commander Corporation; renamed Charles Schwab & Co. in 1973)."},
        {"q": "Where is Schwab headquartered today?", "a": "Westlake, Texas."},
        {"q": "Client assets (Dec 31, 2024)?", "a": "$10.10 trillion."},
        {"q": "Active brokerage accounts (Dec 31, 2024)?", "a": "36.5 million."},
        {"q": "How many branches?", "a": "380+, primarily in the U.S. and U.K."},
        {"q": "What made Schwab famous in the 1970s?", "a": "Pioneering discount brokerage after deregulation."},
        {"q": "Schwab's two technology organizations?", "a": "Schwab Technology Services (STS) and Schwab Cybersecurity Services (SCS)."},
        {"q": "Schwab's interview methodology?", "a": "Behavioral-based interviewing using the S.T.A.R. method."},
        {"q": "Who interviews you first at Schwab?", "a": "A Talent Advisor phone screen, then the Hiring Manager, then any additional team rounds."},
    ],
    "sources": [
        {
            "name": "aboutschwab.com — Our Company",
            "url": "https://www.aboutschwab.com/our-company",
            "what": "Mission, values (Trust / Innovation / Teamwork / Stewardship), culture.",
        },
        {
            "name": "schwabjobs.com — About Schwab",
            "url": "https://www.schwabjobs.com/aboutschwab",
            "what": "Careers mirror of the company story: mission, values, Schwabbies, awards.",
        },
        {
            "name": "schwabjobs.com — How We Hire",
            "url": "https://www.schwabjobs.com/how-we-hire",
            "what": "Five-step hiring process, S.T.A.R. behavioral interviewing, background check scope, AI policy.",
        },
        {
            "name": "schwabjobs.com — Technology",
            "url": "https://www.schwabjobs.com/technology",
            "what": "STS and SCS descriptions, engineering role families (SDET, IAM, DLP, Quality Automation), tech stack.",
        },
        {
            "name": "Wikipedia — Charles Schwab Corporation",
            "url": "https://en.wikipedia.org/wiki/Charles_Schwab_Corporation",
            "what": "Scale figures (Dec 31, 2024), founding history, HQ and branch count.",
        },
    ],
    "disclaimer": (
        "Compiled from public sources in November 2026 for interview preparation. Figures carry "
        "their as-of dates; re-verify anything time-sensitive on aboutschwab.com before your "
        "interview. This is company research — not leaked or internal Schwab material."
    ),
}
