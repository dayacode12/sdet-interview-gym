"""Round 1 playbook for the Schwab SDET - Cyber Security QA interview.

Structure mirrors the research brief in round1.md: Java/automation coding,
API and database testing, IAM/security concepts, the 60-minute flow, the
experience gap, and the Teams/US format.

Evidence discipline:
  * "official"  = published by Charles Schwab on schwabjobs.com.
  * "jd"        = named in the job description / Schwab's own role families.
  * "reported"  = publicly reported by candidates (see the brief), not official.
  * "standard"  = technical answer grounded in a vendor spec or standard.

Schwab does NOT publish technical interview questions. Everything technical
below is a prediction, labelled as such. The official facts are quoted and
linked; they describe the process and the behavioural method, not a question
bank.
"""

from __future__ import annotations

ACCESSED = "2026-11-13"

SOURCES = [
    # ---- Official Charles Schwab sources -------------------------------------
    {
        "id": "how-we-hire",
        "name": "How We Hire — step-by-step guide",
        "publisher": "Charles Schwab (Schwab Jobs)",
        "type": "official",
        "url": "https://www.schwabjobs.com/how-we-hire",
        "supports": (
            "Five published steps (find your fit, candidate profile, apply, "
            "interview, offer). A Talent Advisor sets up an initial phone call; "
            "additional interviews vary by career area, timeline and job "
            "requirements. Offer stage includes background check and drug screen."
        ),
        "accessed": ACCESSED,
    },
    {
        "id": "star",
        "name": "Reach for the S.T.A.R.s — behavioural interview guide",
        "publisher": "Charles Schwab (Schwab Jobs)",
        "type": "official",
        "url": "https://www.schwabjobs.com/how-to-prepare-for-a-behavioral-based-interview",
        "supports": (
            "Schwab's own interviewing method: 'Past behavior often predicts "
            "future behavior.' Answers are assessed in S.T.A.R. format and must "
            "be specific, relevant and recent. Typically a minimum of three "
            "interviewers: a Talent Advisor and two Hiring Managers."
        ),
        "accessed": ACCESSED,
    },
    {
        "id": "technology",
        "name": "Schwab Technology Services (STS) careers",
        "publisher": "Charles Schwab (Schwab Jobs)",
        "type": "official",
        "url": "https://www.schwabjobs.com/technology",
        "supports": (
            "Names SDET, Identity and Access Management (IAM), Data Loss "
            "Prevention, Quality Automation, Site Reliability and Application "
            "Security as engineering role families, with Java, .NET, Python, "
            "Spark, SQL and C# in the stack. Describes Schwab Cybersecurity "
            "Services' mission to safeguard information and cultivate client trust."
        ),
        "accessed": ACCESSED,
    },
    {
        "id": "faqs",
        "name": "Careers FAQs — applying and hiring",
        "publisher": "Charles Schwab (Schwab Jobs)",
        "type": "official",
        "url": "https://www.schwabjobs.com/workingherefaqs",
        "supports": (
            "The process 'generally includes application review, a Talent Advisor "
            "conversation, one or more interviews, an offer and pre-employment "
            "screening.' Also documents hybrid working and culture."
        ),
        "accessed": ACCESSED,
    },
    # ---- Your research brief -------------------------------------------------
    {
        "id": "brief",
        "name": "round1.md — likely topics and example questions",
        "publisher": "Your research brief (compiled from the JD and public guides)",
        "type": "brief",
        "url": "",
        "supports": (
            "The topic map this page follows: Java/automation coding, API/DB "
            "validation, IAM/security, a 60-minute flow, the experience gap and "
            "the Teams format. It names Dataford, Glassdoor, AmbitionBox, "
            "SecInterviews, CyberInterviewQuestions, Techlead.org and Indeed as "
            "its secondary inputs."
        ),
        "accessed": ACCESSED,
    },
    # ---- Standards and vendor docs (technical correctness) -------------------
    {
        "id": "owasp-authn",
        "name": "Authentication Cheat Sheet",
        "publisher": "OWASP",
        "type": "standard",
        "url": "https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html",
        "supports": "Authentication vs authorization, credential handling, MFA, account lockout and session defences.",
        "accessed": ACCESSED,
    },
    {
        "id": "owasp-authz",
        "name": "Authorization Cheat Sheet",
        "publisher": "OWASP",
        "type": "standard",
        "url": "https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html",
        "supports": "Server-side authorization enforcement, deny-by-default, least privilege and IDOR/broken access control.",
        "accessed": ACCESSED,
    },
    {
        "id": "owasp-api",
        "name": "OWASP API Security Top 10 (2023)",
        "publisher": "OWASP",
        "type": "standard",
        "url": "https://owasp.org/API-Security/editions/2023/en/0x11-t10/",
        "supports": "Broken object-level authorization, broken authentication, property-level authorization and unrestricted resource consumption.",
        "accessed": ACCESSED,
    },
    {
        "id": "rfc6749",
        "name": "RFC 6749 — The OAuth 2.0 Authorization Framework",
        "publisher": "IETF",
        "type": "standard",
        "url": "https://www.rfc-editor.org/rfc/rfc6749",
        "supports": "OAuth 2.0 is a delegated authorization framework; access tokens are not proof of end-user identity.",
        "accessed": ACCESSED,
    },
    {
        "id": "oidc-core",
        "name": "OpenID Connect Core 1.0",
        "publisher": "OpenID Foundation",
        "type": "standard",
        "url": "https://openid.net/specs/openid-connect-core-1_0.html",
        "supports": "OIDC adds an identity layer on OAuth 2.0: the ID token's sub/iss/aud/exp claims identify the user.",
        "accessed": ACCESSED,
    },
    {
        "id": "saml",
        "name": "SAML 2.0 Technical Overview",
        "publisher": "OASIS",
        "type": "standard",
        "url": "http://docs.oasis-open.org/security/saml/Post2.0/sstc-saml-tech-overview-2.0.html",
        "supports": "SAML 2.0 browser SSO: XML assertions exchanged through a browser between an IdP and an SP.",
        "accessed": ACCESSED,
    },
    {
        "id": "nist-63b",
        "name": "NIST SP 800-63B — Digital Identity Guidelines: Authentication",
        "publisher": "NIST",
        "type": "standard",
        "url": "https://pages.nist.gov/800-63-4/sp800-63b.html",
        "supports": "Authenticator assurance, phishing resistance, rate limiting and recovery requirements.",
        "accessed": ACCESSED,
    },
    {
        "id": "nist-162",
        "name": "NIST SP 800-162 — Guide to Attribute Based Access Control",
        "publisher": "NIST",
        "type": "standard",
        "url": "https://csrc.nist.gov/pubs/sp/800/162/upd2/final",
        "supports": "ABAC definition and how attributes, policies and subject/resource/environment context combine.",
        "accessed": ACCESSED,
    },
    {
        "id": "nist-dlp",
        "name": "Glossary — Data Loss Prevention (DLP)",
        "publisher": "NIST CSRC",
        "type": "standard",
        "url": "https://csrc.nist.gov/glossary/term/data_loss_prevention",
        "supports": "DLP definition: systems that detect and prevent unauthorized transmission of sensitive data.",
        "accessed": ACCESSED,
    },
    {
        "id": "nist-207",
        "name": "NIST SP 800-207 — Zero Trust Architecture",
        "publisher": "NIST",
        "type": "standard",
        "url": "https://csrc.nist.gov/pubs/sp/800/207/final",
        "supports": "Policy enforcement points and continuous verification — useful framing for access-control scenarios.",
        "accessed": ACCESSED,
    },
    {
        "id": "playwright",
        "name": "Auto-waiting and actionability",
        "publisher": "Playwright",
        "type": "standard",
        "url": "https://playwright.dev/docs/actionability",
        "supports": "Playwright waits for actionability (visible, stable, enabled, receives events) before acting.",
        "accessed": ACCESSED,
    },
    {
        "id": "playwright-pom",
        "name": "Page object model",
        "publisher": "Playwright",
        "type": "standard",
        "url": "https://playwright.dev/docs/pom",
        "supports": "Recommended POM structure and fixture-based composition for UI tests.",
        "accessed": ACCESSED,
    },
    {
        "id": "selenium-waits",
        "name": "Waiting strategies — implicit, explicit, fluent",
        "publisher": "Selenium",
        "type": "standard",
        "url": "https://www.selenium.dev/documentation/webdriver/waits/",
        "supports": "Explicit waits poll for a condition; implicit waits are a global timeout; mixing them is discouraged.",
        "accessed": ACCESSED,
    },
    {
        "id": "selenium-pom",
        "name": "Page object models",
        "publisher": "Selenium",
        "type": "standard",
        "url": "https://www.selenium.dev/documentation/test_practices/encouraged/page_object_models/",
        "supports": "POM as a layer that separates page structure/actions from test logic.",
        "accessed": ACCESSED,
    },
    {
        "id": "rest-assured",
        "name": "REST Assured usage guide",
        "publisher": "REST Assured",
        "type": "standard",
        "url": "https://github.com/rest-assured/rest-assured/wiki/Usage",
        "supports": "Given/when/then syntax, JSON body assertions, headers, status codes and schema validation.",
        "accessed": ACCESSED,
    },
    {
        "id": "json-schema",
        "name": "JSON Schema",
        "publisher": "JSON Schema",
        "type": "standard",
        "url": "https://json-schema.org/",
        "supports": "Declarative contract validation for request/response payloads.",
        "accessed": ACCESSED,
    },
    {
        "id": "postgres-select",
        "name": "PostgreSQL SELECT — joins, GROUP BY, HAVING",
        "publisher": "PostgreSQL",
        "type": "standard",
        "url": "https://www.postgresql.org/docs/current/sql-select.html",
        "supports": "JOIN semantics, GROUP BY and HAVING behaviour used in the SQL answers.",
        "accessed": ACCESSED,
    },
    {
        "id": "oracle-map",
        "name": "Java HashMap API",
        "publisher": "Oracle",
        "type": "standard",
        "url": "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/HashMap.html",
        "supports": "HashMap behaviour, merge(), and the equals/hashCode contract for keys.",
        "accessed": ACCESSED,
    },
    {
        "id": "oracle-collections",
        "name": "Java Collections Framework tutorial",
        "publisher": "Oracle",
        "type": "standard",
        "url": "https://docs.oracle.com/javase/tutorial/collections/interfaces/map.html",
        "supports": "Choosing Map/Set/List implementations and their ordering/duplicate semantics.",
        "accessed": ACCESSED,
    },
]

OFFICIAL_PROCESS = {
    "headline": "What Schwab actually publishes",
    "facts": [
        {
            "claim": (
                "Hiring has five published steps: find your fit, build a candidate "
                "profile, apply, interview, then offer."
            ),
            "source_ids": ["how-we-hire"],
        },
        {
            "claim": (
                "A Talent Advisor sets up an initial phone call. Additional "
                "interviews vary by career area, hiring timeline and job "
                "requirements — there is no single fixed loop."
            ),
            "source_ids": ["how-we-hire", "faqs"],
        },
        {
            "claim": (
                "Interviewing is behavioural-based: 'Past behavior often predicts "
                "future behavior.' Answers are assessed in S.T.A.R. format and "
                "must be specific, relevant and recent."
            ),
            "source_ids": ["star"],
        },
        {
            "claim": (
                "You will typically meet a minimum of three people: a Talent "
                "Advisor and two Hiring Managers."
            ),
            "source_ids": ["star"],
        },
        {
            "claim": (
                "Schwab's technology careers page names SDET, IAM, Data Loss "
                "Prevention, Quality Automation, Site Reliability and Application "
                "Security as engineering role families, with Java, .NET, Python, "
                "Spark, SQL and C# in the stack."
            ),
            "source_ids": ["technology"],
        },
        {
            "claim": (
                "Schwab Cybersecurity Services describes its mission as "
                "safeguarding information and cultivating client trust, spanning "
                "access, data, applications, endpoints and cloud."
            ),
            "source_ids": ["technology"],
        },
    ],
    "implication": (
        "The official material tells you how Schwab interviews and what the "
        "technology organisation values. It does not publish technical questions. "
        "So the technical questions below are predictions — each labelled with "
        "the evidence that makes it likely, never presented as leaked material."
    ),
    "what_it_does_not_say": (
        "Schwab does not publish a Java/SQL/IAM question bank, an official "
        "first-round script, or a guarantee that your loop matches this page. "
        "Confirm the format with your Talent Advisor."
    ),
}

SECTIONS = [
    {
        "id": "java-automation",
        "title": "Java / Automation Coding",
        "icon": "braces",
        "intro": (
            "The brief predicts classic SDET coding plus framework design. "
            "Schwab's own careers page lists Java and Quality Automation as core "
            "technology role families, so this is the least speculative section "
            "on the page. Write compilable Java, then narrate edge cases."
        ),
        "questions": [
            {
                "id": "r1-java-reverse",
                "prompt": "Write a Java method to reverse a string without using StringBuilder.reverse() or any built-in reverse method.",
                "evidence": "jd",
                "why": (
                    "The brief lists this exact task as a typical SDET coding "
                    "question. It tests loops, arrays, null handling and whether "
                    "you can explain complexity — not library recall."
                ),
                "model_answer": (
                    "Use two pointers and swap in place on a char array. Handle "
                    "null and empty input explicitly, then state the cost: O(n) "
                    "time and O(n) space because toCharArray() copies. In an "
                    "interview, add one sentence about Unicode: char is a UTF-16 "
                    "code unit, so an emoji made of a surrogate pair would be "
                    "split; for true text safety iterate code points."
                ),
                "code": (
                    "public static String reverse(String input) {\n"
                    "    if (input == null || input.length() < 2) return input;\n"
                    "    char[] chars = input.toCharArray();\n"
                    "    int left = 0, right = chars.length - 1;\n"
                    "    while (left < right) {\n"
                    "        char tmp = chars[left];\n"
                    "        chars[left++] = chars[right];\n"
                    "        chars[right--] = tmp;\n"
                    "    }\n"
                    "    return new String(chars);\n"
                    "}"
                ),
                "key_points": [
                    "Two-pointer swap, not string concatenation in a loop (which is O(n²)).",
                    "Null and length < 2 are valid edge cases — say them before coding.",
                    "State O(n) time / O(n) space, and why StringBuilder would also be O(n).",
                    "Mention surrogate pairs if the interviewer pushes on Unicode.",
                ],
                "follow_ups": [
                    "Reverse the words in a sentence but keep word order? (split, reverse the array, join)",
                    "Reverse in place for a char[]? (same two-pointer loop, no allocation)",
                    "How would you unit-test it? (null, empty, one char, palindrome, surrogate pair)",
                ],
                "traps": [
                    "Using StringBuilder.reverse() after being told not to.",
                    "Ignoring null and crashing on the first line.",
                    "Claiming O(1) space while allocating a char array.",
                ],
                "source_ids": ["brief", "oracle-collections"],
            },
            {
                "id": "r1-java-duplicates",
                "prompt": "Find the duplicate elements in an array (or the repeated characters in a string).",
                "evidence": "jd",
                "why": (
                    "The brief names this as a standard collections-and-loops "
                    "screen. It also maps directly to duplicate detection in IAM "
                    "reconciliation — a strong bridge to your real work."
                ),
                "model_answer": (
                    "Use a HashSet as the 'seen' set. For each value, add() returns "
                    "false when the value is already present, so that is the "
                    "duplicate. Keep a second LinkedHashSet if the interviewer wants "
                    "a stable, de-duplicated list of duplicates. This is O(n) time "
                    "and O(n) space. For an int[] you need HashSet<Integer> because "
                    "generics cannot hold primitives."
                ),
                "code": (
                    "public static <T> Set<T> duplicates(T[] values) {\n"
                    "    Set<T> seen = new HashSet<>();\n"
                    "    Set<T> dupes = new LinkedHashSet<>();\n"
                    "    if (values == null) return dupes;\n"
                    "    for (T value : values) {\n"
                    "        if (!seen.add(value)) dupes.add(value);\n"
                    "    }\n"
                    "    return dupes;\n"
                    "}"
                ),
                "key_points": [
                    "HashSet.add() returns false on a duplicate — the whole trick.",
                    "LinkedHashSet preserves first-seen order when output order matters.",
                    "equals()/hashCode() must be consistent for custom objects.",
                    "Bridge: the same pattern detects duplicate identities during IAM reconciliation.",
                ],
                "follow_ups": [
                    "Return the first duplicate only? (return immediately on add() == false)",
                    "Count occurrences of every element? (HashMap + merge)",
                    "Do it in O(1) extra space for a bounded range? (index-marking, with caveats)",
                ],
                "traps": [
                    "Nested loops and calling it O(n) — it is O(n²).",
                    "Using == instead of equals() for boxed types or Strings.",
                    "Returning the input array as the 'duplicates' answer.",
                ],
                "source_ids": ["brief", "oracle-map"],
            },
            {
                "id": "r1-java-wordcount",
                "prompt": "Count how many times each word appears in a sentence.",
                "evidence": "jd",
                "why": (
                    "The brief lists word frequencies explicitly. It tests "
                    "string parsing, normalisation and the Map API — the same "
                    "mechanics as counting failed logins or entitlements per user."
                ),
                "model_answer": (
                    "Normalise case with Locale.ROOT, split on non-word characters, "
                    "skip empty tokens, and use Map.merge(word, 1, Integer::sum). "
                    "Use LinkedHashMap if the interviewer wants insertion order; "
                    "HashMap is fine otherwise. Say what you assume about "
                    "apostrophes and hyphenated words instead of silently choosing."
                ),
                "code": (
                    "public static Map<String, Integer> wordFrequencies(String text) {\n"
                    "    Map<String, Integer> counts = new LinkedHashMap<>();\n"
                    "    if (text == null || text.isBlank()) return counts;\n"
                    "    for (String word : text.toLowerCase(Locale.ROOT).split(\"\\\\W+\")) {\n"
                    "        if (!word.isEmpty()) counts.merge(word, 1, Integer::sum);\n"
                    "    }\n"
                    "    return counts;\n"
                    "}"
                ),
                "key_points": [
                    "State the tokenisation rule: what counts as a word?",
                    "Locale.ROOT for lowercase — avoids the Turkish 'I' surprise.",
                    "merge() is atomic-looking and shorter than get/put.",
                    "Return type choice is part of the answer: Map<String,Integer>.",
                ],
                "follow_ups": [
                    "Top-k most frequent words? (PriorityQueue or bucket sort)",
                    "Ignore a stop-word list? (filter before merge)",
                    "Stream version? (Collectors.groupingBy with counting())",
                ],
                "traps": [
                    "Splitting on a single space and missing punctuation/newlines.",
                    "Using == to compare words.",
                    "Forgetting null/blank input.",
                ],
                "source_ids": ["brief", "oracle-map"],
            },
            {
                "id": "r1-oop-polymorphism",
                "prompt": "How have you used polymorphism or interfaces in an automation framework?",
                "evidence": "jd",
                "why": (
                    "The brief predicts OOP/design questions, and Schwab's "
                    "behavioural method rewards specific, recent examples. Answer "
                    "with a structure you actually built, not a textbook definition."
                ),
                "model_answer": (
                    "Define a Page contract — open(), isLoaded(), and the actions "
                    "the test needs. LoginPage and AccountsPage implement it, so a "
                    "generic navigation step can accept Page and stay unchanged when "
                    "a new page is added. I use a factory/strategy for browser and "
                    "environment selection, and composition for utilities (waits, "
                    "API client, test data). Inheritance is limited to a thin "
                    "BasePage for logging and waits, because deep hierarchies make "
                    "tests brittle. The payoff is that adding a page or browser is "
                    "an extension, not an edit to every test."
                ),
                "code": "",
                "key_points": [
                    "Name the contract and two concrete implementations.",
                    "Explain the open/closed payoff: new page, no test rewrite.",
                    "Mention composition over inheritance for utilities.",
                    "Tie it to a measured outcome (fewer duplicated waits/locators).",
                ],
                "follow_ups": [
                    "Abstract class vs interface — which would you choose here and why?",
                    "Where does the PageFactory/DI fit?",
                    "How do checked and unchecked exceptions affect framework error handling?",
                ],
                "traps": [
                    "Reciting 'encapsulation, inheritance, polymorphism' with no example.",
                    "A BasePage god-class that every page inherits.",
                    "Assertions inside page objects, hiding failures from the test report.",
                ],
                "source_ids": ["brief", "selenium-pom", "playwright-pom"],
            },
            {
                "id": "r1-selenium-pom",
                "prompt": "Explain your Selenium framework architecture (POM), and write an explicit wait for an element to be clickable.",
                "evidence": "jd",
                "why": (
                    "The brief names POM architecture and WebDriverWait as likely "
                    "questions, and Selenium is standard SDET tooling. Schwab's "
                    "technology page lists Quality Automation as a role family."
                ),
                "model_answer": (
                    "Layers: tests (TestNG, assertions, data), page objects "
                    "(locators + user actions), a driver/browser factory, shared "
                    "utilities (waits, screenshots, logging, config), and CI "
                    "reporting. Tests never touch By locators directly. Use explicit "
                    "waits for the specific condition; implicit waits are one global "
                    "timeout and mixing the two produces unpredictable behaviour. "
                    "Dynamic locators should be relative and stable — prefer "
                    "data-testid, then CSS, then XPath as a last resort. For "
                    "parallelism, ThreadLocal<WebDriver> plus isolated test data. "
                    "For flakiness: wait for state, classify the failure, retry only "
                    "known transient cases, and quarantine with an owner."
                ),
                "code": (
                    "WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));\n"
                    "WebElement submit = wait.until(\n"
                    "    ExpectedConditions.elementToBeClickable(By.cssSelector(\"[data-testid='submit']\"))\n"
                    ");\n"
                    "submit.click();"
                ),
                "key_points": [
                    "Draw the layers before naming tools.",
                    "Explicit wait for a condition; never sleep().",
                    "Do not mix implicit and explicit waits.",
                    "Dynamic locators: stable attributes, relative paths, no brittle indexes.",
                    "Parallel: ThreadLocal driver + independent users/data.",
                    "Flakiness: classify (product/environment/test), then fix or quarantine.",
                ],
                "follow_ups": [
                    "How do you handle a StaleElementReferenceException?",
                    "How do you run the suite in Jenkins/GitHub Actions?",
                    "How do you test file upload or a new browser tab?",
                ],
                "traps": [
                    "Thread.sleep() presented as a wait strategy.",
                    "One giant BaseTest that hides setup and teardown.",
                    "Absolute XPath copied from DevTools.",
                ],
                "source_ids": ["brief", "selenium-waits", "selenium-pom"],
            },
            {
                "id": "r1-playwright-migration",
                "prompt": "Why did you migrate from Selenium to Playwright, and how did you measure the improvement?",
                "evidence": "reported",
                "why": (
                    "Public candidate reports (collected in the existing research "
                    "bank) say interviewers probe 'why did you choose your "
                    "frameworks'. The brief also predicts a Selenium-vs-Playwright "
                    "comparison. Expect the 33% claim to be challenged."
                ),
                "model_answer": (
                    "Playwright gives auto-waiting and actionability checks before "
                    "each action, web-first assertions that retry, browser contexts "
                    "for cheap isolation, a trace viewer for failures, built-in API "
                    "testing and parallel workers. Selenium still wins on breadth of "
                    "browser/driver/vendor support and its W3C WebDriver standard. I "
                    "migrated a vertical slice first, replaced sleeps with "
                    "web-first assertions, moved page objects to fixtures, then "
                    "measured the same suite on the same environment across multiple "
                    "runs and reported the median — not the best run. The result was "
                    "a ~33% reduction in regression runtime, plus fewer "
                    "wait-related flakes."
                ),
                "code": "",
                "key_points": [
                    "Give both sides: what Playwright fixes, what Selenium still does better.",
                    "Migration method: inventory → vertical slice → fixtures → measure.",
                    "Measurement discipline: same suite, same env, multiple runs, median.",
                    "Do not overclaim: 33% on your suite is not a universal law.",
                ],
                "follow_ups": [
                    "What did you lose in the migration?",
                    "How did you keep coverage honest during the transition?",
                    "When would you not migrate?",
                ],
                "traps": [
                    "Saying Playwright is 'just faster' with no mechanism.",
                    "Quoting the best single run as the result.",
                    "Pretending Selenium has no advantages.",
                ],
                "source_ids": ["brief", "playwright", "selenium-waits"],
            },
        ],
    },
    {
        "id": "api-db",
        "title": "API and Database Testing",
        "icon": "database",
        "intro": (
            "The brief predicts REST Assured, authentication/authorization cases, "
            "schema validation and IAM-shaped SQL. Schwab's page lists SQL in the "
            "technology stack. The strongest answers connect the API assertion to "
            "the database row and then to the security meaning."
        ),
        "questions": [
            {
                "id": "r1-api-create",
                "prompt": "Write a REST Assured test that creates a user and validates the status and payload.",
                "evidence": "jd",
                "why": (
                    "The brief names this as the likely hands-on API task. It tests "
                    "request construction, assertions and cleanup — the baseline "
                    "every API-QA interview starts from."
                ),
                "model_answer": (
                    "Build the request with content type and a JSON body, POST it, "
                    "then assert the status, the Location header and the response "
                    "fields. Use Hamcrest matchers rather than printing the body. "
                    "Add the negative cases that matter: duplicate username → 409, "
                    "missing required field → 400, no token → 401. Finally verify "
                    "the row exists in the database and clean it up in teardown so "
                    "the test is repeatable."
                ),
                "code": (
                    "given()\n"
                    "    .contentType(ContentType.JSON)\n"
                    "    .body(Map.of(\"username\", \"qa_user\", \"role\", \"READ_ONLY\"))\n"
                    ".when()\n"
                    "    .post(\"/api/users\")\n"
                    ".then()\n"
                    "    .statusCode(201)\n"
                    "    .header(\"Location\", containsString(\"/api/users/\"))\n"
                    "    .body(\"username\", equalTo(\"qa_user\"))\n"
                    "    .body(\"role\", equalTo(\"READ_ONLY\"))\n"
                    "    .body(\"id\", notNullValue());"
                ),
                "key_points": [
                    "Assert status + schema/fields + headers, not just 200.",
                    "Negative cases are part of the answer, not an afterthought.",
                    "Verify the database side effect, then clean up.",
                    "Never assert on a generated id value — assert it exists and is stable across reads.",
                ],
                "follow_ups": [
                    "How would you validate the response against a JSON Schema?",
                    "How do you make the test idempotent?",
                    "What would you check in the audit log?",
                ],
                "traps": [
                    "Only asserting statusCode(200).",
                    "Hardcoding a token or a database id.",
                    "Leaving created users behind and breaking the next run.",
                ],
                "source_ids": ["brief", "rest-assured", "json-schema"],
            },
            {
                "id": "r1-api-auth",
                "prompt": "How do you authenticate and authorize your API tests?",
                "evidence": "jd",
                "why": (
                    "The brief calls out tokens, valid/invalid auth cases and "
                    "authorization as likely probes. For a cyber security QA role, "
                    "this is the highest-signal API question."
                ),
                "model_answer": (
                    "Get a token from the identity provider — client credentials for "
                    "service tests, authorization code + PKCE for user flows — and "
                    "keep it in a secret store or environment variable, never in "
                    "source. Send it as a Bearer token. Test the matrix: no token "
                    "→ 401; expired or malformed token → 401; valid token but wrong "
                    "role → 403; valid token and correct role → 200; tenant A's token "
                    "against tenant B's object → 403/404. Then check the enforcement "
                    "point: the server must reject, not just the UI. A 401 means we "
                    "don't know who you are; a 403 means we do and you still can't."
                ),
                "code": "",
                "key_points": [
                    "Token acquisition is a flow, not a hardcoded string.",
                    "401 vs 403 stated precisely.",
                    "Test both horizontal (other user) and vertical (other role) escalation.",
                    "Authorization must be enforced server-side; UI hiding is not a control.",
                ],
                "follow_ups": [
                    "How do you test token expiry without waiting an hour?",
                    "What about refresh-token rotation and revocation?",
                    "How do you avoid leaking tokens into logs or reports?",
                ],
                "traps": [
                    "Only testing the happy path with one admin token.",
                    "Confusing authentication with authorization.",
                    "Assuming a 404 means the object doesn't exist rather than 'not yours'.",
                ],
                "source_ids": ["brief", "owasp-authz", "owasp-api", "rfc6749"],
            },
            {
                "id": "r1-api-schema",
                "prompt": "How do you validate a response schema and confirm the database side effect?",
                "evidence": "jd",
                "why": (
                    "The brief predicts both schema validation and database "
                    "verification questions. Together they test whether your API "
                    "test stops at the JSON boundary."
                ),
                "model_answer": (
                    "Validate the contract with JSON Schema: required fields, types, "
                    "enums, formats and no unexpected leakage. Then query the "
                    "database by the natural key and assert the row, its status and "
                    "its audit entry. For asynchronous flows, poll with a bounded "
                    "timeout instead of sleeping. Also test the negative side: an "
                    "invalid request must not leave a partial row — that is a "
                    "transaction-boundary defect. Finally check for duplicates, "
                    "because a retried POST that creates two rows is a real bug."
                ),
                "code": (
                    "-- after the API returns 201 with id = :id\n"
                    "SELECT user_id, username, status, created_at\n"
                    "FROM users\n"
                    "WHERE user_id = :id;"
                ),
                "key_points": [
                    "Schema validation is contract testing, not value matching.",
                    "Verify the database row, the audit row and the absence of duplicates.",
                    "Bounded polling for eventual consistency.",
                    "Negative request → no partial write.",
                ],
                "follow_ups": [
                    "Where do you store the schema, and who owns it?",
                    "How do you test an event-driven flow with no synchronous response?",
                    "What is your cleanup strategy for shared environments?",
                ],
                "traps": [
                    "Asserting only the fields you happened to look at.",
                    "Sleeping for a fixed time and hoping.",
                    "Ignoring the audit trail in a regulated environment.",
                ],
                "source_ids": ["brief", "rest-assured", "json-schema", "postgres-select"],
            },
            {
                "id": "r1-sql-inactive",
                "prompt": "Given USERS, USER_ROLES and ROLES, find users marked inactive who still have active roles.",
                "evidence": "jd",
                "why": (
                    "The brief gives this exact IAM-shaped query. It is the "
                    "intersection of SQL skill and security judgement — exactly "
                    "what a Cyber Security QA role screens for."
                ),
                "model_answer": (
                    "Join users to user_roles and roles, filter on the inactive "
                    "status, and keep only active assignments. Every returned row is "
                    "an access-control violation, so say that out loud: the query is "
                    "not just a JOIN exercise, it is a control test. If USER_ROLES "
                    "has no status column, drop that predicate and treat any "
                    "assignment as active. Add an index on users.status and "
                    "user_roles.user_id if this runs often."
                ),
                "code": (
                    "SELECT u.user_id, u.username, r.role_name\n"
                    "FROM users u\n"
                    "JOIN user_roles ur ON ur.user_id = u.user_id\n"
                    "JOIN roles r       ON r.role_id  = ur.role_id\n"
                    "WHERE u.status = 'INACTIVE'\n"
                    "  AND ur.status = 'ACTIVE'\n"
                    "ORDER BY u.user_id, r.role_name;"
                ),
                "key_points": [
                    "INNER JOIN drops users with no roles — which is usually what you want here.",
                    "State the schema assumption out loud instead of inventing columns.",
                    "Frame every row as an access-control defect.",
                    "Mention indexes and why the query is safe to run read-only.",
                ],
                "follow_ups": [
                    "Now find users with no roles at all.",
                    "Find role assignments whose user row no longer exists.",
                    "How would you turn this into an automated regression check?",
                ],
                "traps": [
                    "Using WHERE instead of HAVING for an aggregate without noticing.",
                    "Forgetting that INNER JOIN hides role-less users.",
                    "Running UPDATE instead of SELECT during an interview.",
                ],
                "source_ids": ["brief", "postgres-select"],
            },
            {
                "id": "r1-sql-orphans",
                "prompt": "How would you detect duplicate usernames or orphaned records in identity tables?",
                "evidence": "jd",
                "why": (
                    "The brief names duplicate usernames and orphaned records. "
                    "These are the data-integrity checks behind IAM reconciliation."
                ),
                "model_answer": (
                    "Duplicates: group by the normalised key and use HAVING COUNT(*) "
                    "> 1. Orphans: LEFT JOIN from the child table to the parent and "
                    "keep rows where the parent key is NULL. Do both — a foreign key "
                    "prevents orphans going forward but does not prove historical "
                    "data is clean, and case-insensitive duplicates can slip past a "
                    "case-sensitive unique index."
                ),
                "code": (
                    "-- duplicate usernames, case-insensitive\n"
                    "SELECT LOWER(username) AS username, COUNT(*) AS n\n"
                    "FROM users\n"
                    "GROUP BY LOWER(username)\n"
                    "HAVING COUNT(*) > 1;\n"
                    "\n"
                    "-- role assignments with no user\n"
                    "SELECT ur.*\n"
                    "FROM user_roles ur\n"
                    "LEFT JOIN users u ON u.user_id = ur.user_id\n"
                    "WHERE u.user_id IS NULL;"
                ),
                "key_points": [
                    "GROUP BY + HAVING for duplicates; WHERE filters rows before grouping.",
                    "LEFT JOIN ... IS NULL for orphans.",
                    "Normalise case for username uniqueness.",
                    "A constraint prevents new bad rows; a query proves the existing data is clean.",
                ],
                "follow_ups": [
                    "How would you clean the duplicates safely?",
                    "What unique index would you add, and on which expression?",
                    "How do you test that the cleanup did not delete the wrong identity?",
                ],
                "traps": [
                    "Using WHERE COUNT(*) > 1 — invalid, must be HAVING.",
                    "Assuming a unique constraint covers case variations.",
                    "Deleting rows before capturing evidence.",
                ],
                "source_ids": ["brief", "postgres-select"],
            },
            {
                "id": "r1-batch-job",
                "prompt": "How would you test a nightly provisioning or ETL job?",
                "evidence": "jd",
                "why": (
                    "The brief notes the JD mentions scheduled jobs, so batch "
                    "verification is plausible. It also tests idempotency and "
                    "failure handling — senior signals."
                ),
                "model_answer": (
                    "Start with control totals: count and checksum at source, staging "
                    "and target. Then reconcile at record level, not just totals, "
                    "because equal counts can hide a swap. Test idempotency by "
                    "running the job twice and proving the target is unchanged. Test "
                    "the incremental window: late-arriving records, duplicates, a "
                    "record updated mid-run. Test partial failure: does it roll back "
                    "or resume from a watermark without double-provisioning? Check "
                    "the audit/log output and the alert path. Finally inject the "
                    "security case — a missing termination event must not leave "
                    "access behind."
                ),
                "code": "",
                "key_points": [
                    "Control totals + record-level reconciliation.",
                    "Idempotency: run twice, same result.",
                    "Watermarks, late data and duplicate events.",
                    "Partial-failure behaviour and restartability.",
                    "Audit trail and alerting are part of the test, not operations' problem.",
                ],
                "follow_ups": [
                    "How do you test a job that takes six hours?",
                    "What is your rollback strategy if the target is already live?",
                    "How do you prove no records were skipped, not just that counts match?",
                ],
                "traps": [
                    "Only comparing row counts.",
                    "Testing once on a clean environment and calling it done.",
                    "Ignoring the termination-event path.",
                ],
                "source_ids": ["brief", "postgres-select"],
            },
            {
                "id": "r1-microservices",
                "prompt": "How would you test a microservices-based IAM flow?",
                "evidence": "reported",
                "why": (
                    "Public candidate reports collected in the existing research "
                    "bank describe a whiteboard on testing microservices. The brief "
                    "does not list it for round 1, so treat it as a likely bonus "
                    "rather than a guaranteed question."
                ),
                "model_answer": (
                    "Draw the flow first: HR event → IGA → connector → target app, "
                    "with an API gateway and a message bus between some hops. Test "
                    "each service in isolation with contract tests (consumer-driven "
                    "or schema-based), then test the seams: does the event schema "
                    "match, is the consumer idempotent, what happens on retry or "
                    "out-of-order delivery? Mock dependencies only for isolation "
                    "tests; keep a thin end-to-end path for the real contracts. For "
                    "data consistency, assert the invariant and poll within a bounded "
                    "window. Add failure injection: one service down, slow, or "
                    "returning a duplicate."
                ),
                "code": "",
                "key_points": [
                    "Service boundaries and contracts before tooling.",
                    "Mock in isolation, but keep real contract/E2E coverage.",
                    "Idempotency, retries and out-of-order events.",
                    "Eventual consistency needs an invariant and a bounded wait.",
                ],
                "follow_ups": [
                    "Where would you put a contract test in CI?",
                    "How do you debug a record that exists in IGA but not in the target?",
                    "What is the difference between a contract test and an integration test?",
                ],
                "traps": [
                    "Trying to test everything end-to-end and calling it a strategy.",
                    "Mocking so much that no real contract is ever exercised.",
                    "Ignoring the message bus completely.",
                ],
                "source_ids": ["brief", "rest-assured", "json-schema"],
            },
        ],
    },
    {
        "id": "iam-security",
        "title": "IAM & Cybersecurity Concepts",
        "icon": "shield",
        "intro": (
            "This is where the role's security identity is decided. Schwab's own "
            "technology page names IAM and Data Loss Prevention as role families "
            "and describes a mission of safeguarding information and cultivating "
            "client trust. The brief predicts the exact concepts below."
        ),
        "questions": [
            {
                "id": "r1-aaa",
                "prompt": "What is the difference between authentication, authorization and accounting (AAA)?",
                "evidence": "reported",
                "why": (
                    "The brief reports this as a Schwab-style opening question. It "
                    "is the vocabulary everything else builds on."
                ),
                "model_answer": (
                    "Authentication proves who you are — password plus MFA, SAML, "
                    "OIDC. Authorization decides what you may do — roles, scopes, "
                    "attribute policies; it is the 403 after a valid login. "
                    "Accounting/auditing records what you did — session records, "
                    "access logs, non-repudiation. In a brokerage: login is "
                    "authentication, the entitlement check on an account is "
                    "authorization, and the immutable audit trail is accounting. Test "
                    "them separately, because a system can authenticate perfectly and "
                    "still authorize badly."
                ),
                "code": "",
                "key_points": [
                    "One sentence each, then the brokerage example.",
                    "401 vs 403 as the concrete test signal.",
                    "Authorization must be server-side and deny-by-default.",
                    "Accounting is evidence — it is what regulators and investigators read.",
                ],
                "follow_ups": [
                    "Where does SSO fit? (authentication federation)",
                    "Where does MFA fit? (strengthening authentication)",
                    "How would you test each of the three?",
                ],
                "traps": [
                    "Treating authentication and authorization as synonyms.",
                    "Forgetting accounting entirely.",
                    "Saying authorization is 'what you can see in the UI'.",
                ],
                "source_ids": ["brief", "owasp-authn", "owasp-authz"],
            },
            {
                "id": "r1-sso",
                "prompt": "Explain SAML vs OAuth 2.0 vs OpenID Connect. When would you use each?",
                "evidence": "reported",
                "why": (
                    "The brief lists this as a likely Schwab IAM question and notes "
                    "that SSO protocol depth is probed. It is also the most common "
                    "place candidates conflate authorization with authentication."
                ),
                "model_answer": (
                    "SAML 2.0 is XML-based browser SSO between an identity provider "
                    "and a service provider; it is common in enterprise apps. OAuth "
                    "2.0 is a delegated authorization framework for API access — an "
                    "access token says what a client may do, not who the user is. "
                    "OIDC is an identity layer on OAuth 2.0: the ID token is a JWT "
                    "with sub, iss, aud and exp, so you can authenticate a user. Use "
                    "SAML for legacy enterprise federation, OAuth 2.0 for API scopes, "
                    "and OIDC for modern web/mobile login. For public clients, use "
                    "authorization code with PKCE."
                ),
                "code": "",
                "key_points": [
                    "SAML = XML assertions, browser SSO, enterprise.",
                    "OAuth2 = authorization framework, not authentication.",
                    "OIDC = OAuth2 + ID token (JWT) with identity claims.",
                    "PKCE protects the authorization-code flow on public clients.",
                ],
                "follow_ups": [
                    "Sketch the authorization-code flow.",
                    "Why is the implicit flow deprecated?",
                    "How do you validate an ID token signature and claims?",
                ],
                "traps": [
                    "Saying OAuth 2.0 authenticates users.",
                    "Mixing up the ID token and the access token.",
                    "Forgetting audience/issuer validation on the JWT.",
                ],
                "source_ids": ["brief", "rfc6749", "oidc-core", "saml"],
            },
            {
                "id": "r1-jml",
                "prompt": "Walk through the joiner-mover-leaver lifecycle. What are the common pitfalls?",
                "evidence": "reported",
                "why": (
                    "The brief calls JML a core IAM topic and your strongest "
                    "real-world story. Expect a follow-up on how you would test a "
                    "terminated user."
                ),
                "model_answer": (
                    "Joiner: HR creates the identity, the role drives entitlements, "
                    "and provisioning reaches AD, email and apps. Mover: the new role "
                    "adds access, the old access must be removed, and separation-of-"
                    "duties is re-checked. Leaver: disable the identity, revoke "
                    "sessions and refresh tokens, reclaim hardware, transfer data, "
                    "and retain the audit record. Pitfalls: orphaned accounts, "
                    "privilege creep on moves, delayed termination, contractor "
                    "expiry that nobody owns, and shared/service accounts that "
                    "survive the person. Test the full chain: HR event → IGA → "
                    "connector → target app → login attempt."
                ),
                "code": "",
                "key_points": [
                    "Three phases, with the control that matters in each.",
                    "Mover is where privilege creep lives.",
                    "Leaver must include sessions/tokens, not just the account row.",
                    "Test the evidence chain end to end, including a real login attempt.",
                ],
                "follow_ups": [
                    "How do you test a rehire?",
                    "What about a contractor whose end date passes silently?",
                    "Which system is the source of truth?",
                ],
                "traps": [
                    "Only describing the happy path.",
                    "Forgetting downstream apps and active sessions.",
                    "Assuming the HR event always arrives.",
                ],
                "source_ids": ["brief", "nist-207", "owasp-authz"],
            },
            {
                "id": "r1-rbac-abac",
                "prompt": "Compare RBAC and ABAC. When would you use each?",
                "evidence": "reported",
                "why": (
                    "The brief lists RBAC vs ABAC as a likely question. It tests "
                    "whether you can choose a model, not just define acronyms."
                ),
                "model_answer": (
                    "RBAC bundles permissions into roles and assigns roles to "
                    "identities. It is coarse, easy to certify and easy to audit — "
                    "good for baseline entitlements. ABAC evaluates attributes: user "
                    "department, resource classification, time, location, device "
                    "posture. It is fine-grained and context-aware, but harder to "
                    "test and explain. In a brokerage I would start with RBAC for "
                    "the role-to-access map, then add ABAC or conditional access for "
                    "step-up decisions such as a risky login or an unmanaged device."
                ),
                "code": "",
                "key_points": [
                    "RBAC = role → permission; ABAC = attributes + policy.",
                    "RBAC is simpler to certify; ABAC is finer-grained.",
                    "Use both: RBAC baseline, ABAC for context/step-up.",
                    "Test policy precedence and deny-overrides, not just happy paths.",
                ],
                "follow_ups": [
                    "How do you test an ABAC policy matrix without exploding combinations?",
                    "What is deny-by-default and why does it matter?",
                    "How does SoD interact with roles?",
                ],
                "traps": [
                    "Saying ABAC is 'just better'.",
                    "Ignoring the audit/certification cost of fine-grained policies.",
                    "Forgetting that attributes can be stale or spoofed.",
                ],
                "source_ids": ["brief", "nist-162", "owasp-authz"],
            },
            {
                "id": "r1-pam-iga",
                "prompt": "What is privileged access management, and how does PAM differ from IGA?",
                "evidence": "reported",
                "why": (
                    "The brief highlights CyberArk on your resume and predicts a "
                    "PAM-vs-IGA question. This is a chance to use real experience."
                ),
                "model_answer": (
                    "PAM protects high-risk accounts: vaulting credentials, rotating "
                    "them, check-out/check-in, just-in-time elevation, approval and "
                    "session recording. IGA governs access across the whole "
                    "population: joiner-mover-leaver, requests, certifications and "
                    "RBAC. IGA is breadth and governance; PAM is depth and "
                    "high-privilege control. Least privilege needs both — IGA stops "
                    "standing access from spreading, PAM removes standing admin "
                    "credentials and records what was done with them."
                ),
                "code": "",
                "key_points": [
                    "PAM: vault, rotate, check-out, JIT, record.",
                    "IGA: JML, requests, certifications, role governance.",
                    "Breadth vs depth, but complementary.",
                    "Test approval, rotation, session recording and break-glass audit.",
                ],
                "follow_ups": [
                    "How would you test that a vaulted password actually rotated?",
                    "What is break-glass access and how do you audit it?",
                    "How do you detect a standing admin account that should be JIT?",
                ],
                "traps": [
                    "Describing PAM as 'a password manager'.",
                    "Claiming IGA and PAM are the same thing.",
                    "Forgetting session recording and approval evidence.",
                ],
                "source_ids": ["brief", "nist-207", "owasp-authz"],
            },
            {
                "id": "r1-certification",
                "prompt": "How do access certification campaigns work, and how do you stop them becoming rubber stamps?",
                "evidence": "reported",
                "why": (
                    "The brief lists certification campaigns as a likely topic. It "
                    "tests governance judgement and whether you can design a control "
                    "that actually reduces risk."
                ),
                "model_answer": (
                    "A campaign scopes identities and entitlements, routes them to a "
                    "reviewer — usually the manager or app owner — and records a "
                    "certify or revoke decision. To avoid rubber-stamping: certify "
                    "roles rather than raw entitlements where possible, show risk "
                    "signals (unused access, SoD conflicts, privileged roles), sample "
                    "decisions for quality, and measure revoke rate and time-to-"
                    "revoke. Then prove the remediation actually removed downstream "
                    "access, not just closed the campaign task."
                ),
                "code": "",
                "key_points": [
                    "Scope → reviewer → decision → remediation → evidence.",
                    "Reduce reviewer load; surface risk instead of raw rows.",
                    "Measure revoke rate and remediation time.",
                    "Test that 'revoke' actually revokes downstream.",
                ],
                "follow_ups": [
                    "Who reviews the reviewer?",
                    "How do you handle a reviewer who approves everything?",
                    "What evidence would an auditor ask for?",
                ],
                "traps": [
                    "Treating campaign completion as the outcome.",
                    "No sampling or quality check on decisions.",
                    "Revoking in the IGA tool but not in the target app.",
                ],
                "source_ids": ["brief", "nist-162", "owasp-authz"],
            },
            {
                "id": "r1-mfa",
                "prompt": "What is phishing-resistant MFA, and how would you test an MFA login workflow?",
                "evidence": "reported",
                "why": (
                    "The brief predicts MFA and phishing-resistance questions. It "
                    "is a core authentication control in a financial institution."
                ),
                "model_answer": (
                    "Phishing-resistant means the authenticator is bound to the "
                    "origin and cannot be replayed — FIDO2/WebAuthn security keys or "
                    "passkeys, certificate-based auth. SMS and email OTP are better "
                    "than nothing but are vulnerable to interception and real-time "
                    "phishing. Test: MFA is required for every user and every entry "
                    "point; there is no bypass via a legacy protocol or direct API; "
                    "a replayed assertion fails; lockout and rate limiting work; "
                    "recovery for a lost device is audited; and 'remember this "
                    "device' expires."
                ),
                "code": "",
                "key_points": [
                    "Origin-bound, replay-resistant factors: FIDO2/WebAuthn, certificates.",
                    "SMS/email OTP are weaker — say why, not just 'insecure'.",
                    "Test bypass paths, replay, lockout and recovery.",
                    "NIST 800-63B is the reference for authenticator assurance.",
                ],
                "follow_ups": [
                    "How do you test a passkey enrolment flow?",
                    "What happens if the user loses the device?",
                    "How do you prevent MFA fatigue/push bombing?",
                ],
                "traps": [
                    "Calling SMS 'phishing-resistant'.",
                    "Only testing the happy path with one factor.",
                    "Forgetting recovery and device-trust expiry.",
                ],
                "source_ids": ["brief", "nist-63b", "owasp-authn"],
            },
            {
                "id": "r1-dlp",
                "prompt": "What is data loss prevention, and how would you test a DLP rule?",
                "evidence": "jd",
                "why": (
                    "The brief notes the JD names DLP explicitly, and Schwab's own "
                    "careers page lists Data Loss Prevention as an engineering role "
                    "family. Expect at least one DLP question."
                ),
                "model_answer": (
                    "DLP is policy plus tooling that detects and prevents sensitive "
                    "data — PII, card numbers, account numbers, credentials — from "
                    "leaving through email, endpoints/USB, cloud or the web. A rule "
                    "has a detector, a condition, an action (monitor, block, "
                    "quarantine, encrypt, alert) and an exception path. Test with "
                    "synthetic data: a fake but checksum-valid card number should "
                    "trigger; benign content should pass; an encoded, zipped or "
                    "renamed file should still be caught; the alert must not itself "
                    "contain the sensitive value. Then tune false positives with "
                    "context and measure precision, not just block counts."
                ),
                "code": "",
                "key_points": [
                    "Detector → condition → action → exception → audit.",
                    "Test true positives, true negatives and evasion (encoding, archives, rename).",
                    "Do not put the sensitive value in the alert payload.",
                    "Tune with context; measure false-positive rate.",
                ],
                "follow_ups": [
                    "How do you test DLP on endpoint vs email vs cloud?",
                    "What would you do about a rule that blocks too much?",
                    "How do you prove the alert reached the SOC?",
                ],
                "traps": [
                    "Defining DLP as 'blocking email'.",
                    "Only testing one channel.",
                    "Using real client data in a test.",
                ],
                "source_ids": ["brief", "technology", "nist-dlp"],
            },
            {
                "id": "r1-terminated",
                "prompt": "An employee was terminated yesterday but can still log into an app. How do you troubleshoot?",
                "evidence": "reported",
                "why": (
                    "The brief gives this exact scenario, and it matches your real "
                    "IAM termination-testing experience. It is the strongest "
                    "behavioural-plus-technical answer you have."
                ),
                "model_answer": (
                    "Contain first: confirm the account, disable it, revoke active "
                    "sessions and refresh tokens, and preserve evidence. Then walk "
                    "the chain: did the HR termination event arrive, did IGA mark the "
                    "identity inactive, did the connector run, does the target app "
                    "have a local account, and is there a live SSO session or "
                    "remembered device keeping the user in? Check for a shared or "
                    "service account being misused. Fix the root cause, then add a "
                    "regression test that attempts login after termination and "
                    "asserts failure at the API, not just the UI."
                ),
                "code": "",
                "key_points": [
                    "Contain, preserve evidence, then diagnose.",
                    "Walk HR → IGA → connector → target app → session.",
                    "Sessions/tokens are the usual miss.",
                    "Add a regression test that proves the control.",
                ],
                "follow_ups": [
                    "How would you check whether they accessed anything after termination?",
                    "What if the app is SaaS with its own local admin?",
                    "How do you prevent this class of defect, not just this ticket?",
                ],
                "traps": [
                    "Jumping straight to 'disable the account' and skipping evidence.",
                    "Only checking the IGA console, not the target app.",
                    "Forgetting SSO sessions and refresh tokens.",
                ],
                "source_ids": ["brief", "nist-207", "owasp-authz"],
            },
            {
                "id": "r1-admin-grant",
                "prompt": "A user somehow got admin access without approval. What is your approach?",
                "evidence": "reported",
                "why": (
                    "The brief predicts this scenario. It tests incident thinking, "
                    "root-cause analysis and whether you can turn a one-off into a "
                    "preventive control."
                ),
                "model_answer": (
                    "Treat it as a security incident: contain the access, preserve "
                    "audit evidence, and identify the grant path — direct database "
                    "change, app admin, nested group membership, or a broken approval "
                    "workflow. Check what the account did while privileged and "
                    "whether separation-of-duties was violated. Fix the path, then "
                    "add a preventive control: approval enforced server-side, an "
                    "alert on privileged grants, and a periodic recertification. "
                    "Test the control by trying to grant admin without approval and "
                    "asserting the API rejects it."
                ),
                "code": "",
                "key_points": [
                    "Contain → evidence → grant path → blast radius → fix → prevent.",
                    "Nested groups and direct DB changes are common bypasses.",
                    "Approval must be enforced server-side.",
                    "Add an alert and a negative test.",
                ],
                "follow_ups": [
                    "How do you find every other user with the same grant path?",
                    "What if the audit log is incomplete?",
                    "How do you test SoD violations?",
                ],
                "traps": [
                    "Just removing the access and closing the ticket.",
                    "Not checking what the account did.",
                    "Fixing the UI while the API still allows the grant.",
                ],
                "source_ids": ["brief", "owasp-authz", "nist-207"],
            },
        ],
    },
]

FLOW = {
    "title": "Example 60-minute flow",
    "note": (
        "The brief's predicted shape for a US-based Teams screen. Schwab's own "
        "process page confirms a Talent Advisor call plus additional interviews, "
        "but not this exact agenda — treat the timings as a rehearsal script, not "
        "a published schedule."
    ),
    "segments": [
        {
            "minutes": "0–5",
            "title": "Introductions and role overview",
            "do": "Confirm you can hear each other, thank them, and give the 90-second pitch. Ask one logistics question only if it matters.",
            "evidence": "official",
            "source_ids": ["how-we-hire", "star"],
        },
        {
            "minutes": "5–15",
            "title": "Resume deep dive",
            "do": "Walk the Playwright migration, the 300+ case suite and one IAM investigation. For every claim, have the method and the number ready.",
            "evidence": "reported",
            "source_ids": ["brief"],
        },
        {
            "minutes": "15–30",
            "title": "Coding challenge",
            "do": "Clarify input/output, state edge cases, write compilable Java, then test it aloud. Explain complexity before they ask.",
            "evidence": "reported",
            "source_ids": ["brief", "oracle-map"],
        },
        {
            "minutes": "30–40",
            "title": "API and SQL",
            "do": "For the API: status, schema, negative cases, DB side effect. For SQL: say the join logic before typing, then the security meaning of the rows.",
            "evidence": "reported",
            "source_ids": ["brief", "rest-assured", "postgres-select"],
        },
        {
            "minutes": "40–55",
            "title": "IAM and security scenarios",
            "do": "Use the evidence chain: HR → IGA → connector → target → session. Contain first, then diagnose, then prevent.",
            "evidence": "reported",
            "source_ids": ["brief", "technology", "owasp-authz"],
        },
        {
            "minutes": "55–60",
            "title": "Wrap-up and your questions",
            "do": "Ask two reverse questions tied to the role: how the SDET team plugs into shift-left security, and what success looks like in 90 days.",
            "evidence": "official",
            "source_ids": ["star", "technology"],
        },
    ],
}

GAP = {
    "the_issue": (
        "The brief says the job description asks for 7+ years of QA experience "
        "and 4+ years of automation, while your resume shows about two years. "
        "Do not inflate it. Schwab's published behavioural method rewards "
        "specific, relevant, recent evidence — depth beats a padded timeline."
    ),
    "do": [
        "Acknowledge the gap in one sentence and move on — no apology spiral.",
        "Lead with scope and ownership: 300+ automated tests, the Playwright migration, mentoring, IAM workflows.",
        "Quantify with method: 33% regression reduction measured on the same suite and environment, median of runs.",
        "Map depth to the role: Saviynt IGA, CyberArk PAM, REST Assured, SQL, Java — the exact intersection Schwab names.",
        "Offer the learning plan: what you would ramp on first and how you would prove it.",
    ],
    "dont": [
        "Claim years you do not have.",
        "Say 'I know I'm junior' and stop there.",
        "Recite the resume instead of answering the concern.",
        "Promise expertise you cannot demonstrate under follow-up questions.",
    ],
    "script": (
        "\"The posting describes an ideal of seven years; I'm at about two. "
        "What I can show you is depth in the exact work: I've owned 300+ "
        "automated tests across UI and API, led a Selenium-to-Playwright "
        "migration that cut regression time by roughly a third, and tested "
        "IAM workflows end to end — joiner-mover-leaver, access certification "
        "and termination. I haven't had seven years of reps, but I've had "
        "unusually broad ownership for two, and I ramp quickly. If you want "
        "the person who has seen more codebases, that's a fair question. If "
        "you want someone who can own quality for an IAM surface and grow into "
        "the seniority, that's the case I'm making.\""
    ),
}

TEAMS_NOTES = [
    {
        "title": "The medium does not change the content",
        "detail": (
            "A Teams screen with a US-based interviewer still tests the same "
            "Java, API/SQL and IAM material. What changes is clarity: speak in "
            "complete sentences, pause after each point, and check that the "
            "interviewer is following."
        ),
        "source_ids": ["brief"],
    },
    {
        "title": "Narrate before you type",
        "detail": (
            "Say the approach and edge cases before writing code. If you go quiet "
            "for two minutes, the interviewer learns nothing. If you narrate, "
            "even a partial solution demonstrates the reasoning they are scoring."
        ),
        "source_ids": ["brief"],
    },
    {
        "title": "Time-zone and setup discipline",
        "detail": (
            "Confirm the time zone in writing, join five minutes early, and have "
            "a phone hotspot as backup. The brief flags time-zone differences as "
            "the practical risk of a US-based call."
        ),
        "source_ids": ["brief"],
    },
    {
        "title": "Honesty is a scored behaviour",
        "detail": (
            "Schwab's values include integrity and its behavioural guide asks for "
            "specific, relevant, recent examples. 'I haven't done that hands-on, "
            "but here is how I would approach it' reads as senior. Bluffing "
            "collapses under the first follow-up."
        ),
        "source_ids": ["star", "how-we-hire"],
    },
]

DISCLAIMER = (
    "Official Schwab sources describe the hiring process, the behavioural "
    "method and the technology role families. Schwab does not publish technical "
    "interview questions. The technical questions on this page are predictions "
    "informed by your job description, your round1.md brief and public candidate "
    "reports — not leaked or official Schwab material. Technical answers are "
    "checked against the standards and vendor documentation listed in the source "
    "ledger."
)


def get_round1() -> dict:
    question_count = sum(len(section["questions"]) for section in SECTIONS)
    return {
        "title": "Round 1 Playbook",
        "subtitle": (
            "Specific to the Schwab SDET - Cyber Security QA first round: "
            "Java and automation, API/SQL, IAM and DLP, the 60-minute flow, and "
            "how to handle the experience gap."
        ),
        "question_count": question_count,
        "official_process": OFFICIAL_PROCESS,
        "sections": SECTIONS,
        "flow": FLOW,
        "gap": GAP,
        "teams_notes": TEAMS_NOTES,
        "sources": SOURCES,
        "disclaimer": DISCLAIMER,
    }
