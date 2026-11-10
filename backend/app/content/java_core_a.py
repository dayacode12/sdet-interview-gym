"""Java coding questions, core part A (strings, hashing, arrays). Runnable via stdin/stdout."""
from __future__ import annotations

JAVA_CORE_PART_A = [
    {
        "id": "java-reverse-string",
        "title": "Reverse a string without using reverse()",
        "category": "Core Java",
        "subcategory": "String manipulation",
        "type": "code",
        "difficulty": "easy",
        "problem": (
            "Read one line from stdin and print it reversed. "
            "You must NOT use StringBuilder.reverse(), StringBuffer.reverse(), "
            "Collections.reverse() or any other library reverse helper. "
            "Build the reversed string yourself."
        ),
        "input_format": "A single line containing a word (1-1000 characters).",
        "output_format": "The reversed string.",
        "constraints": "1 <= length <= 1000. Line may contain letters, digits and symbols.",
        "starter_code": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        String input = sc.nextLine();\n"
            "        // TODO: reverse input without using reverse()\n"
            "        System.out.println();\n"
            "    }\n"
            "}\n"
        ),
        "tests": [
            {"name": "basic word", "stdin": "automation\n", "expected": "noitamotua"},
            {"name": "palindrome input", "stdin": "racecar\n", "expected": "racecar"},
            {"name": "single char", "stdin": "x\n", "expected": "x"},
            {"name": "mixed symbols", "stdin": "Ab3!z\n", "expected": "z!3bA"},
        ],
        "solution": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        String input = sc.nextLine();\n"
            "        char[] chars = input.toCharArray();\n"
            "        StringBuilder sb = new StringBuilder();\n"
            "        for (int i = chars.length - 1; i >= 0; i--) {\n"
            "            sb.append(chars[i]);\n"
            "        }\n"
            "        System.out.println(sb.toString());\n"
            "    }\n"
            "}\n"
        ),
        "explanation": (
            "Walk the char array from the last index to the first and append each character. "
            "This is O(n) time and O(n) space for the output. "
            "Alternative: swap characters in place using two pointers (i from start, j from end) "
            "inside a char[], which avoids building a second string."
        ),
        "time_complexity": "O(n)",
        "space_complexity": "O(n) for the result (or O(1) extra with in-place char[] swap)",
        "hints": [
            "A String is immutable; you need a char[] or StringBuilder to build the result.",
            "Two-pointer swap inside toCharArray() avoids extra allocations.",
            "Edge cases: single character, and strings with spaces or symbols.",
        ],
        "followups": [
            "How would you reverse in-place without extra space? (char[] swap)",
            "How would you reverse only the words in a sentence, keeping word order?",
            "Why is String concatenation in a loop (s += c) slower than StringBuilder?",
            "How would you unit-test this method? What inputs would you include?",
        ],
    },
    {
        "id": "java-palindrome-check",
        "title": "Check whether a string is a palindrome",
        "category": "Core Java",
        "subcategory": "String manipulation",
        "type": "code",
        "difficulty": "easy",
        "problem": (
            "Read one line from stdin and decide whether it is a palindrome, "
            "ignoring case and any non-alphanumeric characters. "
            "Print PALINDROME or NOT A PALINDROME."
        ),
        "input_format": "A single line (1-1000 characters), may contain spaces, punctuation.",
        "output_format": "PALINDROME if it reads the same forwards and backwards after normalisation, otherwise NOT A PALINDROME.",
        "constraints": "Ignore case. Ignore every character that is not a letter or digit.",
        "starter_code": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        String input = sc.nextLine();\n"
            "        // TODO: normalise then check palindrome\n"
            "        System.out.println();\n"
            "    }\n"
            "}\n"
        ),
        "tests": [
            {"name": "simple palindrome", "stdin": "RaceCar\n", "expected": "PALINDROME"},
            {"name": "phrase with punctuation", "stdin": "A man, a plan, a canal: Panama\n", "expected": "PALINDROME"},
            {"name": "not a palindrome", "stdin": "automation\n", "expected": "NOT A PALINDROME"},
            {"name": "digits palindrome", "stdin": "12 21\n", "expected": "PALINDROME"},
        ],
        "solution": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        String input = sc.nextLine();\n\n"
            "        String normalized = input.toLowerCase().replaceAll(\"[^a-z0-9]\", \"\");\n"
            "        int i = 0, j = normalized.length() - 1;\n"
            "        boolean palindrome = true;\n"
            "        while (i < j) {\n"
            "            if (normalized.charAt(i) != normalized.charAt(j)) {\n"
            "                palindrome = false;\n"
            "                break;\n"
            "            }\n"
            "            i++;\n"
            "            j--;\n"
            "        }\n"
            "        System.out.println(palindrome ? \"PALINDROME\" : \"NOT A PALINDROME\");\n"
            "    }\n"
            "}\n"
        ),
        "explanation": (
            "Normalise first (lowercase + strip non-alphanumerics), then compare characters from both "
            "ends with two pointers. Return on the first mismatch. The normalisation step is what "
            "interviewers usually probe: forgetting case or punctuation is the classic mistake."
        ),
        "time_complexity": "O(n)",
        "space_complexity": "O(n) for the normalised copy (O(1) if you skip non-alphanumerics on the fly)",
        "hints": [
            "Normalise with toLowerCase() and a character filter before comparing.",
            "Two pointers from both ends beat building a reversed copy.",
            "You can do it in O(1) extra space by skipping invalid characters inside the loop.",
        ],
        "followups": [
            "Can you solve it without creating a normalised copy? (skip invalid chars in the loop)",
            "What is the time complexity if you compare against new StringBuilder(s).reverse()?",
            "Which test inputs would you use in an automation suite for this method?",
        ],
    },
    {
        "id": "java-duplicate-characters",
        "title": "Find duplicate characters in a string",
        "category": "Core Java",
        "subcategory": "HashMap",
        "type": "code",
        "difficulty": "easy",
        "problem": (
            "Read one line from stdin and print every character that occurs more than once, "
            "one per line in first-appearance order, formatted exactly as 'c = count'. "
            "If no character repeats, print NONE."
        ),
        "input_format": "A single line containing a word (1-1000 characters).",
        "output_format": "Lines of 'c = count' for each repeated character, or NONE.",
        "constraints": "Case-sensitive: 'A' and 'a' are different characters.",
        "starter_code": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        String input = sc.nextLine();\n"
            "        // TODO: find duplicate characters using a Map\n"
            "    }\n"
            "}\n"
        ),
        "tests": [
            {"name": "classic example", "stdin": "automation\n", "expected": "a = 2\nt = 2\no = 2"},
            {"name": "no duplicates", "stdin": "abcdef\n", "expected": "NONE"},
            {"name": "case sensitivity", "stdin": "AaA\n", "expected": "A = 2"},
        ],
        "solution": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        String input = sc.nextLine();\n\n"
            "        Map<Character, Integer> counts = new LinkedHashMap<>();\n"
            "        for (char c : input.toCharArray()) {\n"
            "            counts.merge(c, 1, Integer::sum);\n"
            "        }\n"
            "        boolean found = false;\n"
            "        for (Map.Entry<Character, Integer> e : counts.entrySet()) {\n"
            "            if (e.getValue() > 1) {\n"
            "                System.out.println(e.getKey() + \" = \" + e.getValue());\n"
            "                found = true;\n"
            "            }\n"
            "        }\n"
            "        if (!found) {\n"
            "            System.out.println(\"NONE\");\n"
            "        }\n"
            "    }\n"
            "}\n"
        ),
        "explanation": (
            "One pass to build a frequency map, one pass to report. LinkedHashMap preserves "
            "first-appearance order, which is why it is preferred over HashMap when output order "
            "matters. merge() is cleaner than containsKey + put."
        ),
        "time_complexity": "O(n)",
        "space_complexity": "O(k) where k is the number of distinct characters",
        "hints": [
            "Which Map implementation keeps insertion order?",
            "counts.merge(c, 1, Integer::sum) is the idiomatic way to count.",
            "Handle the no-duplicates case explicitly (NONE).",
        ],
        "followups": [
            "Why LinkedHashMap instead of HashMap here?",
            "What is the difference between HashMap, LinkedHashMap and TreeMap?",
            "How would this change for a Unicode string where one code point spans two chars?",
            "How would you unit test this, including null and empty input?",
        ],
    },
    {
        "id": "java-first-non-repeating",
        "title": "Find the first non-repeating character",
        "category": "Core Java",
        "subcategory": "Collections",
        "type": "code",
        "difficulty": "easy",
        "problem": (
            "Read one line from stdin and print the first character that occurs exactly once. "
            "If every character repeats, print NONE."
        ),
        "input_format": "A single line (1-1000 characters).",
        "output_format": "The first non-repeating character, or NONE.",
        "constraints": "Case-sensitive.",
        "starter_code": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        String input = sc.nextLine();\n"
            "        // TODO: first non-repeating character\n"
            "        System.out.println();\n"
            "    }\n"
            "}\n"
        ),
        "tests": [
            {"name": "classic", "stdin": "swiss\n", "expected": "w"},
            {"name": "first char unique", "stdin": "aabbcd\n", "expected": "c"},
            {"name": "all repeating", "stdin": "aabb\n", "expected": "NONE"},
            {"name": "single char", "stdin": "z\n", "expected": "z"},
        ],
        "solution": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        String input = sc.nextLine();\n\n"
            "        Map<Character, Integer> counts = new LinkedHashMap<>();\n"
            "        for (char c : input.toCharArray()) {\n"
            "            counts.merge(c, 1, Integer::sum);\n"
            "        }\n"
            "        Character result = null;\n"
            "        for (Map.Entry<Character, Integer> e : counts.entrySet()) {\n"
            "            if (e.getValue() == 1) {\n"
            "                result = e.getKey();\n"
            "                break;\n"
            "            }\n"
            "        }\n"
            "        System.out.println(result == null ? \"NONE\" : String.valueOf(result));\n"
            "    }\n"
            "}\n"
        ),
        "explanation": (
            "Count frequencies first, then iterate in insertion order and return the first entry with "
            "count 1. A single LinkedHashMap gives both requirements. The naive double loop "
            "(for each char, scan the rest of the string) is O(n^2) and is what interviewers want you to avoid."
        ),
        "time_complexity": "O(n)",
        "space_complexity": "O(k)",
        "hints": [
            "Two passes: count, then scan in insertion order.",
            "LinkedHashMap keeps insertion order so the second pass finds the FIRST unique char.",
            "Do not compare indexOf(c) == lastIndexOf(c) for large inputs — that is O(n^2).",
        ],
        "followups": [
            "How would you return the index instead of the character?",
            "What if the input can contain Unicode surrogate pairs?",
            "How does indexOf/lastIndexOf change the complexity?",
        ],
    },
    {
        "id": "java-second-largest",
        "title": "Find the second-largest number in an array",
        "category": "Core Java",
        "subcategory": "Array traversal",
        "type": "code",
        "difficulty": "easy",
        "problem": (
            "Read n and then n integers. Print the second-largest DISTINCT value. "
            "If it does not exist (fewer than two distinct values), print NONE."
        ),
        "input_format": "Line 1: n. Line 2: n space-separated integers.",
        "output_format": "The second-largest distinct integer, or NONE.",
        "constraints": "1 <= n <= 10^5. Values fit in int.",
        "starter_code": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        int n = Integer.parseInt(sc.nextLine().trim());\n"
            "        String[] parts = sc.nextLine().trim().split(\"\\\\s+\");\n"
            "        int[] nums = new int[n];\n"
            "        for (int i = 0; i < n; i++) nums[i] = Integer.parseInt(parts[i]);\n"
            "        // TODO: second-largest distinct value in one pass\n"
            "        System.out.println();\n"
            "    }\n"
            "}\n"
        ),
        "tests": [
            {"name": "basic", "stdin": "5\n10 20 4 45 99\n", "expected": "45"},
            {"name": "duplicates of max", "stdin": "5\n99 99 20 4 45\n", "expected": "45"},
            {"name": "all same", "stdin": "3\n7 7 7\n", "expected": "NONE"},
            {"name": "negative numbers", "stdin": "4\n-5 -1 -9 -3\n", "expected": "-3"},
        ],
        "solution": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        int n = Integer.parseInt(sc.nextLine().trim());\n"
            "        String[] parts = sc.nextLine().trim().split(\"\\\\s+\");\n"
            "        int[] nums = new int[n];\n"
            "        for (int i = 0; i < n; i++) nums[i] = Integer.parseInt(parts[i]);\n\n"
            "        Integer largest = null, second = null;\n"
            "        for (int x : nums) {\n"
            "            if (largest == null || x > largest) {\n"
            "                second = largest;\n"
            "                largest = x;\n"
            "            } else if (x != largest && (second == null || x > second)) {\n"
            "                second = x;\n"
            "            }\n"
            "        }\n"
            "        System.out.println(second == null ? \"NONE\" : String.valueOf(second));\n"
            "    }\n"
            "}\n"
        ),
        "explanation": (
            "Track two variables in a single pass: when a new maximum appears, the old maximum becomes "
            "the second-largest. The x != largest check enforces DISTINCT values, which is where most "
            "candidates slip when the array contains repeated maxima. Sorting is O(n log n); the single "
            "pass is O(n) and needs no extra memory."
        ),
        "time_complexity": "O(n)",
        "space_complexity": "O(1) extra",
        "hints": [
            "Track largest and second in one pass instead of sorting.",
            "Watch the duplicate-maximum case: [99, 99, 45] must give 45, not 99.",
            "Use Integer (nullable) or a sentinel so 'not found' is unambiguous.",
        ],
        "followups": [
            "What if you needed the k-th largest? (heap / quickselect)",
            "How would you handle Integer.MIN_VALUE as valid input?",
            "What is the complexity of sorting-based solutions, and when are they acceptable?",
        ],
    },
    {
        "id": "java-duplicate-elements",
        "title": "Find duplicate elements in an array",
        "category": "Core Java",
        "subcategory": "HashSet",
        "type": "code",
        "difficulty": "easy",
        "problem": (
            "Read n and then n integers. Print every value that appears more than once, "
            "each value once, in the order of its first appearance, space-separated on one line. "
            "If there are no duplicates, print NONE."
        ),
        "input_format": "Line 1: n. Line 2: n space-separated integers.",
        "output_format": "Space-separated duplicates on one line, or NONE.",
        "constraints": "1 <= n <= 10^5.",
        "starter_code": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        int n = Integer.parseInt(sc.nextLine().trim());\n"
            "        String[] parts = sc.nextLine().trim().split(\"\\\\s+\");\n"
            "        int[] nums = new int[n];\n"
            "        for (int i = 0; i < n; i++) nums[i] = Integer.parseInt(parts[i]);\n"
            "        // TODO: print duplicates using a HashSet\n"
            "    }\n"
            "}\n"
        ),
        "tests": [
            {"name": "basic duplicates", "stdin": "8\n1 2 3 2 4 1 5 1\n", "expected": "1 2"},
            {"name": "no duplicates", "stdin": "4\n1 2 3 4\n", "expected": "NONE"},
            {"name": "all same", "stdin": "3\n9 9 9\n", "expected": "9"},
        ],
        "solution": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        int n = Integer.parseInt(sc.nextLine().trim());\n"
            "        String[] parts = sc.nextLine().trim().split(\"\\\\s+\");\n"
            "        int[] nums = new int[n];\n"
            "        for (int i = 0; i < n; i++) nums[i] = Integer.parseInt(parts[i]);\n\n"
            "        Set<Integer> seen = new HashSet<>();\n"
            "        Set<Integer> duplicates = new LinkedHashSet<>();\n"
            "        for (int x : nums) {\n"
            "            if (!seen.add(x)) {\n"
            "                duplicates.add(x);\n"
            "            }\n"
            "        }\n"
            "        if (duplicates.isEmpty()) {\n"
            "            System.out.println(\"NONE\");\n"
            "        } else {\n"
            "            StringJoiner sj = new StringJoiner(\" \");\n"
            "            for (int d : duplicates) sj.add(String.valueOf(d));\n"
            "            System.out.println(sj);\n"
            "        }\n"
            "    }\n"
            "}\n"
        ),
        "explanation": (
            "seen.add(x) returns false the moment a value repeats — that single boolean drives the "
            "whole algorithm. LinkedHashSet for the duplicates keeps first-appearance order and "
            "prevents printing the same duplicate twice (the [1,2,3,2,4,1,5,1] case). "
            "This is the same pattern you use in reconciliation testing to detect duplicate identity records."
        ),
        "time_complexity": "O(n) average",
        "space_complexity": "O(n)",
        "hints": [
            "Set.add() returns false when the element already exists.",
            "Use LinkedHashSet for duplicates so order is preserved and repeats print once.",
            "In IAM terms: this is how you flag duplicate user records during reconciliation.",
        ],
        "followups": [
            "How would you count occurrences instead of just flagging them?",
            "What happens to HashSet performance when hashCodes collide?",
            "How would you find duplicates in a stream too large for memory?",
        ],
    },
    {
        "id": "java-missing-number",
        "title": "Find the missing number in 1..n",
        "category": "Core Java",
        "subcategory": "Logic and complexity",
        "type": "code",
        "difficulty": "easy",
        "problem": (
            "You are given n-1 distinct integers from the range 1..n with exactly one number missing. "
            "Read n, then the n-1 numbers, and print the missing number. "
            "Solve it without sorting."
        ),
        "input_format": "Line 1: n. Line 2: n-1 space-separated distinct integers from 1..n.",
        "output_format": "The missing integer.",
        "constraints": "2 <= n <= 10^6. Watch for overflow in the sum approach.",
        "starter_code": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        int n = Integer.parseInt(sc.nextLine().trim());\n"
            "        String[] parts = sc.nextLine().trim().split(\"\\\\s+\");\n"
            "        // TODO: find the missing number in O(n)\n"
            "        System.out.println();\n"
            "    }\n"
            "}\n"
        ),
        "tests": [
            {"name": "middle missing", "stdin": "5\n1 2 4 5\n", "expected": "3"},
            {"name": "first missing", "stdin": "4\n2 3 4\n", "expected": "1"},
            {"name": "last missing", "stdin": "4\n1 2 3\n", "expected": "4"},
            {"name": "large n", "stdin": "1000000\n" + " ".join(str(i) for i in range(1, 500000)) + " " + " ".join(str(i) for i in range(500001, 1000001)) + "\n", "expected": "500000"},
        ],
        "solution": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        long n = Long.parseLong(sc.nextLine().trim());\n"
            "        String[] parts = sc.nextLine().trim().split(\"\\\\s+\");\n\n"
            "        long expectedSum = n * (n + 1) / 2;\n"
            "        long actualSum = 0;\n"
            "        for (String p : parts) {\n"
            "            actualSum += Long.parseLong(p);\n"
            "        }\n"
            "        System.out.println(expectedSum - actualSum);\n"
            "    }\n"
            "}\n"
        ),
        "explanation": (
            "Gauss: the sum of 1..n is n(n+1)/2. Subtract the actual sum and the difference is the "
            "missing number — O(n) time, O(1) space, no sorting. XOR works equally well "
            "(xor all indexes with all values) and avoids overflow entirely. Using long guards the sum "
            "against overflow for large n."
        ),
        "time_complexity": "O(n)",
        "space_complexity": "O(1)",
        "hints": [
            "Sum formula: n(n+1)/2 minus the actual sum.",
            "The XOR trick avoids overflow: a^a = 0, so pairs cancel.",
            "This is the reconciliation-count idea: expected total vs actual total.",
        ],
        "followups": [
            "What if two numbers are missing?",
            "Sum vs XOR: which is safer against overflow, and why?",
            "How does this relate to validating source vs target counts in a reconciliation job?",
        ],
    },
    {
        "id": "java-char-frequency",
        "title": "Count character frequency in a string",
        "category": "Core Java",
        "subcategory": "HashMap",
        "type": "code",
        "difficulty": "easy",
        "problem": (
            "Read one line from stdin and print the frequency of every character "
            "in first-appearance order, one per line, formatted 'c: count'."
        ),
        "input_format": "A single line (1-1000 characters).",
        "output_format": "One line per distinct character: 'c: count'.",
        "constraints": "Case-sensitive. Include spaces if present.",
        "starter_code": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        String input = sc.nextLine();\n"
            "        // TODO: frequency of every character, first-appearance order\n"
            "    }\n"
            "}\n"
        ),
        "tests": [
            {"name": "classic", "stdin": "automation\n", "expected": "a: 2\nu: 1\nt: 2\no: 2\nm: 1\ni: 1\nn: 1"},
            {"name": "with space", "stdin": "ab a\n", "expected": "a: 2\nb: 1\n : 1"},
        ],
        "solution": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        String input = sc.nextLine();\n\n"
            "        Map<Character, Integer> freq = new LinkedHashMap<>();\n"
            "        for (char c : input.toCharArray()) {\n"
            "            freq.merge(c, 1, Integer::sum);\n"
            "        }\n"
            "        for (Map.Entry<Character, Integer> e : freq.entrySet()) {\n"
            "            System.out.println(e.getKey() + \": \" + e.getValue());\n"
            "        }\n"
            "    }\n"
            "}\n"
        ),
        "explanation": (
            "A frequency map is the single most reused pattern in interview Java: duplicates, "
            "anagrams, first-unique, word counts and grouping all start here. "
            "getOrDefault or merge both work; merge is the modern idiom."
        ),
        "time_complexity": "O(n)",
        "space_complexity": "O(k)",
        "hints": [
            "freq.getOrDefault(c, 0) + 1 or freq.merge(c, 1, Integer::sum).",
            "LinkedHashMap preserves first-appearance order for output.",
            "For fixed alphabets you could use int[26] instead of a Map.",
        ],
        "followups": [
            "int[26] vs HashMap — when is the array better?",
            "How would you print frequencies sorted by count? (sort entries by value)",
            "How would you adapt this to count words instead of characters?",
        ],
    },
    {
        "id": "java-word-frequency",
        "title": "Count word frequency in a sentence",
        "category": "Core Java",
        "subcategory": "HashMap",
        "type": "code",
        "difficulty": "medium",
        "problem": (
            "Read one line from stdin and print each distinct word with its count, "
            "sorted by count descending, then alphabetically for ties, one per line as 'word = count'. "
            "Split on whitespace and treat words case-insensitively (normalise to lowercase)."
        ),
        "input_format": "A single line sentence.",
        "output_format": "Lines of 'word = count', sorted by count desc then word asc.",
        "constraints": "Words contain letters/digits/punctuation attached to the word.",
        "starter_code": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        String input = sc.nextLine();\n"
            "        // TODO: word frequency, sorted by count desc then word asc\n"
            "    }\n"
            "}\n"
        ),
        "tests": [
            {"name": "classic sentence", "stdin": "the quick brown fox jumps over the lazy dog the fox\n", "expected": "the = 3\nfox = 2\nbrown = 1\ndog = 1\njumps = 1\nlazy = 1\nover = 1\nquick = 1"},
            {"name": "case insensitive", "stdin": "Java java JAVA\n", "expected": "java = 3"},
        ],
        "solution": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        String input = sc.nextLine().toLowerCase();\n\n"
            "        Map<String, Integer> freq = new HashMap<>();\n"
            "        for (String w : input.trim().split(\"\\\\s+\")) {\n"
            "            if (!w.isEmpty()) freq.merge(w, 1, Integer::sum);\n"
            "        }\n\n"
            "        List<Map.Entry<String, Integer>> entries = new ArrayList<>(freq.entrySet());\n"
            "        entries.sort(\n"
            "            Map.Entry.<String, Integer>comparingByValue(Comparator.reverseOrder())\n"
            "                .thenComparing(Map.Entry.comparingByKey())\n"
            "        );\n"
            "        for (Map.Entry<String, Integer> e : entries) {\n"
            "            System.out.println(e.getKey() + \" = \" + e.getValue());\n"
            "        }\n"
            "    }\n"
            "}\n"
        ),
        "explanation": (
            "Count with HashMap (order irrelevant while counting), copy the entries into a List and "
            "sort with a composed Comparator: value descending, then key ascending. "
            "Map.Entry.comparingByValue(Comparator.reverseOrder()).thenComparing(comparingByKey()) "
            "is the idiom interviewers expect you to know."
        ),
        "time_complexity": "O(n log n) for the sort over distinct words",
        "space_complexity": "O(k)",
        "hints": [
            "Count with HashMap, then sort the entrySet as a List.",
            "Compose comparators: comparingByValue(reversed).thenComparing(comparingByKey()).",
            "Normalise to lowercase before counting.",
        ],
        "followups": [
            "How would you get the top-K words only? (sort all vs heap of size K)",
            "Stream API version: Collectors.groupingBy + counting?",
            "What is the complexity difference between full sort and a K-sized priority queue?",
        ],
    },
]
