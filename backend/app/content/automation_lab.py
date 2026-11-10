"""Automation testing lab: Selenium, Playwright, REST Assured exercises + framework architecture Q&A."""
from __future__ import annotations

EXERCISES = [
    # ---------------- Selenium ----------------
    {
        "id": "auto-selenium-login",
        "title": "Selenium: launch Chrome and log in",
        "tool": "Selenium",
        "difficulty": "easy",
        "exercise": (
            "Write a Selenium snippet that launches Chrome, navigates to a login page, fills "
            "username and password, clicks submit and asserts the landing page loaded. "
            "Include browser options you would use in CI (headless, window size)."
        ),
        "starter_code": (
            "import java.time.Duration;\n"
            "import org.openqa.selenium.*;\n"
            "import org.openqa.selenium.chrome.*;\n"
            "import org.openqa.selenium.support.ui.*;\n"
            "import static org.testng.Assert.*;\n\n"
            "public class LoginFlow {\n"
            "    public static void main(String[] args) {\n"
            "        // TODO: launch Chrome headless, login, assert\n"
            "    }\n"
            "}\n"
        ),
        "solution": (
            "import java.time.Duration;\n"
            "import org.openqa.selenium.*;\n"
            "import org.openqa.selenium.chrome.*;\n"
            "import org.openqa.selenium.support.ui.*;\n"
            "import static org.testng.Assert.*;\n\n"
            "public class LoginFlow {\n"
            "    public static void main(String[] args) {\n"
            "        ChromeOptions options = new ChromeOptions();\n"
            "        options.addArguments(\"--headless=new\", \"--window-size=1920,1080\");\n"
            "        WebDriver driver = new ChromeDriver(options);\n"
            "        try {\n"
            "            driver.get(\"https://iam.example.com/login\");\n"
            "            driver.findElement(By.id(\"username\")).sendKeys(\"daya\");\n"
            "            driver.findElement(By.id(\"password\")).sendKeys(\"<secret>\");\n"
            "            new WebDriverWait(driver, Duration.ofSeconds(10))\n"
            "                .until(ExpectedConditions.elementToBeClickable(By.id(\"loginButton\")))\n"
            "                .click();\n"
            "            new WebDriverWait(driver, Duration.ofSeconds(10))\n"
            "                .until(ExpectedConditions.urlContains(\"/dashboard\"));\n"
            "            assertEquals(driver.getTitle(), \"Dashboard\");\n"
            "        } finally {\n"
            "            driver.quit();   // quit() not close(): releases the driver too\n"
            "        }\n"
            "    }\n"
            "}\n"
        ),
        "explanation": (
            "CI options (headless, fixed window size) make runs deterministic and screenless. "
            "Explicit waits around every dynamic element. quit() in finally guarantees the browser "
            "process dies even on assertion failure — leaking chrome drivers is how CI nodes "
            "grind to a halt."
        ),
        "followups": [
            "Why quit() instead of close()?",
            "How would you make credentials never appear in code?",
            "How would this look as a TestNG test with a listener for screenshots?",
        ],
    },
    {
        "id": "auto-selenium-dynamic-elements",
        "title": "Selenium: handle dynamic elements",
        "tool": "Selenium",
        "difficulty": "medium",
        "exercise": (
            "A results table renders rows asynchronously after a search. Write code that waits "
            "for the row belonging to a specific request ID to appear and clicks its Approve "
            "button. Show both a wait-condition approach and a locator approach."
        ),
        "starter_code": (
            "import java.time.Duration;\n"
            "import org.openqa.selenium.*;\n"
            "import org.openqa.selenium.support.ui.*;\n\n"
            "public class DynamicTable {\n"
            "    void approveRequest(WebDriver driver, String requestId) {\n"
            "        // TODO: wait for the row and click Approve\n"
            "    }\n"
            "}\n"
        ),
        "solution": (
            "import java.time.Duration;\n"
            "import org.openqa.selenium.*;\n"
            "import org.openqa.selenium.support.ui.*;\n\n"
            "public class DynamicTable {\n"
            "    void approveRequest(WebDriver driver, String requestId) {\n"
            "        By row = By.xpath(\"//tr[td[text()='\" + requestId + \"']]\");\n"
            "        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(15));\n\n"
            "        // Approach 1: wait for the row itself, then scope the button to the row\n"
            "        WebElement rowEl = wait.until(ExpectedConditions.presenceOfElementLocated(row));\n"
            "        rowEl.findElement(By.cssSelector(\"button.approve\")).click();\n\n"
            "        // Approach 2 (stronger): wait directly for the clickable button inside that row\n"
            "        // wait.until(ExpectedConditions.elementToBeClickable(\n"
            "        //     By.xpath(\"//tr[td[text()='\" + requestId + \"']]//button[@class='approve']\"))).click();\n"
            "    }\n"
            "}\n"
        ),
        "explanation": (
            "Dynamic content needs condition-based waits scoped to the specific element — waiting "
            "for 'a table to exist' is not waiting for 'my row to exist'. Scoping the button "
            "search to the located row element (Approach 1) or expressing both in one XPath "
            "(Approach 2) avoids clicking another row's Approve button, which is a real defect "
            "in flaky suites. In interviews, always mention asking developers for stable "
            "data-* attributes instead of text-matching XPath."
        ),
        "followups": [
            "What if the request ID appears in multiple rows?",
            "Why is presenceOfElementLocated sometimes insufficient here?",
            "What data-testid contract would you propose to the dev team?",
        ],
    },
    {
        "id": "auto-selenium-windows-alerts",
        "title": "Selenium: multiple windows, alerts and frames",
        "tool": "Selenium",
        "difficulty": "medium",
        "exercise": (
            "Write snippets for: (a) switching to a popup window, acting, and returning; "
            "(b) accepting and dismissing JS alerts; (c) working inside an iframe."
        ),
        "starter_code": (
            "import org.openqa.selenium.*;\n\n"
            "public class WindowAlertFrame {\n"
            "    void popup(WebDriver driver) {\n"
            "        // TODO\n"
            "    }\n"
            "    void alert(WebDriver driver) {\n"
            "        // TODO\n"
            "    }\n"
            "    void frame(WebDriver driver) {\n"
            "        // TODO\n"
            "    }\n"
            "}\n"
        ),
        "solution": (
            "import org.openqa.selenium.*;\n"
            "import java.util.Set;\n\n"
            "public class WindowAlertFrame {\n"
            "    void popup(WebDriver driver) {\n"
            "        String main = driver.getWindowHandle();\n"
            "        driver.findElement(By.id(\"openReport\")).click();\n"
            "        Set<String> handles = driver.getWindowHandles();\n"
            "        for (String h : handles) {\n"
            "            if (!h.equals(main)) { driver.switchTo().window(h); break; }\n"
            "        }\n"
            "        driver.findElement(By.id(\"download\")).click();\n"
            "        driver.close();                    // close the popup only\n"
            "        driver.switchTo().window(main);     // back to the main window\n"
            "    }\n\n"
            "    void alert(WebDriver driver) {\n"
            "        Alert a = driver.switchTo().alert();   // synchronous: waits for the alert\n"
            "        String text = a.getText();\n"
            "        a.accept();       // or a.dismiss();\n"
            "    }\n\n"
            "    void frame(WebDriver driver) {\n"
            "        driver.switchTo().frame(\"reportFrame\");   // by name/id/index/WebElement\n"
            "        driver.findElement(By.id(\"innerButton\")).click();\n"
            "        driver.switchTo().defaultContent();       // leave the frame\n"
            "    }\n"
            "}\n"
        ),
        "explanation": (
            "Window handles: getWindowHandles returns a Set; switch by handle, never by index. "
            "close() kills the current window while quit() kills the whole session. Alerts need "
            "switchTo().alert() — findElement will not see them. Frames isolate the DOM: you must "
            "switch in and out, and forgetting defaultContent() is a classic reason 'element not "
            "found' errors appear after frame work."
        ),
        "followups": [
            "How do you wait for a new window to open (WebDriverWait with numberOfWindowsToBe)?",
            "Why does NoSuchFrameException happen intermittently?",
            "How does Playwright handle multiple tabs differently?",
        ],
    },
    {
        "id": "auto-selenium-screenshot",
        "title": "Selenium: capture screenshots on failure",
        "tool": "Selenium",
        "difficulty": "medium",
        "exercise": (
            "Implement an ITestListener that captures a screenshot, the current URL and the page "
            "title whenever a test fails, and saves them with a deterministic file name."
        ),
        "starter_code": (
            "import org.openqa.selenium.*;\n"
            "import org.testng.*;\n"
            "import java.nio.file.*;\n\n"
            "public class EvidenceListener implements ITestListener {\n"
            "    // TODO: onTestFailure -> screenshot + URL + title\n"
            "}\n"
        ),
        "solution": (
            "import org.openqa.selenium.*;\n"
            "import org.testng.*;\n"
            "import java.nio.file.*;\n"
            "import java.time.LocalDateTime;\n\n"
            "public class EvidenceListener implements ITestListener {\n\n"
            "    @Override\n"
            "    public void onTestFailure(ITestResult result) {\n"
            "        WebDriver driver = DriverManager.get();          // ThreadLocal driver for parallel runs\n"
            "        String name = result.getMethod().getMethodName();\n"
            "        String stamp = LocalDateTime.now().toString().replace(\":\", \"-\");\n"
            "        Path dir = Paths.get(\"target\", \"evidence\", name);\n"
            "        try {\n"
            "            Files.createDirectories(dir);\n"
            "            TakesScreenshot ts = (TakesScreenshot) driver;\n"
            "            Files.write(dir.resolve(stamp + \".png\"),\n"
            "                        ts.getScreenshotAs(OutputType.BYTES));\n"
            "            Files.writeString(dir.resolve(stamp + \".txt\"),\n"
            "                        \"url=\" + driver.getCurrentUrl() +\n"
            "                        \"\\ntitle=\" + driver.getTitle());\n"
            "        } catch (Exception e) {\n"
            "            // evidence capture must never mask the original test failure\n"
            "            System.err.println(\"evidence capture failed: \" + e.getMessage());\n"
            "        }\n"
            "    }\n"
            "}\n"
        ),
        "explanation": (
            "Evidence capture is a first-class feature of a security QA framework — audit and "
            "defect reports need artifacts. Two details interviewers probe: the capture must "
            "never mask the original failure (catch quietly, log), and with parallel runs the "
            "driver must come from a ThreadLocal, not a static single field."
        ),
        "followups": [
            "How do you attach evidence to an Extent/Allure report instead of files?",
            "What happens to screenshots when the driver is already dead?",
            "How would you capture the DOM HTML too?",
        ],
    },
    {
        "id": "auto-selenium-actions-dropdown",
        "title": "Selenium: dropdowns, hover and Actions class",
        "tool": "Selenium",
        "difficulty": "easy",
        "exercise": (
            "Select a value in a standard SELECT dropdown (by visible text), then hover over a "
            "menu to reveal a submenu and click it using the Actions class."
        ),
        "starter_code": (
            "import org.openqa.selenium.*;\n"
            "import org.openqa.selenium.interactions.Actions;\n"
            "import org.openqa.selenium.support.ui.Select;\n\n"
            "public class Interactions {\n"
            "    void dropdown(WebDriver driver) {\n"
            "        // TODO: select 'Risk' by visible text\n"
            "    }\n"
            "    void hoverMenu(WebDriver driver) {\n"
            "        // TODO: hover #governance then click the revealed 'Certifications' link\n"
            "    }\n"
            "}\n"
        ),
        "solution": (
            "import org.openqa.selenium.*;\n"
            "import org.openqa.selenium.interactions.Actions;\n"
            "import org.openqa.selenium.support.ui.Select;\n\n"
            "public class Interactions {\n"
            "    void dropdown(WebDriver driver) {\n"
            "        Select dept = new Select(driver.findElement(By.id(\"department\")));\n"
            "        dept.selectByVisibleText(\"Risk\");\n"
            "        // also: selectByValue(\"RISK\") / selectByIndex(2)\n"
            "    }\n\n"
            "    void hoverMenu(WebDriver driver) {\n"
            "        Actions actions = new Actions(driver);\n"
            "        actions.moveToElement(driver.findElement(By.id(\"governance\")))   // hover\n"
            "              .pause(200)\n"
            "              .click(driver.findElement(By.linkText(\"Certifications\")))\n"
            "              .perform();   // nothing happens until perform()\n"
            "    }\n"
            "}\n"
        ),
        "explanation": (
            "Select only works for real <select> elements — custom div-based dropdowns need "
            "click-then-click sequences. Actions chains do nothing until perform(); moveToElement "
            "plus a short pause covers CSS transition delays. For custom dropdowns in interviews, "
            "describe the robust pattern: click the opener, wait for options, click the option "
            "matched by text."
        ),
        "followups": [
            "How do you handle a custom (non-select) dropdown?",
            "How would you drag and drop with Actions?",
            "Why do Actions sometimes need a pause?",
        ],
    },
    # ---------------- Playwright ----------------
    {
        "id": "auto-playwright-autowait",
        "title": "Playwright: locators and auto-waiting",
        "tool": "Playwright",
        "difficulty": "easy",
        "exercise": (
            "Write a Playwright (Java) snippet that logs in using role-based locators and "
            "asserts the dashboard heading with a web-first assertion. Explain what "
            "auto-waiting replaces compared to Selenium."
        ),
        "starter_code": (
            "import com.microsoft.playwright.*;\n"
            "import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;\n\n"
            "public class LoginFlow {\n"
            "    public static void main(String[] args) {\n"
            "        // TODO: login + assert with auto-waiting\n"
            "    }\n"
            "}\n"
        ),
        "solution": (
            "import com.microsoft.playwright.*;\n"
            "import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;\n\n"
            "public class LoginFlow {\n"
            "    public static void main(String[] args) {\n"
            "        try (Playwright pw = Playwright.create()) {\n"
            "            Browser browser = pw.chromium().launch();\n"
            "            Page page = browser.newPage();\n"
            "            page.navigate(\"https://iam.example.com/login\");\n"
            "            page.getByLabel(\"Username\").fill(\"daya\");\n"
            "            page.getByLabel(\"Password\").fill(\"<secret>\");\n"
            "            page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName(\"Sign in\")).click();\n"
            "            assertThat(page.getByRole(AriaRole.HEADING, new Page.GetByRoleOptions().setName(\"Dashboard\")))\n"
            "                .isVisible();\n"
            "        }\n"
            "    }\n"
            "}\n"
        ),
        "explanation": (
            "getByRole/getByLabel mirror how users and screen readers perceive the page — more "
            "resilient than CSS selectors tied to markup. Auto-waiting means fill() waits for the "
            "element to be visible, enabled and stable, and click() additionally waits for "
            "actionability — replacing the explicit-wait code that dominates Selenium suites. "
            "Web-first assertions (assertThat) retry until the condition holds."
        ),
        "followups": [
            "What does actionability mean in Playwright terms?",
            "When would you still need an explicit waitFor in Playwright?",
            "How do role-based locators improve accessibility testing?",
        ],
    },
    {
        "id": "auto-playwright-contexts",
        "title": "Playwright: browser contexts and multi-user tests",
        "tool": "Playwright",
        "difficulty": "medium",
        "exercise": (
            "Write a snippet that opens two browser contexts — an employee and an admin — and "
            "verifies the employee cannot see the admin menu while the admin can. Explain why "
            "contexts are better than separate browsers for this."
        ),
        "starter_code": (
            "import com.microsoft.playwright.*;\n\n"
            "public class MultiUserCheck {\n"
            "    public static void main(String[] args) {\n"
            "        // TODO: two contexts, one check\n"
            "    }\n"
            "}\n"
        ),
        "solution": (
            "import com.microsoft.playwright.*;\n"
            "import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;\n\n"
            "public class MultiUserCheck {\n"
            "    public static void main(String[] args) {\n"
            "        try (Playwright pw = Playwright.create()) {\n"
            "            Browser browser = pw.chromium().launch();\n"
            "\n"
            "            BrowserContext employeeCtx = browser.newContext();\n"
            "            BrowserContext adminCtx = browser.newContext();\n"
            "\n"
            "            Page employee = employeeCtx.newPage();\n"
            "            Page admin = adminCtx.newPage();\n"
            "\n"
            "            Auth.loginAs(employee, \"daya\", \"EMPLOYEE\");\n"
            "            Auth.loginAs(admin, \"priya\", \"ADMIN\");\n"
            "\n"
            "            assertThat(employee.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName(\"Admin Console\")))\n"
            "                .isHidden();          // employee must NOT see admin UI\n"
            "            assertThat(admin.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName(\"Admin Console\")))\n"
            "                .isVisible();      // admin must see it\n"
            "\n"
            "            employeeCtx.close();\n"
            "            adminCtx.close();\n"
            "        }\n"
            "    }\n"
            "}\n"
        ),
        "explanation": (
            "Each context is an isolated session: cookies, storage, cache — separate users in one "
            "browser process at a fraction of the cost of two browsers. This is exactly the shape "
            "of authorization testing: two identities interacting with the same page at once, "
            "asserting different visibility. Note the deeper check: UI hiding is never enough; "
            "the same test should also call the admin API with the employee context's token and "
            "assert 403."
        ),
        "followups": [
            "How do you extract and reuse a context's cookies (storageState)?",
            "How would you run 50 contexts in parallel?",
            "Why is isHidden on a non-existent element fine in Playwright?",
        ],
    },
    {
        "id": "auto-playwright-network",
        "title": "Playwright: network interception",
        "tool": "Playwright",
        "difficulty": "medium",
        "exercise": (
            "Write a Playwright snippet that intercepts the entitlement API call and mocks a "
            "response with two entitlements, then asserts the UI renders both. Explain why "
            "network mocking matters in security QA."
        ),
        "starter_code": (
            "import com.microsoft.playwright.*;\n\n"
            "public class MockEntitlements {\n"
            "    public static void main(String[] args) {\n"
            "        // TODO: route + fulfil + assert\n"
            "    }\n"
            "}\n"
        ),
        "solution": (
            "import com.microsoft.playwright.*;\n"
            "import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;\n\n"
            "public class MockEntitlements {\n"
            "    public static void main(String[] args) {\n"
            "        try (Playwright pw = Playwright.create()) {\n"
            "            Browser browser = pw.chromium().launch();\n"
            "            Page page = browser.newPage();\n\n"
            "            page.route(\"**/api/entitlements\", route -> route.fulfill(new Route.FulfillOptions()\n"
            "                .setStatus(200)\n"
            "                .setContentType(\"application/json\")\n"
            "                .setBody(\"[{\\\\\\\"role\\\\\\\":\\\\\\\"EMPLOYEE\\\\\\\"},{\\\\\\\"role\\\\\\\":\\\\\\\"AUDITOR\\\\\\\"}]\")));\n"
            "\n"
            "            page.navigate(\"https://iam.example.com/profile\");\n"
            "            assertThat(page.getByText(\"EMPLOYEE\")).isVisible();\n"
            "            assertThat(page.getByText(\"AUDITOR\")).isVisible();\n"
            "        }\n"
            "    }\n"
            "}\n"
        ),
        "explanation": (
            "page.route() intercepts requests before they leave the browser: fulfil with mocks, "
            "abort to simulate failures, or continue with modifications. For security QA this is "
            "how you test frontend trust boundaries deterministically: feed the UI a role it "
            "should not display, simulate API 500s, or verify the UI does not expose data the "
            "API omits. The mock is stable, so the UI test stops depending on backend state."
        ),
        "followups": [
            "How would you simulate an API 500 or a slow response?",
            "How do you assert on real requests the page made (page.onRequest)?",
            "When is mocking inappropriate in an end-to-end suite?",
        ],
    },
    {
        "id": "auto-playwright-auth-state",
        "title": "Playwright: reuse authentication state",
        "tool": "Playwright",
        "difficulty": "medium",
        "exercise": (
            "Log in once, save the authenticated state to storageState, and create two new "
            "contexts that start already authenticated. Explain the performance impact in CI."
        ),
        "starter_code": (
            "import com.microsoft.playwright.*;\n\n"
            "public class AuthState {\n"
            "    public static void main(String[] args) {\n"
            "        // TODO: login once, save state, reuse\n"
            "    }\n"
            "}\n"
        ),
        "solution": (
            "import com.microsoft.playwright.*;\n"
            "import java.nio.file.Paths;\n\n"
            "public class AuthState {\n"
            "    public static void main(String[] args) {\n"
            "        try (Playwright pw = Playwright.create()) {\n"
            "            Browser browser = pw.chromium().launch();\n"
            "\n"
            "            // 1. log in once\n"
            "            BrowserContext loginCtx = browser.newContext();\n"
            "            Page page = loginCtx.newPage();\n"
            "            Auth.loginAs(page, \"daya\", \"<secret>\");\n"
            "\n"
            "            // 2. persist the session\n"
            "            loginCtx.storageState(new BrowserContext.StorageStateOptions()\n"
            "                .setPath(Paths.get(\"auth/daya.json\")));\n"
            "            loginCtx.close();\n"
            "\n"
            "            // 3. parallel contexts start authenticated — no second login\n"
            "            BrowserContext ctxA = browser.newContext(new Browser.NewContextOptions()\n"
            "                .setStorageStatePath(Paths.get(\"auth/daya.json\")));\n"
            "            BrowserContext ctxB = browser.newContext(new Browser.NewContextOptions()\n"
            "                .setStorageStatePath(Paths.get(\"auth/daya.json\")));\n"
            "        }\n"
            "    }\n"
            "}\n"
        ),
        "explanation": (
            "storageState captures cookies and localStorage as a file; new contexts load it and "
            "start authenticated. One login per suite instead of one per test removes the "
            "slowest, flakiest step from every test — a major driver of the 60-to-40-minute "
            "regression reduction in migration stories. Caveat: state expires, so CI should "
            "re-create it per run, and per-role state files (employee.json, admin.json) "
            "map neatly to authorization matrices."
        ),
        "followups": [
            "How does this interact with short session lifetimes?",
            "How would you generate per-role state files in a suite setup?",
            "What Playwright artifact would you inspect when a reused-state test fails?",
        ],
    },
    # ---------------- REST Assured ----------------
    {
        "id": "auto-rest-crud",
        "title": "REST Assured: CRUD on an entitlement resource",
        "tool": "REST Assured",
        "difficulty": "medium",
        "exercise": (
            "Write REST Assured calls for GET (list), POST (create), PUT (update), PATCH "
            "(partial update) and DELETE of an entitlement resource, with status code and body "
            "assertions for each."
        ),
        "starter_code": (
            "import static io.restassured.RestAssured.*;\n"
            "import static org.hamcrest.Matchers.*;\n\n"
            "public class EntitlementCrud {\n"
            "    void crud() {\n"
            "        // TODO: GET, POST, PUT, PATCH, DELETE\n"
            "    }\n"
            "}\n"
        ),
        "solution": (
            "import static io.restassured.RestAssured.*;\n"
            "import static org.hamcrest.Matchers.*;\n\n"
            "public class EntitlementCrud {\n"
            "    void crud() {\n"
            "        baseURI = \"https://iam.example.com\";\n"
            "\n"
            "        // CREATE\n"
            "        String id =\n"
            "            given().contentType(\"application/json\")\n"
            "                   .body(\"{\\\"name\\\":\\\"CIAM_SUPPORT\\\",\\\"risk\\\":\\\"HIGH\\\"}\")\n"
            "            .when().post(\"/api/entitlements\")\n"
            "            .then().statusCode(201)\n"
            "                   .body(\"name\", equalTo(\"CIAM_SUPPORT\"))\n"
            "                   .extract().path(\"id\");\n"
            "\n"
            "        // READ (list + single)\n"
            "        when().get(\"/api/entitlements\")\n"
            "            .then().statusCode(200).body(\"size()\", greaterThan(0));\n"
            "        given().pathParam(\"id\", id)\n"
            "            .when().get(\"/api/entitlements/{id}\")\n"
            "            .then().statusCode(200).body(\"risk\", equalTo(\"HIGH\"));\n"
            "\n"
            "        // UPDATE (full replace)\n"
            "        given().contentType(\"application/json\")\n"
            "               .body(\"{\\\"name\\\":\\\"CIAM_SUPPORT\\\",\\\"risk\\\":\\\"CRITICAL\\\"}\")\n"
            "            .when().put(\"/api/entitlements/\" + id)\n"
            "            .then().statusCode(200).body(\"risk\", equalTo(\"CRITICAL\"));\n"
            "\n"
            "        // PARTIAL UPDATE\n"
            "        given().contentType(\"application/json\")\n"
            "               .body(\"{\\\"risk\\\":\\\"MEDIUM\\\"}\")\n"
            "            .when().patch(\"/api/entitlements/\" + id)\n"
            "            .then().statusCode(200).body(\"risk\", equalTo(\"MEDIUM\"));\n"
            "\n"
            "        // DELETE + verify gone (404, not 200)\n"
            "        when().delete(\"/api/entitlements/\" + id)\n"
            "            .then().statusCode(204);\n"
            "        when().get(\"/api/entitlements/\" + id)\n"
            "            .then().statusCode(404);\n"
            "    }\n"
            "}\n"
        ),
        "explanation": (
            "Each verb has a contract: 201 + body on create, 200 on read/update, 204 on delete, "
            "and 404 after deletion — asserting the delete actually removed the resource is the "
            "step juniors skip. PUT is full replacement; PATCH is partial. Extracting the id "
            "enables chaining. In IAM terms, this is the entitlement lifecycle, and the security "
            "follow-up is testing all of it again with an unauthorized token expecting 403."
        ),
        "followups": [
            "Why assert 404 after DELETE?",
            "How do you test the same CRUD with an employee token?",
            "How would you validate the JSON schema on each response?",
        ],
    },
    {
        "id": "auto-rest-authz",
        "title": "REST Assured: authentication vs authorization matrix",
        "tool": "REST Assured",
        "difficulty": "hard",
        "exercise": (
            "Build an authorization matrix test: the same endpoint called with (a) no token, "
            "(b) an expired token, (c) an employee token, (d) an admin token. Assert the exact "
            "status codes and that error bodies leak no sensitive detail."
        ),
        "starter_code": (
            "import static io.restassured.RestAssured.*;\n"
            "import static org.hamcrest.Matchers.*;\n\n"
            "public class AuthzMatrix {\n"
            "    void matrix() {\n"
            "        // TODO: four cases, four precise assertions\n"
            "    }\n"
            "}\n"
        ),
        "solution": (
            "import static io.restassured.RestAssured.*;\n"
            "import static org.hamcrest.Matchers.*;\n\n"
            "public class AuthzMatrix {\n"
            "    void matrix() {\n"
            "        baseURI = \"https://iam.example.com\";\n"
            "\n"
            "        // (a) no credentials -> 401\n"
            "        when().get(\"/api/admin/users\")\n"
            "            .then().statusCode(401);\n"
            "\n"
            "        // (b) expired token -> 401 (authentication failed, not 403)\n"
            "        given().header(\"Authorization\", \"Bearer \" + Tokens.expired())\n"
            "            .when().get(\"/api/admin/users\")\n"
            "            .then().statusCode(401)\n"
            "                   .body(\"error\", containsString(\"token_expired\"));\n"
            "\n"
            "        // (c) authenticated employee -> 403 (authorization failed)\n"
            "        given().header(\"Authorization\", \"Bearer \" + Tokens.employee())\n"
            "            .when().get(\"/api/admin/users\")\n"
            "            .then().statusCode(403)\n"
            "                   .body(\"size()\", equalTo(0));       // no data leak\n"
            "\n"
            "        // (d) admin -> 200 with data\n"
            "        given().header(\"Authorization\", \"Bearer \" + Tokens.admin())\n"
            "            .when().get(\"/api/admin/users\")\n"
            "            .then().statusCode(200)\n"
            "                   .body(\"size()\", greaterThan(0));\n"
            "    }\n"
            "}\n"
        ),
        "explanation": (
            "This is THE security QA pattern: an authorization matrix executed as an API suite. "
            "The 401/403 distinction is the grammar: 401 means 'I do not know who you are' "
            "(missing/expired/invalid credentials), 403 means 'I know you and you may not'. "
            "Just as important: error bodies must not leak stack traces, user lists or internal "
            "details — denied responses are asserted to be empty and non-committal."
        ),
        "followups": [
            "How would you scale this to a role x endpoint matrix from a data file?",
            "What response body details would you check for information leakage?",
            "How do you keep tokens fresh in CI?",
        ],
    },
    {
        "id": "auto-rest-chaining-db",
        "title": "REST Assured: API chaining + database verification",
        "tool": "REST Assured",
        "difficulty": "hard",
        "exercise": (
            "Write a test that creates an access request via API, extracts the request id, "
            "approves it via API, then verifies via JDBC that the entitlement row exists in the "
            "database with the right status — the full cross-layer validation."
        ),
        "starter_code": (
            "import static io.restassured.RestAssured.*;\n"
            "import static org.hamcrest.Matchers.*;\n"
            "import java.sql.*;\n\n"
            "public class RequestApprovalFlow {\n"
            "    void flow() throws Exception {\n"
            "        // TODO: create -> approve -> JDBC verify\n"
            "    }\n"
            "}\n"
        ),
        "solution": (
            "import static io.restassured.RestAssured.*;\n"
            "import static org.hamcrest.Matchers.*;\n"
            "import java.sql.*;\n\n"
            "public class RequestApprovalFlow {\n"
            "    void flow() throws Exception {\n"
            "        baseURI = \"https://iam.example.com\";\n"
            "\n"
            "        // 1. create the request as the employee\n"
            "        int requestId =\n"
            "            given().header(\"Authorization\", \"Bearer \" + Tokens.employee())\n"
            "                   .contentType(\"application/json\")\n"
            "                   .body(\"{\\\"entitlement\\\":\\\"CIAM_SUPPORT\\\"}\")\n"
            "            .when().post(\"/api/requests\")\n"
            "            .then().statusCode(201)\n"
            "                   .body(\"status\", equalTo(\"PENDING\"))\n"
            "                   .extract().path(\"id\");\n"
            "\n"
            "        // 2. approve as the manager\n"
            "        given().header(\"Authorization\", \"Bearer \" + Tokens.manager())\n"
            "               .pathParam(\"id\", requestId)\n"
            "            .when().post(\"/api/requests/{id}/approve\")\n"
            "            .then().statusCode(200)\n"
            "                   .body(\"status\", equalTo(\"APPROVED\"));\n"
            "\n"
            "        // 3. verify the database agrees with the API\n"
            "        try (Connection con = DriverManager.getConnection(dbUrl, dbUser, dbPass);\n"
            "             PreparedStatement ps = con.prepareStatement(\n"
            "                 \"SELECT status, approver_id FROM access_requests WHERE request_id = ?\")) {\n"
            "            ps.setInt(1, requestId);\n"
            "            ResultSet rs = ps.executeQuery();\n"
            "            assertTrue(rs.next(), \"request row missing in DB\");\n"
            "            assertEquals(rs.getString(\"status\"), \"APPROVED\");\n"
            "        }\n"
            "    }\n"
            "}\n"
        ),
        "explanation": (
            "Three-layer validation in one test: API contract (201/200 + status values), "
            "workflow semantics (approval by the right principal), and persistence (the database "
            "row matches). The API saying APPROVED while the row says PENDING is exactly the "
            "defect class this catches. PreparedStatements prevent SQL injection in test code "
            "too — interviews notice that detail."
        ),
        "followups": [
            "What if the API reads through a cache and the DB is ahead?",
            "How would you assert audit log rows as well?",
            "How do you clean up the created data afterwards?",
        ],
    },
]


FRAMEWORK_ARCHITECTURE_QA = [
    {
        "id": "arch-explain-layers",
        "question": "Explain your automation framework architecture.",
        "model_answer": (
            "Layered: test layer (TestNG/Cucumber specs, no locators) -> business layer "
            "(page objects for UI, service clients for API, same operation shape so a flow can "
            "be driven either way) -> utilities (wait wrappers, evidence-capturing assertions, "
            "test-data builders, config reader) -> config layer (environment URLs, credentials "
            "from a secret store) -> execution layer (Maven, parallel TestNG, CI pipelines, "
            "Docker runners) -> reporting layer (test results plus screenshots, request/response "
            "logs, traces on failure). Tests are data-isolated and self-cleaning so parallel "
            "runs never interfere. The design goal throughout: a failure must be diagnosable "
            "from the report alone."
        ),
    },
    {
        "id": "arch-why-pom",
        "question": "Why did you choose the Page Object Model?",
        "model_answer": (
            "POM puts locators and interactions in one class per page so a UI change is fixed "
            "in exactly one place instead of across hundreds of scripts. It gives a vocabulary "
            "that matches the product ('loginPage.login(user)') so tests read like behaviour, "
            "not like DOM trivia. The discipline that makes it work: no assertions inside page "
            "methods, no test data inside pages, and methods return the next page for fluent "
            "navigation. For API testing the same shape applies — service classes per resource "
            "instead of pages."
        ),
    },
    {
        "id": "arch-avoid-duplication",
        "question": "How do you avoid code duplication across tests?",
        "model_answer": (
            "Through the business layer: any sequence used twice becomes a method on a page or "
            "service client ('submitAccessRequest(role)'); repeated assertions become "
            "assertion helpers with built-in evidence capture; repeated data setups become "
            "builders ('UserBuilder.withRole(RISK).create()'). Composition beats inheritance "
            "for reuse here. The smell that tells me duplication is winning: tests that copy a "
            "10-line setup block. The rule: three strikes and it moves into the framework."
        ),
    },
    {
        "id": "arch-test-data",
        "question": "How do you manage test data?",
        "model_answer": (
            "Each test creates the data it needs through builders or setup APIs — never shared "
            "pre-seeded rows — and cleans up afterwards (teardown or soft-expiry timestamps). "
            "Static reference data (roles, applications) is versioned in the repo and seeded "
            "per environment. Credentials come from a secret store, never from files in the "
            "repo. For identity data specifically, I use clearly-marked test identifiers "
            "(TESTAUTO- prefix) so production reports can filter automation noise — which is a "
            "real problem in IAM platforms where test identities pollute governance dashboards."
        ),
    },
    {
        "id": "arch-parallel",
        "question": "How do you execute tests in parallel and prevent interference?",
        "model_answer": (
            "TestNG parallel=methods with a thread pool, drivers in ThreadLocal, and — after "
            "the Playwright migration — browser contexts as the cheap isolation unit. "
            "Interference prevention is about state: per-test data creation, no ordering "
            "dependencies, no shared mutable fixtures, and a single-writer rule for shared "
            "resources. Flaky parallel failures almost always mean hidden shared state — "
            "finding them is a data-isolation exercise, not a wait-tuning one."
        ),
    },
    {
        "id": "arch-secrets",
        "question": "How do you manage secrets and credentials?",
        "model_answer": (
            "Credentials live in a secret store (vault or CI secret variables) and reach tests "
            "as environment variables at runtime — never in source files, never in reports, "
            "masked in logs. Test users are purpose-built identities with least privilege, "
            "not reused personal accounts. Rotating a credential should not require a code "
            "change, and expired-credential failures in CI should say so explicitly rather "
            "than surfacing as random 401 flakiness."
        ),
    },
    {
        "id": "arch-app-vs-automation-defect",
        "question": "How do you identify whether a failure is an application defect or an automation defect?",
        "model_answer": (
            "Reproduce outside the test: same call in Postman, same query in SQL, same steps "
            "manually. If the product misbehaves independently of my test, it is a product "
            "defect. If it only misbehaves under the test, I check the test's assumptions: "
            "waits, data state, environment config. Evidence decides: request/response logs, "
            "database state, traces. When triage is ambiguous I classify as automation-suspect "
            "first and keep digging — wrongly blaming the product burns credibility with "
            "developers."
        ),
    },
    {
        "id": "arch-scale-1000",
        "question": "How would you scale your framework to 1,000 tests?",
        "model_answer": (
            "Execution: parallelism via contexts/threads, sharding across CI agents, and suite "
            "tiering (smoke / regression / full) so feedback stays fast. Stability: flake rate "
            "as a tracked metric with quarantine discipline. Maintenance: generated data "
            "builders, shared business-layer methods, and lint rules against locator "
            "duplication. Diagnostics: every failure must carry evidence, because at 1,000 "
            "tests a human re-run to triage is unaffordable. And selection: run subsets by "
            "risk tag (security-critical first) rather than always running everything."
        ),
    },
]


def list_exercises() -> list[dict]:
    return [
        {
            "id": e["id"],
            "title": e["title"],
            "tool": e["tool"],
            "difficulty": e["difficulty"],
            "exercise": e["exercise"],
        }
        for e in EXERCISES
    ]


def get_exercise(exercise_id: str) -> dict | None:
    for e in EXERCISES:
        if e["id"] == exercise_id:
            return e
    return None


def list_architecture_qa() -> list[dict]:
    return FRAMEWORK_ARCHITECTURE_QA
