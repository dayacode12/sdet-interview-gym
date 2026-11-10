"""Java coding questions, core part B (comparators, collections, algorithmics)."""
from __future__ import annotations

JAVA_CORE_PART_B = [
    {
        "id": "java-sort-employees",
        "title": "Sort employees by salary using Comparator",
        "category": "Core Java",
        "subcategory": "Comparator",
        "type": "code",
        "difficulty": "medium",
        "problem": (
            "Read n and then n lines of 'name salary'. Print the employees sorted by salary "
            "descending; employees with equal salary must be printed in ascending name order. "
            "Output one employee per line as 'name salary'."
        ),
        "input_format": "Line 1: n. Then n lines: 'name salary'.",
        "output_format": "n lines sorted by salary desc, name asc: 'name salary'.",
        "constraints": "1 <= n <= 1000. Salary is a non-negative integer.",
        "starter_code": (
            "import java.util.*;\n\n"
            "class Employee {\n"
            "    String name;\n"
            "    int salary;\n"
            "    Employee(String name, int salary) { this.name = name; this.salary = salary; }\n"
            "}\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        int n = Integer.parseInt(sc.nextLine().trim());\n"
            "        List<Employee> employees = new ArrayList<>();\n"
            "        for (int i = 0; i < n; i++) {\n"
            "            String[] parts = sc.nextLine().trim().split(\"\\\\s+\");\n"
            "            employees.add(new Employee(parts[0], Integer.parseInt(parts[1])));\n"
            "        }\n"
            "        // TODO: sort by salary desc, then name asc\n"
            "        for (Employee e : employees) System.out.println(e.name + \" \" + e.salary);\n"
            "    }\n"
            "}\n"
        ),
        "tests": [
            {"name": "basic sort", "stdin": "4\nDaya 50000\nRavi 80000\nMeera 50000\nAsha 120000\n", "expected": "Asha 120000\nRavi 80000\nDaya 50000\nMeera 50000"},
            {"name": "tie broken by name", "stdin": "3\nZoe 10\nAmy 10\nBen 10\n", "expected": "Amy 10\nBen 10\nZoe 10"},
            {"name": "single employee", "stdin": "1\nSolo 1\n", "expected": "Solo 1"},
        ],
        "solution": (
            "import java.util.*;\n\n"
            "class Employee {\n"
            "    String name;\n"
            "    int salary;\n"
            "    Employee(String name, int salary) { this.name = name; this.salary = salary; }\n"
            "}\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        int n = Integer.parseInt(sc.nextLine().trim());\n"
            "        List<Employee> employees = new ArrayList<>();\n"
            "        for (int i = 0; i < n; i++) {\n"
            "            String[] parts = sc.nextLine().trim().split(\"\\\\s+\");\n"
            "            employees.add(new Employee(parts[0], Integer.parseInt(parts[1])));\n"
            "        }\n"
            "        employees.sort(\n"
            "            Comparator.comparingInt((Employee e) -> e.salary).reversed()\n"
            "                .thenComparing(e -> e.name)\n"
            "        );\n"
            "        for (Employee e : employees) System.out.println(e.name + \" \" + e.salary);\n"
            "    }\n"
            "}\n"
        ),
        "explanation": (
            "Comparator.comparingInt(...).reversed().thenComparing(...) is the modern Java 8+ idiom. "
            "The explicit lambda parameter type in comparingInt((Employee e) -> e.salary) is required "
            "before .reversed() so type inference works. An alternative is implementing "
            "Comparable<Employee> with a compareTo that mirrors the same rule."
        ),
        "time_complexity": "O(n log n)",
        "space_complexity": "O(n)",
        "hints": [
            "Comparator.comparingInt(e -> e.salary).reversed() gives salary descending.",
            "thenComparing(e -> e.name) breaks ties alphabetically.",
            "compareTo returns negative/zero/positive — know which direction sorts ascending.",
        ],
        "followups": [
            "Comparator vs Comparable: when do you choose which?",
            "How would you make Employee immutable and still sort it?",
            "How would you sort a stream and collect the top 3 earners?",
        ],
    },
    {
        "id": "java-remove-duplicates-list",
        "title": "Remove duplicates from an ArrayList preserving order",
        "category": "Core Java",
        "subcategory": "Collections",
        "type": "code",
        "difficulty": "easy",
        "problem": (
            "Read one comma-separated line of values and print them deduplicated, "
            "keeping the first occurrence of each value, joined again by ', '. "
            "Empty input should print an empty line."
        ),
        "input_format": "A single line of comma-separated values (no spaces after commas).",
        "output_format": "Deduplicated values joined with ', ' in original order.",
        "constraints": "0-1000 values. Values are non-empty tokens.",
        "starter_code": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        String line = sc.hasNextLine() ? sc.nextLine() : \"\";\n"
            "        // TODO: remove duplicates preserving first occurrence\n"
            "        System.out.println();\n"
            "    }\n"
            "}\n"
        ),
        "tests": [
            {"name": "basic", "stdin": "apple,banana,apple,cherry,banana\n", "expected": "apple, banana, cherry"},
            {"name": "no duplicates", "stdin": "a,b,c\n", "expected": "a, b, c"},
            {"name": "empty", "stdin": "\n", "expected": ""},
        ],
        "solution": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        String line = sc.hasNextLine() ? sc.nextLine() : \"\";\n"
            "        String[] values = line.isEmpty() ? new String[0] : line.split(\",\");\n\n"
            "        Set<String> seen = new LinkedHashSet<>();\n"
            "        for (String v : values) seen.add(v);\n\n"
            "        StringJoiner sj = new StringJoiner(\", \");\n"
            "        for (String v : seen) sj.add(v);\n"
            "        System.out.println(sj);\n"
            "    }\n"
            "}\n"
        ),
        "explanation": (
            "new ArrayList<>(new LinkedHashSet<>(list)) is the one-line idiom; LinkedHashSet both "
            "deduplicates and preserves insertion order. A plain HashSet would lose order, and a "
            "TreeSet would sort — neither matches the requirement. The same idea applies when you "
            "deduplicate entitlement lists pulled from an API response."
        ),
        "time_complexity": "O(n) average",
        "space_complexity": "O(n)",
        "hints": [
            "new ArrayList<>(new LinkedHashSet<>(list)) is the one-liner.",
            "Why not HashSet or TreeSet? Order requirements decide.",
            "Stream API alternative: list.stream().distinct().collect(toList()).",
        ],
        "followups": [
            "How does stream().distinct() decide equality?",
            "When would you deduplicate by a key field rather than the whole object?",
            "How would you deduplicate test-case IDs in a suite before execution?",
        ],
    },
    {
        "id": "java-string-stats",
        "title": "Classify characters in a sentence",
        "category": "Core Java",
        "subcategory": "String manipulation",
        "type": "code",
        "difficulty": "medium",
        "problem": (
            "Read one line from stdin and print four lines with counts: vowels, consonants, "
            "digits and spaces. Letters only count as vowels/consonants (case-insensitive); "
            "other characters are ignored."
        ),
        "input_format": "A single line (1-1000 characters).",
        "output_format": "Exactly four lines: 'vowels: X', 'consonants: Y', 'digits: Z', 'spaces: W'.",
        "constraints": "Count exactly the space character for spaces; ignore punctuation and symbols.",
        "starter_code": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        String input = sc.nextLine();\n"
            "        // TODO: count vowels, consonants, digits, spaces\n"
            "    }\n"
            "}\n"
        ),
        "tests": [
            {"name": "classic", "stdin": "SDET 2026 @ Schwab\n", "expected": "vowels: 2\nconsonants: 8\ndigits: 4\nspaces: 3"},
            {"name": "empty", "stdin": "\n", "expected": "vowels: 0\nconsonants: 0\ndigits: 0\nspaces: 0"},
        ],
        "solution": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        String input = sc.nextLine();\n\n"
            "        Set<Character> vowels = Set.of('a','e','i','o','u');\n"
            "        int v = 0, c = 0, d = 0, s = 0;\n"
            "        for (char ch : input.toLowerCase().toCharArray()) {\n"
            "            if (ch >= 'a' && ch <= 'z') {\n"
            "                if (vowels.contains(ch)) v++;\n"
            "                else c++;\n"
            "            } else if (ch >= '0' && ch <= '9') d++;\n"
            "            else if (ch == ' ') s++;\n"
            "        }\n"
            "        System.out.println(\"vowels: \" + v);\n"
            "        System.out.println(\"consonants: \" + c);\n"
            "        System.out.println(\"digits: \" + d);\n"
            "        System.out.println(\"spaces: \" + s);\n"
            "    }\n"
            "}\n"
        ),
        "explanation": (
            "Normalise case once with toLowerCase(), then classify each character. Character.isLetter() "
            "and Character.isDigit() are the library-safe versions and handle Unicode; the range checks "
            "are the manual version interviewers sometimes ask for. The '@' symbol must be ignored, "
            "not counted as a consonant — that is the trap in this exercise."
        ),
        "time_complexity": "O(n)",
        "space_complexity": "O(1)",
        "hints": [
            "Lowercase the whole string first so 'A' and 'a' count the same.",
            "Non-alphanumeric characters other than space are ignored entirely.",
            "Character.isLetter/isDigit are Unicode-aware alternatives.",
        ],
        "followups": [
            "How would Character.isLetter() behave for non-ASCII scripts?",
            "How would you count unique vowels that appear, rather than total occurrences?",
            "Which boundary inputs would you add to an automated test for this?",
        ],
    },
    {
        "id": "java-sum-pairs",
        "title": "Find the first pair that sums to a target",
        "category": "Core Java",
        "subcategory": "HashMap",
        "type": "code",
        "difficulty": "medium",
        "problem": (
            "Read a target integer and then n integers. Print the FIRST pair of distinct "
            "positions (a, b) whose values sum to the target, formatted 'a + b'. "
            "The pair must come from different positions; print the earlier-seen value first. "
            "If no pair exists, print NONE. Solve it in one pass without sorting."
        ),
        "input_format": "Line 1: target. Line 2: n. Line 3: n space-separated integers.",
        "output_format": "'a + b' where a + b = target, or NONE.",
        "constraints": "2 <= n <= 10^5. Values fit in int.",
        "starter_code": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        int target = Integer.parseInt(sc.nextLine().trim());\n"
            "        int n = Integer.parseInt(sc.nextLine().trim());\n"
            "        String[] parts = sc.nextLine().trim().split(\"\\\\s+\");\n"
            "        int[] nums = new int[n];\n"
            "        for (int i = 0; i < n; i++) nums[i] = Integer.parseInt(parts[i]);\n"
            "        // TODO: first pair summing to target, one pass with a Map\n"
            "        System.out.println();\n"
            "    }\n"
            "}\n"
        ),
        "tests": [
            {"name": "basic", "stdin": "10\n5\n1 9 5 4 6\n", "expected": "1 + 9"},
            {"name": "no pair", "stdin": "100\n3\n1 2 3\n", "expected": "NONE"},
            {"name": "double of target needs two elements", "stdin": "8\n3\n4 4 1\n", "expected": "4 + 4"},
            {"name": "negative numbers", "stdin": "0\n4\n-3 3 -2 2\n", "expected": "-3 + 3"},
        ],
        "solution": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        int target = Integer.parseInt(sc.nextLine().trim());\n"
            "        int n = Integer.parseInt(sc.nextLine().trim());\n"
            "        String[] parts = sc.nextLine().trim().split(\"\\\\s+\");\n"
            "        int[] nums = new int[n];\n"
            "        for (int i = 0; i < n; i++) nums[i] = Integer.parseInt(parts[i]);\n\n"
            "        Map<Integer, Integer> seen = new HashMap<>(); // value -> first index\n"
            "        String result = \"NONE\";\n"
            "        for (int x : nums) {\n"
            "            int complement = target - x;\n"
            "            if (seen.containsKey(complement)) {\n"
            "                result = complement + \" + \" + x;\n"
            "                break;\n"
            "            }\n"
            "            seen.putIfAbsent(x, 1);\n"
            "        }\n"
            "        System.out.println(result);\n"
            "    }\n"
            "}\n"
        ),
        "explanation": (
            "For each value, compute target - x and check whether the complement was already seen. "
            "The map turns the O(n^2) double loop into O(n). Printing complement + \" + \" + x keeps "
            "the earlier-seen value first. This 'complement lookup' pattern appears constantly in "
            "interviews — two-sum is the gateway question for HashMap fluency."
        ),
        "time_complexity": "O(n) average",
        "space_complexity": "O(n)",
        "hints": [
            "For each x, look for (target - x) among values already seen.",
            "Store seen values in a Map/Set as you iterate — one pass only.",
            "Careful with output order: the value seen EARLIER prints first.",
        ],
        "followups": [
            "How would you return ALL pairs instead of the first?",
            "What if the array were sorted? (two pointers, O(1) space)",
            "How would you handle duplicates and index reporting?",
        ],
    },
    {
        "id": "java-anagram-check",
        "title": "Check whether two strings are anagrams",
        "category": "Core Java",
        "subcategory": "Collections",
        "type": "code",
        "difficulty": "easy",
        "problem": (
            "Read two lines from stdin and print ANAGRAM if they are anagrams of each other "
            "(same characters with the same counts, case-insensitive), otherwise NOT ANAGRAM."
        ),
        "input_format": "Two lines, one string each.",
        "output_format": "ANAGRAM or NOT ANAGRAM.",
        "constraints": "Case-insensitive. Ignore any non-alphanumeric characters.",
        "starter_code": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        String a = sc.nextLine();\n"
            "        String b = sc.nextLine();\n"
            "        // TODO: anagram check\n"
            "        System.out.println();\n"
            "    }\n"
            "}\n"
        ),
        "tests": [
            {"name": "classic anagram", "stdin": "listen\nsilent\n", "expected": "ANAGRAM"},
            {"name": "different lengths", "stdin": "hello\nworlds\n", "expected": "NOT ANAGRAM"},
            {"name": "case insensitive", "stdin": "Dormitory\ndirty room\n", "expected": "ANAGRAM"},
            {"name": "same letters different counts", "stdin": "aab\nabb\n", "expected": "NOT ANAGRAM"},
        ],
        "solution": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        String a = sc.nextLine();\n"
            "        String b = sc.nextLine();\n\n"
            "        Map<Integer, Integer> counts = new HashMap<>();\n"
            "        for (int c : a.toLowerCase().chars().filter(Character::isLetterOrDigit).toArray()) {\n"
            "            counts.merge(c, 1, Integer::sum);\n"
            "        }\n"
            "        for (int c : b.toLowerCase().chars().filter(Character::isLetterOrDigit).toArray()) {\n"
            "            Integer remaining = counts.merge(c, -1, Integer::sum);\n"
            "            if (remaining < 0) {\n"
            "                System.out.println(\"NOT ANAGRAM\");\n"
            "                return;\n"
            "            }\n"
            "        }\n"
            "        System.out.println(counts.values().stream().allMatch(v -> v == 0) ? \"ANAGRAM\" : \"NOT ANAGRAM\");\n"
            "    }\n"
            "}\n"
        ),
        "explanation": (
            "Count the first string into a frequency map, then DECREMENT using the second string. "
            "Any negative count or any leftover positive count means NOT ANAGRAM. "
            "The one-shot alternative is normalising both (lowercase, strip non-alphanumerics), "
            "converting to char[] and sorting, then comparing with Arrays.equals — O(n log n) but "
            "very hard to get wrong."
        ),
        "time_complexity": "O(n) with the counting map",
        "space_complexity": "O(k)",
        "hints": [
            "Normalise both strings first: lowercase and keep letters/digits only.",
            "Two approaches: sorted char arrays, or increment/decrement a frequency map.",
            "Length check after normalisation is a cheap early exit.",
        ],
        "followups": [
            "Group all anagrams in a list of words — which map key would you use?",
            "Sorted-char-array vs frequency-map: complexity trade-off?",
            "How would you test anagram logic in an automation framework?",
        ],
    },
    {
        "id": "java-fibonacci",
        "title": "Print the first n Fibonacci numbers",
        "category": "Core Java",
        "subcategory": "Logic and complexity",
        "type": "code",
        "difficulty": "easy",
        "problem": (
            "Read n and print the first n Fibonacci numbers starting from 0, "
            "space-separated on one line. Use iteration, not recursion."
        ),
        "input_format": "A single integer n.",
        "output_format": "n space-separated Fibonacci numbers: 0 1 1 2 3 5 ...",
        "constraints": "1 <= n <= 90 (use long; it overflows near n = 93).",
        "starter_code": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        int n = Integer.parseInt(sc.nextLine().trim());\n"
            "        // TODO: iterative Fibonacci\n"
            "        System.out.println();\n"
            "    }\n"
            "}\n"
        ),
        "tests": [
            {"name": "first ten", "stdin": "10\n", "expected": "0 1 1 2 3 5 8 13 21 34"},
            {"name": "single", "stdin": "1\n", "expected": "0"},
            {"name": "two", "stdin": "2\n", "expected": "0 1"},
        ],
        "solution": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        int n = Integer.parseInt(sc.nextLine().trim());\n\n"
            "        StringBuilder sb = new StringBuilder();\n"
            "        long a = 0, b = 1;\n"
            "        for (int i = 0; i < n; i++) {\n"
            "            if (i > 0) sb.append(' ');\n"
            "            sb.append(a);\n"
            "            long next = a + b;\n"
            "            a = b;\n"
            "            b = next;\n"
            "        }\n"
            "        System.out.println(sb);\n"
            "    }\n"
            "}\n"
        ),
        "explanation": (
            "Iterate with two rolling variables. Naive recursion is O(2^n) and recomputes the same "
            "values exponentially; memoisation fixes it at O(n) time / O(n) space, and the iterative "
            "loop is O(n) time / O(1) space. Interviewers use Fibonacci to check whether you can "
            "explain WHY recursion is slow before you fix it."
        ),
        "time_complexity": "O(n) iterative (naive recursion is O(2^n))",
        "space_complexity": "O(1) iterative",
        "hints": [
            "Roll two variables a and b forward — no array needed.",
            "Naive recursion explodes exponentially; explain why before coding.",
            "Use long: Fibonacci overflows int at n = 47.",
        ],
        "followups": [
            "Why is naive recursive Fibonacci O(2^n)?",
            "Memoisation vs iteration: which do you pick and why?",
            "Where does int overflow first appear in this sequence?",
        ],
    },
    {
        "id": "java-prime-check",
        "title": "Check whether a number is prime",
        "category": "Core Java",
        "subcategory": "Logic and complexity",
        "type": "code",
        "difficulty": "easy",
        "problem": (
            "Read a long integer and print PRIME if it is prime, otherwise NOT PRIME. "
            "Your check must run in O(sqrt(n))."
        ),
        "input_format": "A single integer n (0 <= n <= 10^15).",
        "output_format": "PRIME or NOT PRIME.",
        "constraints": "Use long. Handle 0, 1 and negative inputs as NOT PRIME.",
        "starter_code": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        long n = Long.parseLong(sc.nextLine().trim());\n"
            "        // TODO: primality check in O(sqrt(n))\n"
            "        System.out.println();\n"
            "    }\n"
            "}\n"
        ),
        "tests": [
            {"name": "small prime", "stdin": "7\n", "expected": "PRIME"},
            {"name": "small composite", "stdin": "9\n", "expected": "NOT PRIME"},
            {"name": "zero and one", "stdin": "1\n", "expected": "NOT PRIME"},
            {"name": "large prime", "stdin": "999999999999989\n", "expected": "PRIME"},
            {"name": "even large", "stdin": "1000000000000000\n", "expected": "NOT PRIME"},
        ],
        "solution": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        long n = Long.parseLong(sc.nextLine().trim());\n\n"
            "        boolean prime = n > 1;\n"
            "        if (prime) {\n"
            "            if (n % 2 == 0) {\n"
            "                prime = (n == 2);\n"
            "            } else {\n"
            "                for (long i = 3; i * i <= n; i += 2) {\n"
            "                    if (n % i == 0) { prime = false; break; }\n"
            "                }\n"
            "            }\n"
            "        }\n"
            "        System.out.println(prime ? \"PRIME\" : \"NOT PRIME\");\n"
            "    }\n"
            "}\n"
        ),
        "explanation": (
            "Divisors pair up: if d divides n then n/d divides n too, so one of the pair is <= sqrt(n). "
            "Checking i * i <= n avoids floating-point sqrt. Skipping even numbers after testing 2 "
            "halves the work. The 0/1/negative boundary is where candidates lose easy points."
        ),
        "time_complexity": "O(sqrt(n))",
        "space_complexity": "O(1)",
        "hints": [
            "You only need to test divisors up to sqrt(n).",
            "Use i * i <= n rather than Math.sqrt to avoid precision issues.",
            "0, 1 and negatives are NOT prime — handle them before the loop.",
        ],
        "followups": [
            "Why is checking up to n/2 wrong but checking up to sqrt(n) correct?",
            "i*i <= n vs i <= Math.sqrt(n): which is safer and why?",
            "How would you sieve all primes below a limit (Sieve of Eratosthenes)?",
        ],
    },
    {
        "id": "java-string-compression",
        "title": "Run-length compress a string",
        "category": "Core Java",
        "subcategory": "String manipulation",
        "type": "code",
        "difficulty": "medium",
        "problem": (
            "Read one line from stdin and print its run-length encoding: each run of the same "
            "character becomes 'char count' concatenated. Example: aaabbc becomes a3b2c1. "
            "A single character that never repeats still gets the count 1."
        ),
        "input_format": "A single line (1-1000 characters, no spaces).",
        "output_format": "The compressed string.",
        "constraints": "Do not use regular expressions for the core logic.",
        "starter_code": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        String input = sc.nextLine();\n"
            "        // TODO: run-length encoding\n"
            "        System.out.println();\n"
            "    }\n"
            "}\n"
        ),
        "tests": [
            {"name": "classic", "stdin": "aaabbc\n", "expected": "a3b2c1"},
            {"name": "single char", "stdin": "a\n", "expected": "a1"},
            {"name": "no repeats", "stdin": "abcdef\n", "expected": "a1b1c1d1e1f1"},
            {"name": "alternating", "stdin": "abab\n", "expected": "a1b1a1b1"},
        ],
        "solution": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        String input = sc.nextLine();\n\n"
            "        StringBuilder sb = new StringBuilder();\n"
            "        int i = 0;\n"
            "        while (i < input.length()) {\n"
            "            char c = input.charAt(i);\n"
            "            int j = i;\n"
            "            while (j < input.length() && input.charAt(j) == c) j++;\n"
            "            sb.append(c).append(j - i);\n"
            "            i = j;\n"
            "        }\n"
            "        System.out.println(sb);\n"
            "    }\n"
            "}\n"
        ),
        "explanation": (
            "Two pointers over the string: i marks the start of a run, j scans to the end of the run, "
            "and j - i is the run length. Building output with StringBuilder avoids the O(n^2) "
            "cost of repeated String concatenation. Interview variants include returning the "
            "original when the compressed form is longer."
        ),
        "time_complexity": "O(n)",
        "space_complexity": "O(n)",
        "hints": [
            "Scan runs with two pointers; append char then run length.",
            "Build the result in a StringBuilder, never with += in a loop.",
            "Follow-up variant: if compressed is longer than original, return the original.",
        ],
        "followups": [
            "How does String += differ from StringBuilder in complexity?",
            "How would you handle multi-character run values like 'a12'?",
            "What edge cases must an automation test cover here?",
        ],
    },
    {
        "id": "java-rotate-array",
        "title": "Rotate an array to the right by k steps",
        "category": "Core Java",
        "subcategory": "Array traversal",
        "type": "code",
        "difficulty": "medium",
        "problem": (
            "Read n, k and then n integers. Print the array rotated right by k, "
            "space-separated. k can be larger than n (wrap with modulo). "
            "Target: O(n) time. The rotation reversal trick avoids extra arrays."
        ),
        "input_format": "Line 1: n. Line 2: k. Line 3: n space-separated integers.",
        "output_format": "The rotated array, space-separated.",
        "constraints": "1 <= n <= 10^5. 0 <= k <= 10^9.",
        "starter_code": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        int n = Integer.parseInt(sc.nextLine().trim());\n"
            "        int k = Integer.parseInt(sc.nextLine().trim());\n"
            "        String[] parts = sc.nextLine().trim().split(\"\\\\s+\");\n"
            "        int[] nums = new int[n];\n"
            "        for (int i = 0; i < n; i++) nums[i] = Integer.parseInt(parts[i]);\n"
            "        // TODO: rotate right by k (k may exceed n)\n"
            "    }\n"
            "}\n"
        ),
        "tests": [
            {"name": "basic rotate", "stdin": "7\n3\n1 2 3 4 5 6 7\n", "expected": "5 6 7 1 2 3 4"},
            {"name": "k equal to n", "stdin": "3\n3\n1 2 3\n", "expected": "1 2 3"},
            {"name": "k larger than n", "stdin": "4\n6\n1 2 3 4\n", "expected": "3 4 1 2"},
            {"name": "k zero", "stdin": "3\n0\n9 8 7\n", "expected": "9 8 7"},
        ],
        "solution": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    static void reverse(int[] a, int from, int to) {\n"
            "        while (from < to) {\n"
            "            int tmp = a[from]; a[from] = a[to]; a[to] = tmp;\n"
            "            from++; to--;\n"
            "        }\n"
            "    }\n\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        int n = Integer.parseInt(sc.nextLine().trim());\n"
            "        int k = Integer.parseInt(sc.nextLine().trim()) % n;\n"
            "        String[] parts = sc.nextLine().trim().split(\"\\\\s+\");\n"
            "        int[] nums = new int[n];\n"
            "        for (int i = 0; i < n; i++) nums[i] = Integer.parseInt(parts[i]);\n\n"
            "        reverse(nums, 0, n - 1);        // reverse whole array\n"
            "        reverse(nums, 0, k - 1);       // reverse first k\n"
            "        reverse(nums, k, n - 1);       // reverse remainder\n\n"
            "        StringJoiner sj = new StringJoiner(\" \");\n"
            "        for (int x : nums) sj.add(String.valueOf(x));\n"
            "        System.out.println(sj);\n"
            "    }\n"
            "}\n"
        ),
        "explanation": (
            "k %= n first because rotating by n returns the array to itself. The three-reversal trick "
            "rotates in place: reverse everything, then reverse the first k, then the rest. "
            "The straightforward alternative — building a new array with result[(i + k) % n] = a[i] — "
            "is also O(n) and perfectly acceptable; say both out loud in the interview."
        ),
        "time_complexity": "O(n)",
        "space_complexity": "O(1) extra with the reversal trick",
        "hints": [
            "Normalise k with modulo before anything else.",
            "In-place trick: reverse all, then reverse first k, then the rest.",
            "Simple alternative: result[(i + k) % n] = a[i] in a new array.",
        ],
        "followups": [
            "Left rotation instead of right — what changes?",
            "Why does the reversal trick work? Can you prove it in a sentence?",
            "How would you rotate a List<Integer> with the same complexity?",
        ],
    },
]
