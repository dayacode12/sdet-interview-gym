"""Java-for-automation interview questions. 'design' type questions are not executed."""
from __future__ import annotations

JAVA_AUTOMATION_QUESTIONS = [
    {
        "id": "java-parse-json-manually",
        "title": "Count objects in a JSON array without libraries",
        "category": "Java for Automation",
        "subcategory": "Parse JSON",
        "type": "code",
        "difficulty": "medium",
        "problem": (
            "You receive a JSON array of user objects as a single line, for example "
            '[{"id": 1, "name": "a"}, {"id": 2, "name": "b"}]. '
            "Without using any JSON library, print the number of objects in the array. "
            "Assume well-formed JSON with no nested objects and no braces inside string values."
        ),
        "input_format": "A single line containing a JSON array.",
        "output_format": "The number of objects in the array.",
        "constraints": "No external libraries. Handle empty array [].",
        "starter_code": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        String json = sc.nextLine();\n"
            "        // TODO: count objects without JSON libraries\n"
            "        System.out.println();\n"
            "    }\n"
            "}\n"
        ),
        "tests": [
            {"name": "two objects", "stdin": '[{"id": 1, "name": "a"}, {"id": 2, "name": "b"}]\n', "expected": "2"},
            {"name": "empty array", "stdin": "[]\n", "expected": "0"},
            {"name": "single object", "stdin": '[{"id": 9, "name": "z"}]\n', "expected": "1"},
        ],
        "solution": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        String json = sc.nextLine();\n\n"
            "        int objects = 0;\n"
            "        for (char c : json.toCharArray()) {\n"
            "            if (c == '{') objects++;\n"
            "        }\n"
            "        System.out.println(objects);\n"
            "    }\n"
            "}\n"
        ),
        "explanation": (
            "With the stated constraints (no nesting), counting top-level '{' characters equals the "
            "object count. In production you would use a real parser: RestAssured's JsonPath, "
            "org.json, or Jackson. This exercise proves you understand what a parser does for you. "
            "Be ready to say clearly: manual parsing is for interviews only — never for production "
            "test code, because escaped quotes, nesting and unicode will break it."
        ),
        "time_complexity": "O(n)",
        "space_complexity": "O(1)",
        "hints": [
            "Count top-level '{' characters given the no-nesting constraint.",
            "State out loud that production code would use JsonPath or Jackson.",
            "Ask the interviewer about nesting before committing to the simple count.",
        ],
        "followups": [
            "How would you extract a field with JsonPath in REST Assured? (path(\"id\"))",
            "Why is regex/manual parsing dangerous for real JSON? (escapes, nesting, types)",
            "How would you validate the full JSON schema instead of one field?",
        ],
    },
    {
        "id": "java-extract-json-field",
        "title": "Extract and assert a JSON response field (REST Assured)",
        "category": "Java for Automation",
        "subcategory": "Read JSON response",
        "type": "design",
        "difficulty": "medium",
        "problem": (
            "Write a REST Assured test that calls GET /api/users/{id}, extracts the role field "
            "from the JSON response and asserts it equals the expected role. Show both the "
            "built-in assertion style and an explicit extraction style."
        ),
        "input_format": "Not an executable exercise — write the code and explain it.",
        "output_format": "A compilable REST Assured test.",
        "constraints": "Use given()/when()/then() fluency. Show JsonPath extraction.",
        "starter_code": (
            "import static io.restassured.RestAssured.*;\n"
            "import static org.hamcrest.Matchers.*;\n"
            "import org.testng.annotations.Test;\n\n"
            "public class GetUserTest {\n"
            "    // TODO: GET /api/users/42 and validate role == 'EMPLOYEE'\n"
            "}\n"
        ),
        "tests": [],
        "solution": (
            "import static io.restassured.RestAssured.*;\n"
            "import static org.hamcrest.Matchers.*;\n"
            "import org.testng.annotations.Test;\n\n"
            "public class GetUserTest {\n\n"
            "    // Style 1: declarative assertion in the then() block\n"
            "    @Test\n"
            "    public void validateRoleDeclaratively() {\n"
            "        given()\n"
            "            .baseUri(\"https://iam.example.com\")\n"
            "            .auth().oauth2(\"<bearer-token>\")\n"
            "            .pathParam(\"id\", 42)\n"
            "        .when()\n"
            "            .get(\"/api/users/{id}\")\n"
            "        .then()\n"
            "            .statusCode(200)\n"
            "            .body(\"role\", equalTo(\"EMPLOYEE\"));\n"
            "    }\n\n"
            "    // Style 2: extract the value and assert explicitly (better for reporting)\n"
            "    @Test\n"
            "    public void validateRoleViaJsonPath() {\n"
            "        String role =\n"
            "            given()\n"
            "                .baseUri(\"https://iam.example.com\")\n"
            "                .auth().oauth2(\"<bearer-token>\")\n"
            "            .when()\n"
            "                .get(\"/api/users/42\")\n"
            "            .then()\n"
            "                .statusCode(200)\n"
            "                .extract().jsonPath().getString(\"role\");\n\n"
            "        assert \"EMPLOYEE\".equals(role)\n"
            "            : \"Expected role EMPLOYEE but found \" + role;\n"
            "    }\n"
            "}\n"
        ),
        "explanation": (
            "Style 1 keeps the assertion inside the fluent chain and reads like a specification. "
            "Style 2 extracts with JsonPath so you can log the actual value, compare it with the "
            "database, or pass it to the next step (API chaining). In IAM testing you almost always "
            "want style 2 eventually, because the API role must be cross-checked against the "
            "database and the UI — a single then() assertion cannot do that."
        ),
        "time_complexity": "N/A",
        "space_complexity": "N/A",
        "hints": [
            "given().when().then() is the REST Assured flow.",
            "extract().jsonPath().getString(\"role\") pulls a field out for further checks.",
            "auth().oauth2(token) attaches a bearer token.",
        ],
        "followups": [
            "How would you validate a list field, e.g. every entitlement in an array?",
            "How do you validate the response against a JSON schema? (matchesJsonSchemaInClasspath)",
            "How would you assert both the API response and the database value in one test?",
        ],
    },
    {
        "id": "java-safe-parse",
        "title": "Handle exceptions when parsing input",
        "category": "Java for Automation",
        "subcategory": "Handle exceptions",
        "type": "code",
        "difficulty": "easy",
        "problem": (
            "Read lines from stdin until EOF. Each line should contain an integer. "
            "Print the parsed value for valid lines and 'ERROR: <line>' for invalid lines. "
            "The program must never crash: any parsing failure is reported, not thrown. "
            "Blank lines are skipped silently."
        ),
        "input_format": "Multiple lines until EOF.",
        "output_format": "One line per input line: the integer, or 'ERROR: <original line>'.",
        "constraints": "No stack traces may reach stdout. Use try/catch around the parse.",
        "starter_code": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    // TODO: parse each line defensively\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        while (sc.hasNextLine()) {\n"
            "            String line = sc.nextLine();\n"
            "            // TODO: parse safely\n"
            "        }\n"
            "    }\n"
            "}\n"
        ),
        "tests": [
            {"name": "mixed valid and invalid", "stdin": "5\nabc\n-3\n\n12x\n", "expected": "5\nERROR: abc\n-3\nERROR: 12x"},
            {"name": "all valid", "stdin": "1\n2\n3\n", "expected": "1\n2\n3"},
        ],
        "solution": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        while (sc.hasNextLine()) {\n"
            "            String line = sc.nextLine();\n"
            "            if (line.isBlank()) continue;\n"
            "            try {\n"
            "                int value = Integer.parseInt(line.trim());\n"
            "                System.out.println(value);\n"
            "            } catch (NumberFormatException e) {\n"
            "                System.out.println(\"ERROR: \" + line);\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "}\n"
        ),
        "explanation": (
            "NumberFormatException is unchecked and is thrown by Integer.parseInt. Catching the "
            "specific exception — not a blanket catch (Exception) — is the point of this question. "
            "This defensive parsing is exactly what a robust automation utility does when it reads "
            "test data files: one bad row must not kill the whole suite."
        ),
        "time_complexity": "O(total input size)",
        "space_complexity": "O(1)",
        "hints": [
            "Integer.parseInt throws NumberFormatException — catch it, never let it escape.",
            "Blank lines: skip with isBlank() before parsing.",
            "In automation terms: one bad row of test data must not abort the run.",
        ],
        "followups": [
            "Checked vs unchecked exceptions — give examples of each.",
            "Why is catch (Exception e) usually a bad idea?",
            "How do try-with-resources and finally differ?",
        ],
    },
    {
        "id": "java-reusable-validation",
        "title": "Create a reusable validation method",
        "category": "Java for Automation",
        "subcategory": "Create reusable methods",
        "type": "code",
        "difficulty": "easy",
        "problem": (
            "Implement a reusable method isValidUsername(String) that returns true when the "
            "username is 5-12 characters long and contains only letters and digits. "
            "Read lines until EOF and print VALID or INVALID for each."
        ),
        "input_format": "Multiple lines until EOF.",
        "output_format": "VALID or INVALID per line.",
        "constraints": "null input counts as INVALID.",
        "starter_code": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    // TODO: static boolean isValidUsername(String username)\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        while (sc.hasNextLine()) {\n"
            "            String line = sc.nextLine();\n"
            "            // TODO: call isValidUsername and print VALID / INVALID\n"
            "        }\n"
            "    }\n"
            "}\n"
        ),
        "tests": [
            {"name": "mixed", "stdin": "daya123\nab\nvalid_user\nDaya9\nx!\n", "expected": "VALID\nINVALID\nINVALID\nVALID\nINVALID"},
            {"name": "boundary lengths", "stdin": "abcde\nabcdefghijkl\nabcdefghijklm\n", "expected": "VALID\nVALID\nINVALID"},
        ],
        "solution": (
            "import java.util.*;\n\n"
            "public class Main {\n\n"
            "    static boolean isValidUsername(String username) {\n"
            "        if (username == null) return false;\n"
            "        if (username.length() < 5 || username.length() > 12) return false;\n"
            "        for (char c : username.toCharArray()) {\n"
            "            if (!Character.isLetterOrDigit(c)) return false;\n"
            "        }\n"
            "        return true;\n"
            "    }\n\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        while (sc.hasNextLine()) {\n"
            "            System.out.println(isValidUsername(sc.nextLine()) ? \"VALID\" : \"INVALID\");\n"
            "        }\n"
            "    }\n"
            "}\n"
        ),
        "explanation": (
            "The guard clauses (null, length, then character scan) make the method independently "
            "testable — that is the real interview point: extraction into a pure static method is "
            "how reusable automation utilities are born. 'valid_user' is INVALID because the "
            "underscore is neither a letter nor a digit."
        ),
        "time_complexity": "O(n) per username",
        "space_complexity": "O(1)",
        "hints": [
            "Guard clauses first: null check, length check, then character scan.",
            "Character.isLetterOrDigit handles the character rule.",
            "A pure static method like this is trivially unit-testable — say that.",
        ],
        "followups": [
            "How would you unit test this method (which cases must you cover)?",
            "How would the design change if the rules came from a config file?",
            "Where does this pattern appear in your automation framework?",
        ],
    },
    {
        "id": "java-basepage-inheritance",
        "title": "Design a BasePage class using inheritance",
        "category": "Java for Automation",
        "subcategory": "Implement inheritance",
        "type": "design",
        "difficulty": "medium",
        "problem": (
            "Design a BasePage class for a Selenium Page Object framework. It should hold the "
            "WebDriver and WebDriverWait, expose a reusable waitForClickable(WebElement) helper "
            "and a safeClick helper, and be extended by a LoginPage that uses them. "
            "Explain what inheritance buys you here."
        ),
        "input_format": "Not an executable exercise — write the class design.",
        "output_format": "BasePage + LoginPage skeleton with constructors wired correctly.",
        "constraints": "WebDriver must be passed in, never instantiated inside the page class.",
        "starter_code": (
            "public class BasePage {\n"
            "    // TODO: WebDriver + WebDriverWait fields, constructor,\n"
            "    // TODO: protected waitForClickable / safeClick helpers\n"
            "}\n\n"
            "public class LoginPage extends BasePage {\n"
            "    // TODO: login() using the inherited helpers\n"
            "}\n"
        ),
        "tests": [],
        "solution": (
            "import java.time.Duration;\n"
            "import org.openqa.selenium.*;\n"
            "import org.openqa.selenium.support.ui.*;\n\n"
            "public class BasePage {\n"
            "    protected final WebDriver driver;\n"
            "    protected final WebDriverWait wait;\n\n"
            "    public BasePage(WebDriver driver) {\n"
            "        this.driver = driver;\n"
            "        this.wait = new WebDriverWait(driver, Duration.ofSeconds(10));\n"
            "    }\n\n"
            "    protected WebElement waitForClickable(WebElement element) {\n"
            "        return wait.until(ExpectedConditions.elementToBeClickable(element));\n"
            "    }\n\n"
            "    protected void safeClick(WebElement element) {\n"
            "        waitForClickable(element).click();\n"
            "    }\n"
            "}\n\n"
            "public class LoginPage extends BasePage {\n"
            "    private final By username = By.id(\"username\");\n"
            "    private final By password = By.id(\"password\");\n"
            "    private final By submit   = By.id(\"loginButton\");\n\n"
            "    public LoginPage(WebDriver driver) {\n"
            "        super(driver);              // BasePage constructor wires driver + wait\n"
            "    }\n\n"
            "    public void login(String user, String pass) {\n"
            "        driver.findElement(username).sendKeys(user);\n"
            "        driver.findElement(password).sendKeys(pass);\n"
            "        safeClick(driver.findElement(submit));\n"
            "    }\n"
            "}\n"
        ),
        "explanation": (
            "Inheritance centralises wait/click behaviour in one place: fix a flaky-click strategy once "
            "and every page benefits. super(driver) is mandatory — the parent constructor runs first. "
            "Composition is the alternative (a WaitHelper object injected into pages) and is arguably "
            "cleaner; mentioning that trade-off scores points. The WebDriver is injected, never "
            "created inside a page, which keeps pages testable and thread-safe under parallel runs."
        ),
        "time_complexity": "N/A",
        "space_complexity": "N/A",
        "hints": [
            "protected fields + constructor injection: pages receive the driver, never create it.",
            "super(driver) must be the first statement of the child constructor.",
            "Be ready to defend inheritance vs composition for the wait helpers.",
        ],
        "followups": [
            "Why must the child constructor call super(driver)?",
            "Inheritance vs composition for shared wait logic — argue both.",
            "How does this design behave under parallel TestNG execution?",
        ],
    },
    {
        "id": "java-wait-strategy-interface",
        "title": "Implement an interface for wait strategies",
        "category": "Java for Automation",
        "subcategory": "Implement interfaces",
        "type": "design",
        "difficulty": "medium",
        "problem": (
            "Define a WaitStrategy interface with a single method apply(WebDriver, By) that "
            "returns WebElement. Implement two strategies: ClickableWait and VisibleWait. "
            "Show how a caller picks a strategy without if/else chains. "
            "Explain why an interface beats an enum-with-switch here."
        ),
        "input_format": "Not an executable exercise — write the interface and implementations.",
        "output_format": "Interface + two implementations + a polymorphic caller.",
        "constraints": "No if/else on strategy type at the call site.",
        "starter_code": (
            "public interface WaitStrategy {\n"
            "    // TODO: WebElement apply(WebDriver driver, By locator);\n"
            "}\n"
        ),
        "tests": [],
        "solution": (
            "import java.time.Duration;\n"
            "import org.openqa.selenium.*;\n"
            "import org.openqa.selenium.support.ui.*;\n\n"
            "public interface WaitStrategy {\n"
            "    WebElement apply(WebDriver driver, By locator);\n"
            "}\n\n"
            "class ClickableWait implements WaitStrategy {\n"
            "    @Override\n"
            "    public WebElement apply(WebDriver driver, By locator) {\n"
            "        return new WebDriverWait(driver, Duration.ofSeconds(10))\n"
            "            .until(ExpectedConditions.elementToBeClickable(locator));\n"
            "    }\n"
            "}\n\n"
            "class VisibleWait implements WaitStrategy {\n"
            "    @Override\n"
            "    public WebElement apply(WebDriver driver, By locator) {\n"
            "        return new WebDriverWait(driver, Duration.ofSeconds(10))\n"
            "            .until(ExpectedConditions.visibilityOfElementLocated(locator));\n"
            "    }\n"
            "}\n\n"
            "class Element {\n"
            "    private final WaitStrategy strategy;   // injected — no if/else at call site\n"
            "    Element(WaitStrategy strategy) { this.strategy = strategy; }\n\n"
            "    WebElement resolve(WebDriver driver, By locator) {\n"
            "        return strategy.apply(driver, locator);\n"
            "    }\n"
            "}\n"
        ),
        "explanation": (
            "Polymorphism replaces branching: Element.resolve() calls whichever strategy was injected. "
            "Adding a third strategy (e.g. PresentWait) requires zero changes to existing code — "
            "that is the Open/Closed principle in practice. This mirrors how real frameworks "
            "(including Selenium's own ExpectedConditions and Playwright's auto-wait states) "
            "model waiting as pluggable behaviour."
        ),
        "time_complexity": "N/A",
        "space_complexity": "N/A",
        "hints": [
            "One-method interfaces are the classic strategy pattern.",
            "The caller holds a WaitStrategy reference and calls apply() — no type checks.",
            "New strategy = new class, zero edits elsewhere (Open/Closed principle).",
        ],
        "followups": [
            "Default methods in interfaces — when would you use one here?",
            "Abstract class vs interface: how do you choose?",
            "How does Playwright's auto-waiting remove the need for most of this code?",
        ],
    },
    {
        "id": "java-test-suite-collections",
        "title": "Manage a test suite with Collections",
        "category": "Java for Automation",
        "subcategory": "Use collections",
        "type": "code",
        "difficulty": "medium",
        "problem": (
            "Read test case names from stdin, one per line, until EOF. Lines starting with "
            "'SKIP:' mark a test that must be excluded. Print: (1) the number of unique runnable "
            "tests, (2) the names sorted alphabetically, one per line, prefixed 'TEST: ', then "
            "(3) the skipped names in input order prefixed 'SKIP: '. Deduplicate by name."
        ),
        "input_format": "Lines until EOF. A skipped line looks like 'SKIP: flakyLogin'.",
        "output_format": "First line 'count: N', then sorted runnable tests, then skipped tests in input order.",
        "constraints": "A name may appear both as runnable and skipped — being skipped always wins.",
        "starter_code": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        // TODO: collect, dedupe, exclude, sort\n"
            "    }\n"
            "}\n"
        ),
        "tests": [
            {
                "name": "mixed suite",
                "stdin": "loginTest\nSKIP: flakyLogin\ndashboardTest\nloginTest\nSKIP: duplicateTest\nduplicateTest\n",
                "expected": "count: 2\nTEST: dashboardTest\nTEST: loginTest\nSKIP: flakyLogin\nSKIP: duplicateTest",
            },
            {"name": "empty input", "stdin": "", "expected": "count: 0"},
        ],
        "solution": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        Set<String> skipped = new LinkedHashSet<>();   // preserves input order\n"
            "        Set<String> runnable = new LinkedHashSet<>();  // dedupe + order\n"
            "        while (sc.hasNextLine()) {\n"
            "            String line = sc.nextLine().trim();\n"
            "            if (line.isEmpty()) continue;\n"
            "            if (line.startsWith(\"SKIP:\")) {\n"
            "                skipped.add(line.substring(5).trim());\n"
            "            } else {\n"
            "                runnable.add(line);\n"
            "            }\n"
            "        }\n"
            "        runnable.removeAll(skipped);                    // skipped always wins\n"
            "        List<String> sorted = new ArrayList<>(runnable);\n"
            "        Collections.sort(sorted);\n"
            "        System.out.println(\"count: \" + sorted.size());\n"
            "        for (String t : sorted) System.out.println(\"TEST: \" + t);\n"
            "        for (String s : skipped) System.out.println(\"SKIP: \" + s);\n"
            "    }\n"
            "}\n"
        ),
        "explanation": (
            "Three collection choices carry the design: LinkedHashSet for input order + dedupe, "
            "removeAll for the exclusion rule, then a sorted copy for reporting. removeAll is O(n) "
            "average because both are hash sets. This mirrors a real suite filter: read names, "
            "exclude the quarantine list, sort for a stable report — the same logic TestNG suite "
            "filters and CI exclusion lists perform."
        ),
        "time_complexity": "O(n log n) for the final sort",
        "space_complexity": "O(n)",
        "hints": [
            "LinkedHashSet for dedupe + order, removeAll for exclusion, sort a copy for output.",
            "A name in both lists is excluded — apply removeAll AFTER collecting everything.",
            "Print the count after exclusion, not before.",
        ],
        "followups": [
            "Why LinkedHashSet rather than TreeSet for the input phase?",
            "How would you return tests matching a pattern (e.g. smoke only)?",
            "Where in your framework did you use this exact pattern?",
        ],
    },
    {
        "id": "java-soft-assertions",
        "title": "Write reusable soft assertions",
        "category": "Java for Automation",
        "subcategory": "Write reusable assertions",
        "type": "design",
        "difficulty": "medium",
        "problem": (
            "Design a SoftAssertUtil class that collects assertion failures instead of throwing on "
            "the first one, reports every failure at the end, and throws a single AssertionError "
            "containing all messages if anything failed. Explain why hard asserts alone are a "
            "problem in UI automation."
        ),
        "input_format": "Not an executable exercise — write the utility class.",
        "output_format": "A SoftAssertUtil with assertEquals / assertTrue and a final assertAll().",
        "constraints": "Thread-safety is out of scope; correctness of collect-then-throw is the goal.",
        "starter_code": (
            "import java.util.*;\n\n"
            "public class SoftAssertUtil {\n"
            "    // TODO: collect failures, assertEquals, assertTrue, assertAll\n"
            "}\n"
        ),
        "tests": [],
        "solution": (
            "import java.util.*;\n\n"
            "public class SoftAssertUtil {\n"
            "    private final List<String> failures = new ArrayList<>();\n\n"
            "    public void assertEquals(Object actual, Object expected, String label) {\n"
            "        if (actual == null ? expected != null : !actual.equals(expected)) {\n"
            "            failures.add(label + \": expected <\" + expected + \"> but found <\" + actual + \">\");\n"
            "        }\n"
            "    }\n\n"
            "    public void assertTrue(boolean condition, String label) {\n"
            "        if (!condition) {\n"
            "            failures.add(label + \": expected true but found false\");\n"
            "        }\n"
            "    }\n\n"
            "    public void assertAll() {\n"
            "        if (!failures.isEmpty()) {\n"
            "            StringBuilder sb = new StringBuilder(\"Soft assertion failures:\");\n"
            "            for (int i = 0; i < failures.size(); i++) {\n"
            "                sb.append(\"\\n  \").append(i + 1).append(\") \").append(failures.get(i));\n"
            "            }\n"
            "            throw new AssertionError(sb.toString());\n"
            "        }\n"
            "    }\n"
            "}\n\n"
            "// Usage inside a TestNG test:\n"
            "// SoftAssertUtil soft = new SoftAssertUtil();\n"
            "// soft.assertEquals(page.getRole(), \"EMPLOYEE\", \"UI role\");\n"
            "// soft.assertTrue(page.isLogoutVisible(), \"logout link\");\n"
            "// soft.assertAll();   // throws once, with every failure listed\n"
        ),
        "explanation": (
            "Hard asserts stop at the first failure, so one broken field hides every other defect on "
            "the page — with soft asserts you get the full failure report per test. Collect-then-throw "
            "at assertAll() is the same idea as TestNG's SoftAssert and AssertJ's soft assertions. "
            "Interviewers love the note that the failure list should also be logged (Extent/Allure) "
            "for evidence, not just thrown."
        ),
        "time_complexity": "N/A",
        "space_complexity": "N/A",
        "hints": [
            "Accumulate failure messages in a List; throw once in assertAll().",
            "This is TestNG's SoftAssert pattern — name it.",
            "Pair it with screenshot/log capture on failure for evidence.",
        ],
        "followups": [
            "When is a hard assert actually the right choice?",
            "How would you make this utility thread-safe for parallel runs?",
            "How do soft assertions interact with retry-analyzer logic for flaky tests?",
        ],
    },
    {
        "id": "java-dataprovider",
        "title": "Feed a test from a DataProvider",
        "category": "Java for Automation",
        "subcategory": "Test data providers",
        "type": "design",
        "difficulty": "medium",
        "problem": (
            "Write a TestNG DataProvider that supplies username/role pairs for a login test, "
            "reading rows from a two-column source. Show the test method consuming it with "
            "@Test(dataProvider = ...) and explain how TestNG treats each row."
        ),
        "input_format": "Not an executable exercise — write the provider and test.",
        "output_format": "DataProvider returning Object[][] + a parameterised test.",
        "constraints": "Each data row must run as an independent test instance.",
        "starter_code": (
            "import org.testng.annotations.DataProvider;\n"
            "import org.testng.annotations.Test;\n\n"
            "public class LoginDataDrivenTest {\n"
            "    // TODO: @DataProvider users() -> Object[][]\n"
            "    // TODO: @Test(dataProvider = \"users\") login(username, role)\n"
            "}\n"
        ),
        "tests": [],
        "solution": (
            "import org.testng.annotations.DataProvider;\n"
            "import org.testng.annotations.Test;\n\n"
            "public class LoginDataDrivenTest {\n\n"
            "    @DataProvider(name = \"users\")\n"
            "    public Object[][] users() {\n"
            "        return new Object[][] {\n"
            "            {\"daya\",   \"EMPLOYEE\"},\n"
            "            {\"admin01\", \"ADMIN\"},\n"
            "            {\"auditor\", \"AUDITOR\"},\n"
            "            {\"locked\",  \"LOCKED\"}   // negative row: login must be denied\n"
            "        };\n"
            "    }\n\n"
            "    @Test(dataProvider = \"users\")\n"
            "    public void loginAs(String username, String role) {\n"
            "        LoginPage page = new LoginPage(DriverManager.get());\n"
            "        page.login(username, TestUsers.passwordFor(username));\n"
            "        switch (role) {\n"
            "            case \"LOCKED\" -> org.testng.Assert.assertFalse(page.isLoggedIn(),\n"
            "                    username + \" must be denied\");\n"
            "            default -> org.testng.Assert.assertEquals(page.getRole(), role,\n"
            "                    username + \" must see role \" + role);\n"
            "        }\n"
            "    }\n"
            "}\n"
        ),
        "explanation": (
            "TestNG runs the test method once per row and reports each row separately — "
            "loginAs('locked') failing does not hide loginAs('daya') passing. Object[][] is the "
            "required shape; each inner array maps to the method parameters positionally. "
            "In production the rows come from Excel/CSV/JSON via the same contract, which is how "
            "you separate test logic from test data."
        ),
        "time_complexity": "N/A",
        "space_complexity": "N/A",
        "hints": [
            "Object[][] with one inner array per row, mapped to method parameters.",
            "Each row = one independently reported test — say that sentence explicitly.",
            "Keep expected outcomes in the data (positive AND negative rows).",
        ],
        "followups": [
            "How would you source the same rows from a CSV or JSON file?",
            "Data-driven testing vs parameterised testing — what is the difference in TestNG?",
            "How does parallel execution interact with shared mutable test data?",
        ],
    },
    {
        "id": "java-page-object",
        "title": "Design a Page Object class",
        "category": "Java for Automation",
        "subcategory": "Design a Page Object class",
        "type": "design",
        "difficulty": "medium",
        "problem": (
            "Design a LoginPage Page Object for a login flow: username field, password field, "
            "submit button, and an error banner. Methods: login(user, pass) returning the next "
            "page, and getErrorText(). Locators as By constants, waits inside the page, "
            "no assertions inside the page class. Explain the responsibilities split."
        ),
        "input_format": "Not an executable exercise — write the page object.",
        "output_format": "LoginPage with private locators, login() and getErrorText().",
        "constraints": "No assertions, no test data, no driver creation inside the page.",
        "starter_code": (
            "import org.openqa.selenium.*;\n\n"
            "public class LoginPage {\n"
            "    // TODO: locators, constructor, login(), getErrorText()\n"
            "}\n"
        ),
        "tests": [],
        "solution": (
            "import java.time.Duration;\n"
            "import org.openqa.selenium.*;\n"
            "import org.openqa.selenium.support.ui.*;\n\n"
            "public class LoginPage {\n"
            "    private final WebDriver driver;\n"
            "    private final WebDriverWait wait;\n\n"
            "    private static final By USERNAME = By.cssSelector(\"input[name='username']\");\n"
            "    private static final By PASSWORD = By.cssSelector(\"input[name='password']\");\n"
            "    private static final By SUBMIT   = By.cssSelector(\"button[type='submit']\");\n"
            "    private static final By ERROR    = By.cssSelector(\".login-error\");\n\n"
            "    public LoginPage(WebDriver driver) {\n"
            "        this.driver = driver;\n"
            "        this.wait = new WebDriverWait(driver, Duration.ofSeconds(10));\n"
            "    }\n\n"
            "    /** Performs login and returns the landing page. */\n"
            "    public DashboardPage login(String user, String pass) {\n"
            "        driver.findElement(USERNAME).sendKeys(user);\n"
            "        driver.findElement(PASSWORD).sendKeys(pass);\n"
            "        wait.until(ExpectedConditions.elementToBeClickable(SUBMIT)).click();\n"
            "        return new DashboardPage(driver);   // fluent navigation\n"
            "    }\n\n"
            "    /** Text of the error banner, or empty string when absent. */\n"
            "    public String getErrorText() {\n"
            "        try {\n"
            "            return wait.until(ExpectedConditions.visibilityOfElementLocated(ERROR)).getText();\n"
            "        } catch (TimeoutException e) {\n"
            "            return \"\";\n"
            "        }\n"
            "    }\n"
            "}\n"
        ),
        "explanation": (
            "POM splits responsibilities: the page owns locators and interactions; the test owns "
            "assertions and flow. When the UI changes, you fix one locator in one class instead of "
            "hundreds of scripts. login() returning DashboardPage models navigation fluently. "
            "Methods never assert — that is the discipline interviewers check for. Note the catch of "
            "TimeoutException in getErrorText(): 'error banner absent' is a valid outcome, not a "
            "framework crash."
        ),
        "time_complexity": "N/A",
        "space_complexity": "N/A",
        "hints": [
            "Locators private + static final; interactions public; assertions OUTSIDE the page.",
            "login() should return the next page object for fluent navigation.",
            "Waits live inside the page, never as Thread.sleep in tests.",
        ],
        "followups": [
            "How do you keep page objects maintainable when the UI changes weekly?",
            "How would the same page object look in Playwright? (locators auto-wait)",
            "Where do you put assertions, and why not inside page methods?",
        ],
    },
    {
        "id": "java-dynamic-xpath",
        "title": "Build dynamic locators",
        "category": "Java for Automation",
        "subcategory": "Locators",
        "type": "design",
        "difficulty": "medium",
        "problem": (
            "Write a utility method that locates a table row by a dynamic cell value — e.g. find "
            "the row of an access request by request ID — using both a parameterised XPath and a "
            "CSS alternative. Explain the security and stability implications of string-built XPath."
        ),
        "input_format": "Not an executable exercise — write the utility and discuss trade-offs.",
        "output_format": "A locator utility with an XPath version and a CSS/data-attribute version.",
        "constraints": "The dynamic value comes from test data and must be escaped safely.",
        "starter_code": (
            "import org.openqa.selenium.*;\n\n"
            "public class TableLocator {\n"
            "    // TODO: static By rowByRequestId(String requestId)\n"
            "}\n"
        ),
        "tests": [],
        "solution": (
            "import org.openqa.selenium.*;\n\n"
            "public class TableLocator {\n\n"
            "    /** XPath version: parameterised, never string-concatenated raw input. */\n"
            "    public static By rowByRequestIdXPath(String requestId) {\n"
            "        String safe = requestId.replace(\"\\\"\", \"&quot;\")   // escape quotes\n"
            "                              .replace(\"'\", \"&apos;\");\n"
            "        return By.xpath(\"//tr[td[text()='\" + safe + \"']]\");\n"
            "    }\n\n"
            "    /** CSS version: requires a data- attribute in the app under test. */\n"
            "    public static By rowByRequestIdCss(String requestId) {\n"
            "        return By.cssSelector(\"tr[data-request-id='\" + requestId + \"']\");\n"
            "    }\n"
            "}\n\n"
            "// Discussion points:\n"
            "// 1. Prefer unique data-* attributes over positional XPath (//tr[3]) — position breaks.\n"
            "// 2. Escaping quotes prevents locator injection and 'not found' failures.\n"
            "// 3. A test-attribute contract with developers (data-testid) is the most stable strategy.\n"
            "// 4. XPath engines are slower than CSS for very large DOMs; measure, do not assume.\n"
        ),
        "explanation": (
            "Dynamic locators are unavoidable in IAM dashboards (find this request, this user, this "
            "entitlement row). The strong answer covers: (1) escape user-supplied values in XPath "
            "string literals, (2) prefer semantic data-* attributes agreed with developers, "
            "(3) avoid positional axes that break on sorting, and (4) know that CSS selectors cannot "
            "traverse upward (parent()) while XPath can — a genuine technical differentiator, not "
            "just style."
        ),
        "time_complexity": "N/A",
        "space_complexity": "N/A",
        "hints": [
            "Escape quotes in dynamic values before embedding them in XPath.",
            "data-testid attributes agreed with developers beat fragile positional XPath.",
            "XPath can traverse up (parent::) and text-match; CSS cannot.",
        ],
        "followups": [
            "What makes //div[7]/table[2]/tr[13]/td[4] fragile?",
            "How do you debug 'element not found' — relative vs absolute XPath?",
            "How would Playwright's getByRole/getByText change this code?",
        ],
    },
    {
        "id": "java-retry-logic",
        "title": "Implement retry logic safely",
        "category": "Java for Automation",
        "subcategory": "Flaky test handling",
        "type": "code",
        "difficulty": "medium",
        "problem": (
            "Implement retry logic: an operation is retried up to 5 times with an increasing delay "
            "between attempts (delay = attempt number seconds, simulated without sleeping — just "
            "count it). Read an integer k: the operation fails the first k times then succeeds. "
            "Print 'SUCCESS after N attempts' when it succeeds within 5 attempts, "
            "otherwise 'FAILED after 5 attempts'."
        ),
        "input_format": "A single integer k: the number of initial failures before success.",
        "output_format": "SUCCESS after N attempts, or FAILED after 5 attempts.",
        "constraints": "Max 5 attempts total. The retry loop must have a hard bound — an unbounded retry is a bug.",
        "starter_code": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    static int failuresLeft;\n\n"
            "    static boolean flakyOperation() {\n"
            "        if (failuresLeft > 0) { failuresLeft--; return false; }\n"
            "        return true;\n"
            "    }\n\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        failuresLeft = Integer.parseInt(sc.nextLine().trim());\n"
            "        // TODO: bounded retry with growing backoff (no real sleeping needed)\n"
            "        System.out.println();\n"
            "    }\n"
            "}\n"
        ),
        "tests": [
            {"name": "succeeds on third attempt", "stdin": "2\n", "expected": "SUCCESS after 3 attempts"},
            {"name": "succeeds immediately", "stdin": "0\n", "expected": "SUCCESS after 1 attempts"},
            {"name": "exceeds retries", "stdin": "7\n", "expected": "FAILED after 5 attempts"},
        ],
        "solution": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    static int failuresLeft;\n\n"
            "    static boolean flakyOperation() {\n"
            "        if (failuresLeft > 0) { failuresLeft--; return false; }\n"
            "        return true;\n"
            "    }\n\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        failuresLeft = Integer.parseInt(sc.nextLine().trim());\n\n"
            "        final int MAX_ATTEMPTS = 5;\n"
            "        int attempt = 0;\n"
            "        boolean success = false;\n"
            "        while (attempt < MAX_ATTEMPTS) {\n"
            "            attempt++;\n"
            "            if (flakyOperation()) { success = true; break; }\n"
            "            // exponential-ish backoff: in real code Thread.sleep(attempt * 1000L)\n"
            "            // or a TestNG IRetryAnalyzer; here we only count it.\n"
            "        }\n"
            "        System.out.println((success ? \"SUCCESS after \" : \"FAILED after \") + attempt + \" attempts\");\n"
            "    }\n"
            "}\n"
        ),
        "explanation": (
            "Retries must be bounded and observable: a hard attempt limit, a backoff that grows, "
            "logging of every attempt, and a final failure that is reported, not swallowed. "
            "In TestNG this is IRetryAnalyzer with maxRetryCount; in Playwright you often do not "
            "need it at all because auto-waiting removes the race conditions that cause flakiness. "
            "The interview-winning sentence: retries treat the symptom — first classify whether the "
            "failure is a product defect, an environment issue or an automation bug."
        ),
        "time_complexity": "O(attempts)",
        "space_complexity": "O(1)",
        "hints": [
            "Hard bound on attempts — unbounded retry loops are production incidents.",
            "Backoff should grow (linear or exponential), never constant hammering.",
            "In TestNG this is IRetryAnalyzer; classify flakiness before retrying.",
        ],
        "followups": [
            "How would you wire this into TestNG (IRetryAnalyzer, maxRetryCount)?",
            "When is a retry masking a real defect, and what do you do about it?",
            "How does Playwright's auto-waiting reduce the need for retries?",
        ],
    },
    {
        "id": "java-testdata-to-map",
        "title": "Parse key=value test data into a Map",
        "category": "Java for Automation",
        "subcategory": "Test data providers",
        "type": "code",
        "difficulty": "medium",
        "problem": (
            "Read one line of the form 'key=value;key2=value2;...' and print every pair as "
            "'key = value' sorted by key, one per line. An empty line prints nothing. "
            "Later duplicates of the same key keep the FIRST value. Values may contain '=' "
            "(split on the first '=' only)."
        ),
        "input_format": "A single line of semicolon-separated pairs.",
        "output_format": "Sorted 'key = value' lines, or nothing for empty input.",
        "constraints": "Ignore empty segments (e.g. trailing ';'). Keys are unique after first-win dedupe.",
        "starter_code": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        String line = sc.hasNextLine() ? sc.nextLine() : \"\";\n"
            "        // TODO: parse into a Map, first value wins, print sorted by key\n"
            "    }\n"
            "}\n"
        ),
        "tests": [
            {"name": "basic", "stdin": "role=EMPLOYEE;dept=Risk;env=UAT\n", "expected": "dept = Risk\nenv = UAT\nrole = EMPLOYEE"},
            {"name": "value with equals", "stdin": "query=a=b;simple=x\n", "expected": "query = a=b\nsimple = x"},
            {"name": "duplicate keys keep first", "stdin": "a=1;a=2;b=3\n", "expected": "a = 1\nb = 3"},
            {"name": "empty", "stdin": "\n", "expected": ""},
        ],
        "solution": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        String line = sc.hasNextLine() ? sc.nextLine() : \"\";\n\n"
            "        Map<String, String> data = new TreeMap<>();   // sorted by key automatically\n"
            "        if (!line.isBlank()) {\n"
            "            for (String pair : line.split(\";\")) {\n"
            "                if (pair.isBlank()) continue;\n"
            "                int eq = pair.indexOf('=');             // split on FIRST '=' only\n"
            "                if (eq <= 0) continue;\n"
            "                String key = pair.substring(0, eq);\n"
            "                String value = pair.substring(eq + 1);\n"
            "                data.putIfAbsent(key, value);          // first value wins\n"
            "            }\n"
            "        }\n"
            "        for (Map.Entry<String, String> e : data.entrySet()) {\n"
            "            System.out.println(e.getKey() + \" = \" + e.getValue());\n"
            "        }\n"
            "    }\n"
            "}\n"
        ),
        "explanation": (
            "indexOf('=') splits on the first equals so values may contain '='; split(\"=\", 2) does "
            "the same. putIfAbsent implements first-value-wins. TreeMap gives sorted output for free. "
            "This is literally how properties files, .env files and CI variables are parsed — say "
            "that connection out loud, it turns a toy exercise into a framework story."
        ),
        "time_complexity": "O(n log k) for the TreeMap inserts",
        "space_complexity": "O(k)",
        "hints": [
            "indexOf('=') (or split with limit 2) handles values containing '='.",
            "putIfAbsent makes the first duplicate win.",
            "TreeMap sorts keys automatically.",
        ],
        "followups": [
            "How would you load the same data from a .properties file? (Properties.load)",
            "How do you manage secrets so they never appear in test data files?",
            "How would you type-convert values (int/boolean) safely?",
        ],
    },
    {
        "id": "java-test-result-summary",
        "title": "Summarise test results from a log",
        "category": "Java for Automation",
        "subcategory": "Create reusable methods",
        "type": "code",
        "difficulty": "medium",
        "problem": (
            "Read lines until EOF. Each line is either 'PASS <testname>' or 'FAIL <testname>'. "
            "Print a summary: 'total: X', 'passed: Y', 'failed: Z', then each failed test name "
            "in input order prefixed 'FAILED: '. If nothing failed, still print the totals only. "
            "Empty input prints total: 0, passed: 0, failed: 0."
        ),
        "input_format": "Lines of 'PASS name' or 'FAIL name' until EOF.",
        "output_format": "Summary lines then failed test names.",
        "constraints": "A test name may appear twice; count every occurrence.",
        "starter_code": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        // TODO: tally PASS/FAIL and print a summary\n"
            "    }\n"
            "}\n"
        ),
        "tests": [
            {
                "name": "mixed results",
                "stdin": "PASS loginTest\nFAIL dashboardTest\nPASS searchTest\nFAIL flakyChart\n",
                "expected": "total: 4\npassed: 2\nfailed: 2\nFAILED: dashboardTest\nFAILED: flakyChart",
            },
            {"name": "all pass", "stdin": "PASS a\nPASS b\n", "expected": "total: 2\npassed: 2\nfailed: 0"},
            {"name": "empty", "stdin": "", "expected": "total: 0\npassed: 0\nfailed: 0"},
        ],
        "solution": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        int total = 0, passed = 0, failed = 0;\n"
            "        List<String> failedNames = new ArrayList<>();   // input order preserved\n"
            "        while (sc.hasNextLine()) {\n"
            "            String line = sc.nextLine().trim();\n"
            "            if (line.isEmpty()) continue;\n"
            "            int space = line.indexOf(' ');\n"
            "            String status = line.substring(0, space);\n"
            "            String name = line.substring(space + 1);\n"
            "            total++;\n"
            "            if (status.equals(\"PASS\")) passed++;\n"
            "            else { failed++; failedNames.add(name); }\n"
            "        }\n"
            "        System.out.println(\"total: \" + total);\n"
            "        System.out.println(\"passed: \" + passed);\n"
            "        System.out.println(\"failed: \" + failed);\n"
            "        for (String name : failedNames) System.out.println(\"FAILED: \" + name);\n"
            "    }\n"
            "}\n"
        ),
        "explanation": (
            "This is a CI health-check in miniature: totals, a pass ratio you can trend across runs, "
            "and the failure list in first-seen order for triage. Interviewers extend it with: "
            "compute the pass percentage as a double, group failures by first word (suite), or flag "
            "tests that fail intermittently across runs — the flakiness detector is the one that "
            "impresses."
        ),
        "time_complexity": "O(n)",
        "space_complexity": "O(n)",
        "hints": [
            "Keep counters plus a List for failed names (order matters for triage).",
            "Compute the pass rate as a double to avoid integer division truncation.",
            "Follow-up: how would you detect a test that flips between PASS/FAIL across runs?",
        ],
        "followups": [
            "How would you compute pass percentage without integer-division bugs?",
            "How would you detect flaky tests across multiple runs of this summary?",
            "How would you push this summary into a CI pipeline report?",
        ],
    },
]
